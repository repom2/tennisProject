# import beautifulsoup4
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
import requests
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)


def wta_scrape():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions

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
    url = "https://www.wtatennis.com/tournament/1096/hua-hin/2024/scores"
    url = "https://www.atptour.com/en/players/alexander-zverev/z355/player-stats"
    url = "http://www.tennisabstract.com/cgi-bin/wplayer.cgi?p=EmmaNavarro"
    url = "https://www.tennisabstract.com/cgi-bin/wplayer-classic.cgi?p=EmmaNavarro"
    driver.get(url)

    # Get the HTML content
    html = driver.page_source

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')
    logging.info(soup)
    # Find all <a> tags in the HTML
    a_tags = soup.find_all('a')#, class_='tennis-match__match-link')
    a_tags = soup.find_all('a', class_=lambda
        value: value and 'tennis-match' in value)

    # Iterate over each <a> tag and perform an action, like printing the href attribute
    for a in a_tags:
        logging.info(a)
        print(a.get('href'))  # Print the hyperlink reference

    all_div_tags = soup.find_all('div', class_=lambda
        value: value and 'tournament-scores' in value)
    for div_tag in all_div_tags:
        #logging.info(div_tag)
        a_tags = div_tag.find_all('a')#, class_='tennis-match__match-link')
        for a in a_tags:
            logging.info(a)
            print(a.get('href'))

    # Close the browser session when done
    driver.quit()

