# import beautifulsoup4
from selenium import webdriver
from bs4 import BeautifulSoup
import logging
from selenium.webdriver.chrome.options import Options as ChromeOptions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)


def tennisabstract_scrape_atp():


    # Specify the URL where the Selenium Hub is running
    hub_url = "http://selenium-hub:4444/wd/hub"  # Use hostname/IP of your selenium_hub service if running remotely

    # Define options for the Chrome browser
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)

    # Instantiate a remote WebDriver object connecting to the Selenium Hub
    driver = webdriver.Remote(
        command_executor=hub_url, options=chrome_options
    )

    # Target URL
    url = "https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p=JiriLehecka"
    driver.get(url)

    # Get the HTML content
    html = driver.page_source

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')
    #logging.info(soup)

    tables = soup.find_all('table')#, class_='tennis-match__match-link')

    # Iterate over each <a> tag and perform an action, like printing the href attribute
    i = 0
    for table in tables:
        logging.info(table)
        logging.info("---------------Table: " + str(i))
        i += 1
        #break

    # clean all html tags
    player_info = tables[5].get_text()
    logging.info(player_info)
    logging.info("---------------Table: " + str(5))
    soup = tables[4]

    # Find the player's bio section and extract player information
    player_bio_section = soup.find(id="biog")
    name_country = player_bio_section.find('b').get_text() if player_bio_section.find('b') else None
    date_of_birth = player_bio_section.find(text="Date of birth: ").next_sibling if player_bio_section.find(text="Date of birth: ") else None
    play_hand = player_bio_section.find(text="Plays: ").next_sibling if player_bio_section.find(text="Plays: ") else None
    current_rank = player_bio_section.find(text="Current rank: ").find_next('b').get_text() if player_bio_section.find(text="Current rank: ") else None
    peak_rank = player_bio_section.find(text="Peak rank: ").find_next('b').get_text() if player_bio_section.find(text="Peak rank: ") else None

    print(f"Name and Country: {name_country}")
    for tr in soup.find_all('tr'):
        td = tr.find('td')
        if td:
            text_content = td.text
            # Checking and splitting based on known labels
            if 'Date of birth' in text_content:
                date_of_birth = text_content.split(': ')[1].strip()
            elif 'Plays' in text_content:
                play_hand = text_content.split(': ')[1].strip()
            elif 'Peak Rank' in text_content:
                peak_rank = text_content.split(': ')[1].strip()
    print(f"Date of Birth: {date_of_birth}")
    print(f"Play Hand: {play_hand}")
    print(f"Current Rank: {current_rank}")
    print(f"Peak Rank: {peak_rank}")

    # Now let's get the statistics from the 'wonloss' section
    stats_table = soup.find(id="wonloss")

    # Extracting the header
    headers = []
    for header in stats_table.find_all('th'):
        headers.append(header.get_text().strip())

    # Extracting the stats for each row
    stats_data = []
    for row in stats_table.find_all('tr')[1:]:  # Skipping the headers
        stats = []
        for cell in row.find_all(['td', 'th']):
            stats.append(cell.get_text().strip())
        stats_data.append(stats)

    # Displaying the results
    print("\nStatistics:")
    print(headers)
    for stat in stats_data:
        print(stat)

    # MATCHES TABLE
    matches_table = tables[8].find('table', {'id': 'matches'})

    # Extract the headers
    headers = [header.text.strip() for header in matches_table.find_all('th')]

    # Initialize a list to store all match data
    all_matches_data = []

    # Extract the match details from each row in the matches table body
    for row in matches_table.tbody.find_all('tr'):
        # Initialize a dictionary to store data for the current match
        match_data = {}

        # Extract all cells in the row
        cells = row.find_all('td')

        # Assign each cell's text to the dictionary using the header as the key
        for header, cell in zip(headers, cells):
            match_data[header] = cell.get_text().strip()

        # Append the match data dictionary to the list of all match data
        all_matches_data.append(match_data)

    # Display the extracted matches data
    for match in all_matches_data:
        print(match)
    # Close the browser session when done
    driver.quit()

