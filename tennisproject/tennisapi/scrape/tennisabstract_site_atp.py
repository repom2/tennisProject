# import beautifulsoup4
import logging
from datetime import datetime
import time
from bs4 import BeautifulSoup

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)


def tennisabstract_scrape_atp():
    try:
        # Specify the URL where the Selenium Hub is running
        hub_url = (
            "http://selenium-hub:4444/wd/hub"
        )  # Use hostname/IP of your selenium_hub service if running remotely

        # Define options for the Chrome browser
        chrome_options = ChromeOptions()
        chrome_options.add_argument(
            "--headless"
        )  # Run in headless mode (no browser UI)

        # Instantiate a remote WebDriver object connecting to the Selenium Hub
        driver = webdriver.Remote(command_executor=hub_url, options=chrome_options)

        # Target URL
        url = "https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p=JiriLehecka"
        driver.get(url)

        # Get the HTML content
        html = driver.page_source

        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(html, "html.parser")
        # logging.info(soup)

        tables = soup.find_all("table")  # , class_='tennis-match__match-link')

        # Iterate over each <a> tag and perform an action, like printing the href attribute
        # i = 0
        # for table in tables:
        #   logging.info(table)
        #  logging.info("---------------Table: " + str(i))
        #  i += 1
        # break

        # clean all html tags
        player_info = tables[5].get_text()
        logging.info(player_info)
        logging.info("---------------Table: " + str(5))
        soup = tables[4]

        # Find the player's bio section and extract player information
        player_bio_section = soup.find(id="biog")
        name_country = (
            player_bio_section.find("b").get_text()
            if player_bio_section.find("b")
            else None
        )
        date_of_birth = (
            player_bio_section.find(text="Date of birth: ").next_sibling
            if player_bio_section.find(text="Date of birth: ")
            else None
        )
        play_hand = (
            player_bio_section.find(text="Plays: ").next_sibling
            if player_bio_section.find(text="Plays: ")
            else None
        )
        current_rank = (
            player_bio_section.find(text="Current rank: ").find_next("b").get_text()
            if player_bio_section.find(text="Current rank: ")
            else None
        )
        peak_rank = (
            player_bio_section.find(text="Peak rank: ").find_next("b").get_text()
            if player_bio_section.find(text="Peak rank: ")
            else None
        )

        print(f"Name and Country: {name_country}")
        for tr in soup.find_all("tr"):
            td = tr.find("td")
            if td:
                text_content = td.text
                # Checking and splitting based on known labels
                if "Date of birth" in text_content:
                    date_of_birth = text_content.split(": ")[1].strip()
                if "Plays" in text_content:
                    play_hand = text_content.split(": ")[1].strip()
                elif "Peak rank" in text_content:
                    peak_rank = text_content

        # change the date of birth to age
        date_format = "%d-%b-%Y"
        birthdate = datetime.strptime(date_of_birth, date_format)
        current_date = datetime.now()
        age = (
            current_date.year
            - birthdate.year
            - (
                (current_date.month, current_date.day)
                < (birthdate.month, birthdate.day)
            )
        )

        # make dictionary of this data
        player_info = {
            "name_country": name_country,
            "current_rank": current_rank,
            "age": age,
            "play_hand": play_hand,
            "peak_rank": peak_rank,
        }
        logging.info(player_info)

        # Now let's get the statistics from the 'wonloss' section
        stats_table = soup.find(id="wonloss")

        # Extracting the header
        headers = []
        for header in stats_table.find_all("th"):
            headers.append(header.get_text().strip())

        # Extracting the stats for each row
        stats_data = []
        for row in stats_table.find_all("tr")[1:]:  # Skipping the headers
            stats = []
            for cell in row.find_all(["td", "th"]):
                stats.append(cell.get_text().strip())
            stats_data.append(stats)

        # Displaying the results
        print("\nStatistics:")
        print(headers)
        for stat in stats_data:
            print(stat)

        # MATCHES TABLE
        try:
            matches_table = tables[7].find("table", {"id": "matches"})
            #logging.info(matches_table)
            # Extract the headers
            headers = [header.text.strip() for header in matches_table.find_all("th")]
        except Exception as e:
            logging.error(f"Error extracting matches table: {e}")
            driver.quit()

        # Initialize a list to store all match data
        all_matches_data = []

        # Extract the match details from each row in the matches table body
        for row in matches_table.tbody.find_all("tr"):
            # Initialize a dictionary to store data for the current match
            match_data = {}

            # Extract all cells in the row
            cells = row.find_all("td")

            # Assign each cell's text to the dictionary using the header as the key
            for header, cell in zip(headers, cells):
                match_data[header] = cell.get_text().strip()
                if header == "Rk":
                    continue

            # Append the match data dictionary to the list of all match data
            all_matches_data.append(match_data)

        # create a dataframe from the dictionary list
        df = pd.DataFrame(all_matches_data[:15])
        # Convert the DataFrame to a Markdown table
        md_table = df.to_markdown(index=False)
        print(md_table)
        # return the dataframe
    except Exception as e:
        logging.error(e)
    # Close the browser session when done
    driver.quit()
