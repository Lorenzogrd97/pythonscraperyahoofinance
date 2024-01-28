import pymongo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["yahoo_stocks"]
collection = db["stock_data"]

# Function to scrape Yahoo finance and insert data into MongoDB


def scrape_and_insert():
    # Selenium setup
    driver = webdriver.Edge()  # Make sure to have Edge WebDriver installed and in PATH
    driver.implicitly_wait(10)  # Implicit wait

    # Navigate to Yahoo Finance
    driver.get("https://finance.yahoo.com/most-active/")
    time.sleep(5)  # Let the page load
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
            column_names = ["Symbol", "Name", "Price", "Change", "Percent Change",
                            "Volume", "Avg Vol (3 month)", "Market Cap", "PE Ratio"]
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = {}

                # Loop through each cell and insert its text into MongoDB
                for i, cell in enumerate(cells):
                    if i < len(column_names):  # Check if column index is within bounds
                        column_name = column_names[i]
                        row_data[column_name] = cell.text

                # Check if 'Symbol' key exists in row_data
                if 'Symbol' in row_data:
                    symbol = row_data["Symbol"]
                    existing_record = collection.find_one({"Symbol": symbol})
                    if existing_record:
                        collection.update_one(
                            {"Symbol": symbol}, {"$set": row_data})
                    else:
                        collection.insert_one(row_data)

            # Find the next page button and click it
            next_page_button = driver.find_element(
                By.CSS_SELECTOR, "#scr-res-table > div.W\(100\%\).Mt\(15px\).Ta\(end\) > button.Va\(m\).H\(20px\).Bd\(0\).M\(0\).P\(0\).Fz\(s\).Pstart\(10px\).O\(n\)\:f.Fw\(500\).C\(\$linkColor\)")
            next_page_button.click()
            time.sleep(5)
        except NoSuchElementException:
            break

    # Closing Selenium
    driver.quit()

# Main function to run the scraping process and restart


def main():
    while True:
        scrape_and_insert()
        print("Scraping and insertion completed. Restarting in 100 seconds...")
        time.sleep(100)


if __name__ == "__main__":
    main()
