import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire.utils import decode

import psycopg2
from decouple import config

# Retrieve database connection parameters from environment variables or a configuration file
db_host = config('DB_HOST')
db_port = config('DB_PORT')
db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
db_name = config('DB_NAME')

# Set up database connection parameters
db_params = {
    'host': db_host,
    'port': db_port,
    'user': db_user,
    'password': db_password,
    'database': db_name,
}

# Define the base URL of the page you want to scrape
base_url = "https://finance.yahoo.com/most-active"
base_url_quote = "https://finance.yahoo.com/quote/"
gecko_driver_path = "/usr/local/bin/geckodriver"

try:
    # Establish a connection to the PostgreSQL database
    # conn = psycopg2.connect(**db_params)
    # cursor = conn.cursor()

    # Create FirefoxOptions
    firefox_options = FirefoxOptions()

    # Create a FirefoxService instance (you don't need to specify the executable_path)
    # Create a FirefoxService instance with log output
    firefox_service = FirefoxService(
        log_path='/Users/lorenzopassamonti/Developer/pythonscraperyahoofinance/geckodriver.log')

    # Initialize the Firefox WebDriver with the FirefoxService and FirefoxOptions
    browser = webdriver.Firefox(
        options=firefox_options, service=firefox_service)

    page_number = 0  # Start with the first page
    while True:
        if page_number == 0:
            # Create the URL for the current page
            # Assuming each page shows 25 items
            url = f"{base_url}"
            print(url)

            # Load the URL in the headless browser
            browser.get(url)

            # Wait for the "Load More" button to be clickable
            load_more_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div/div/div/div/form/div[2]/div[2]/button[2]"))
            )
            load_more_button.click()

            # Wait for the page to load (you might need to adjust the time based on your internet speed)
            time.sleep(10)

            tables = browser.find_elements(By.TAG_NAME, 'table')

            if tables:
                # Assuming you want to scrape the first table found on the page
                table = tables[0]
                # Extract data from the table
                rows = table.find_elements(
                    By.TAG_NAME, 'tr')  # Find all table rows
                for row in rows:
                    # Extract data from each row
                    # Find all table cells in the row
                    cells = row.find_elements(By.TAG_NAME, 'td')

                    for index, cell in enumerate(cells):
                        print(cell.text)
                    #     if index == 0:
                    #         url_quote = f"{base_url_quote}" + \
                    #             cell.text+"?p"+cell.text
                    #         print(url_quote)
                    #         # Check if it's the first iteration
                    #         browser.get(url_quote)
                    # for request in all_request:

                        #     body = decode(request.body, request.headers.get(
                        #         'Content-Encoding', 'identity'))
                        #     decoded_body = body.decode('utf-8')
                        #     print(decoded_body)
                        #     # print(body)

                        #     # if request.url.startswith("https://query1.finance.yahoo.com/v8/finance"):
                        #     #     if request.response and request.response.status_code:

                        #     #         print(request.response)
                        #     #         print(request.url, request.response.status_code,
                        #     #               request.response.headers['Content-Type'])
                    # print("finished")

            else:
                print("No tables found on the page")
                time.sleep(2000000)

            # Increment the page number to navigate to the next page
            page_number += 1

        else:
            # Wait for the "Load More" button to be clickable on subsequent pages
            load_more_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/section/div/div[2]/div[2]/button[3]"))
            )
            load_more_button.click()

            # Wait for the page to load (you might need to adjust the time based on your internet speed)
            time.sleep(10)

            tables = browser.find_elements(By.TAG_NAME, 'table')

            if tables:
                # Assuming you want to scrape the first table found on the page
                table = tables[0]
                # Extract data from the table
                rows = table.find_elements(
                    By.TAG_NAME, 'tr')  # Find all table rows
                for row in rows:
                    # Extract data from each row
                    # Find all table cells in the row
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    for cell in cells:
                        print(cell.text)  # Print the text content of each cell
            else:
                print("No tables found on the page")
                time.sleep(2000000)

except Exception as e:
    print("Error:", e)
finally:
    # Close the browser when done
    if 'browser' in locals():
        browser.quit()
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()
