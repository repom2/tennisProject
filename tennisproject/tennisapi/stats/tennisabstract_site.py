# import beautifulsoup4
import logging
from datetime import datetime

from bs4 import BeautifulSoup

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

logging = logging.getLogger(__name__)


def tennisabstract_scrape(row, home, surface):
    try:
        if home == "home":
            index_columns = [
                "home_spw",
                "home_rpw",
                "home_dr",
                "home_matches",
                "home_peak_rank",
                "home_current_rank",
                "home_plays",
                "home_player_info",
                "home_md_table",
                "home_spw_clay",
                "home_rpw_clay",
                "home_dr_clay",
                "home_matches_clay",
                "home_spw_grass",
                "home_rpw_grass",
                "home_dr_grass",
                "home_matches_grass",
            ]
            player_name = row["atp_home_fullname"]
            # if row['home_peak_rank']:
            #   return row[index_columns]
        else:
            index_columns = [
                "away_spw",
                "away_rpw",
                "away_dr",
                "away_matches",
                "away_peak_rank",
                "away_current_rank",
                "away_plays",
                "away_player_info",
                "away_md_table",
                "away_spw_clay",
                "away_rpw_clay",
                "away_dr_clay",
                "away_matches_clay",
                "away_spw_grass",
                "away_rpw_grass",
                "away_dr_grass",
                "away_matches_grass",
            ]
            player_name = row["atp_away_fullname"]
            # if row['away_peak_rank']:
            #   return row[index_columns]
        # strip the player name
        player_name = player_name.strip().replace(" ", "")
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
        url = (
            "https://www.tennisabstract.com/cgi-bin/wplayer-classic.cgi?p="
            + player_name
        )

        if surface == "grass":
            url += "&f=ACareerqqB2"
        driver.get(url)

        # Get the HTML content
        html = driver.page_source

        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table")  # , class_='tennis-match__match-link')

        # clean all html tags
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
                elif "Plays" in text_content:
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

        spw, rpw, dr, matches = None, None, None, None
        # Displaying the results
        print("\nStatistics:")
        for stat in stats_data:
            if stat[0] == "Hard":
                matches = stat[1]
                try:
                    rpw = float(stat[7].replace("%", ""))
                    dr = float(stat[8])
                    spw = round((100 - rpw / dr) * 0.01, 3)
                    rpw = round(rpw * 0.01, 3)
                except ValueError:
                    spw = None
                    rpw = None
                    dr = None
                    matches = None

                print([spw, rpw, dr, matches], "Hard")
            if stat[0] == "Clay":
                matches_clay = stat[1]
                try:
                    rpw_clay = float(stat[7].replace("%", ""))
                    dr_clay = float(stat[8])
                    spw_clay = round((100 - rpw_clay / dr_clay) * 0.01, 3)
                    rpw_clay = round(rpw_clay * 0.01, 3)
                except ValueError:
                    spw_clay = None
                    rpw_clay = None
                    dr_clay = None
                    matches_clay = None
                print([spw_clay, rpw_clay, dr_clay, matches_clay], "Clay")
            if surface == "grass":
                if "Time Span" in stat[0]:
                    matches_grass = stat[1]
                    try:
                        rpw_grass = float(stat[7].replace("%", ""))
                        dr_grass = float(stat[8])
                        spw_grass = round((100 - rpw_grass / dr_grass) * 0.01, 3)
                        rpw_grass = round(rpw_grass * 0.01, 3)
                    except ValueError:
                        spw_grass = None
                        rpw_grass = None
                        dr_grass = None
                        matches_grass = None
                    print([spw_grass, rpw_grass, dr_grass, matches_grass], "Grass")
            else:
                if stat[0] == "Grass":
                    matches_grass = stat[1]
                    try:
                        rpw_grass = float(stat[7].replace("%", ""))
                        dr_grass = float(stat[8])
                        spw_grass = round((100 - rpw_grass / dr_grass) * 0.01, 3)
                        rpw_grass = round(rpw_grass * 0.01, 3)
                    except ValueError:
                        spw_grass = None
                        rpw_grass = None
                        dr_grass = None
                        matches_grass = None
                    print([spw_grass, rpw_grass, dr_grass, matches_grass], "Grass")

        # MATCHES TABLE
        try:
            matches_table = tables[8].find("table", {"id": "matches"})
            # Extract the headers
            headers = [header.text.strip() for header in matches_table.find_all("th")]
        except Exception as e:
            matches_table = tables[7].find("table", {"id": "matches"})
            # Extract the headers
            try:
                headers = [
                    header.text.strip() for header in matches_table.find_all("th")
                ]
            except AttributeError:
                matches_table = []

        # Initialize a list to store all match data
        all_matches_data = []

        if len(matches_table) > 0:
            matches_table = matches_table.tbody.find_all("tr")

            # Extract the match details from each row in the matches table body
            for row in matches_table:
                # Initialize a dictionary to store data for the current match
                match_data = {}

                # Extract all cells in the row
                cells = row.find_all("td")

                # Assign each cell's text to the dictionary using the header as the key
                for header, cell in zip(headers, cells):
                    match_data[header] = cell.get_text().strip()

                # Append the match data dictionary to the list of all match data
                all_matches_data.append(match_data)

            # create a dataframe from the dictionary list
            df = pd.DataFrame(all_matches_data[:15])
            # Convert the DataFrame to a Markdown table
            md_table = df.to_markdown(index=False)
        else:
            md_table = "No matches found"
            print("No matches found")
        driver.quit()
        # print(df)
        # exit()
        # print([spw, rpw, dr, matches, peak_rank, current_rank, play_hand, player_info, md_table])
        # return list as pandas dataframe series
        return pd.Series(
            [
                spw,
                rpw,
                dr,
                matches,
                peak_rank,
                current_rank,
                play_hand,
                player_info,
                md_table,
                spw_clay,
                rpw_clay,
                dr_clay,
                matches_clay,
                spw_grass,
                rpw_grass,
                dr_grass,
                matches_grass,
            ],
            index=index_columns,
        )
    except Exception as e:
        return pd.Series(
            [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            index=index_columns,
        )
