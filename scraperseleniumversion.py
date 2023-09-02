import time
from selenium import webdriver
from bs4 import BeautifulSoup
import psycopg2
from decouple import config
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
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
gecko_driver_path = "/usr/local/bin/geckodriver"

try:
    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Define the SQL statement to insert data into the table (modify as per your table structure)
    # insert_query = """
    # INSERT INTO stocks (symbol, name, price, change, percent_change, volume, avg3month, market_cap)
    # VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    # """

    # Create FirefoxOptions
    firefox_options = FirefoxOptions()
    firefox_options.add_argument('--headless')

    # Create a FirefoxService instance (you don't need to specify the executable_path)
    # Create a FirefoxService instance with log output
    firefox_service = FirefoxService(log_path='/usr/local/bin/geckodriver.log')

    # Initialize the Firefox WebDriver with the FirefoxService and FirefoxOptions
    browser = webdriver.Firefox(
        options=firefox_options, service=firefox_service)

    page_number = 0  # Start with the first page
    while True:
        # Create the URL for the current page
        # Assuming each page shows 25 items
        url = f"{base_url}?offset={page_number * 25}&count=25"
        print(url)

        # Load the URL in the headless browser
        browser.get(url)
        # Wait for page to load (you might need to adjust the time based on your internet speed)
        time.sleep(5)

        # Get the fully rendered HTML using Selenium
        page_source = browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find the table containing the stock data (you may need to inspect the page source to identify the table)
        table = soup.find("table")

        # If the table is not found, it means you've reached the end of the pages
        if not table:
            break

        # Iterate through rows in the table and extract data
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            symbol = cells[0].text.strip()
            name = cells[1].text.strip()
            price = cells[2].text.strip()
            change = cells[3].text.strip()
            percent_change = cells[4].text.strip()
            volume = cells[5].text.strip()
            avg_vol_3_month = cells[6].text.strip()
            market_cap = cells[7].text.strip()

            # Transform data as needed (volume, avg_vol_3_month, market_cap)

            # Insert data into the database
            cursor.execute(insert_query, (
                symbol, name, price, change, percent_change, volume, avg_vol_3_month, market_cap
            ))

        # Increment the page number to navigate to the next page
        page_number += 1
        print('Page ' + str(page_number) + ' completed')

    # Commit the changes after processing all pages
    conn.commit()
    print("All Stocks successfully inserted into the database.")

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
