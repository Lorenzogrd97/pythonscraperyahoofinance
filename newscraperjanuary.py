from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import pymongo
import time

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["yahoo_stocks"]
collection = db["stock_data"]

# Function to scrape Yahoo finance and insert data into MongoDB


def scrape_and_insert():
    base_url = "https://finance.yahoo.com/quote/{}/"

    # Selenium setup
    driver = webdriver.Edge()  # Make sure to have Edge WebDriver installed and in PATH
    driver.implicitly_wait(10)  # Implicit wait

    # Navigate to Yahoo Finance
    driver.get("https://finance.yahoo.com/most-active/")
    time.sleep(5)  # Let the page load
    # scroll-down-btn
    elementScrollDown = driver.find_element(
        By.CSS_SELECTOR, "#scroll-down-btn")
    elementScrollDown.click()
    elementRefuseAll = driver.find_element(
        By.CSS_SELECTOR, "#consent-page > div > div > div > form > div.wizard-body > div.actions.couple > button.btn.secondary.reject-all")
    elementRefuseAll.click()
    time.sleep(5)
    # Find the table element
    while True:
        try:
            # Find the table element
            table = driver.find_element(
                By.CSS_SELECTOR, "#scr-res-table > div.Ovx\(a\).Ovx\(h\)--print.Ovy\(h\).W\(100\%\) > table")

            # Find all rows in the table
            rows = table.find_elements(By.TAG_NAME, "tr")

            # Loop through each row
            for row in rows:
                # Find all cells in the row
                cells = row.find_elements(By.TAG_NAME, "td")
                # Loop through each cell and print its text
                for cell in cells:
                    print(cell.text)

            # Find the next page button and click it
            next_page_button = driver.find_element(
                By.CSS_SELECTOR, "#scr-res-table > div.W\(100\%\).Mt\(15px\).Ta\(end\) > button.Va\(m\).H\(20px\).Bd\(0\).M\(0\).P\(0\).Fz\(s\).Pstart\(10px\).O\(n\)\:f.Fw\(500\).C\(\$linkColor\)")
            next_page_button.click()
            time.sleep(5)
        except NoSuchElementException:
            # If no next page button is found, break out of the loop
            break
    # Closing Selenium
    driver.quit()

# Main function to run the scraping process and restart


def main():
    while True:
        scrape_and_insert()
        print("Scraping and insertion completed. Restarting in 24 hours...")
        time.sleep(86400)  # 24 hours delay


if __name__ == "__main__":
    main()
