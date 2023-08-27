import requests
from bs4 import BeautifulSoup
import psycopg2
from decouple import config
db_host = config('DB_HOST')
db_port = config('DB_PORT')
db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
db_name = config('DB_NAME')

# Now, you can use these values in your code
db_params = {
    'host': db_host,
    'port': db_port,
    'user': db_user,
    'password': db_password,
    'database': db_name,
}

# Define the base URL of the page you want to scrape
base_url = "https://finance.yahoo.com/most-active"

try:
    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Define the SQL statement to insert data into the table (modify as per your table structure)
    insert_query = """
    INSERT INTO stocks (symbol, name, price, change, percent_change, volume,avg3month,market_cap)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    page_number = 0  # Start with the first page
    while True:
        # Create the URL for the current page
        url = f"{base_url}?count=100&offset={page_number * 100}"  # Assuming each page shows 25 items
        print(url)
        # Send an HTTP GET request to the current page
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Find the table containing the stock data (you may need to inspect the page source to identify the table)
            table = soup.find("table")

            # If the table is not found, it means you've reached the end of the pages
            if not table:
                break

            # Create empty lists to store the data
            stock_data = []

            # Iterate through rows in the table
            for row in table.find_all("tr")[1:]:
                # Extract data from each cell in the row
                
                cells = row.find_all("td")
                symbol = cells[0].text.strip()
                name = cells[1].text.strip()
                price = cells[2].text.strip()
                change = cells[3].text.strip()
                percent_change = cells[4].text.strip()
                volume = cells[5].text.strip()
             
                avg_vol_3_month = cells[6].text.strip()
                  
                
                market_cap = cells[7].text.strip()
          

                # Append the data to the stock_data list
                stock_data.append({
                    "Symbol": symbol,
                    "Name": name,
                    "Price": price,
                    "Change": change,
                    "Percent Change": percent_change,
                    "Volume": volume,
                    "Avg Vol (3 month)": avg_vol_3_month,
                    "Market Cap": market_cap,
                
                })

            for stock in stock_data:
                print(stock)
                percent_change_value = float(stock["Percent Change"].strip('%'))
                # Transform volume values like "134.99M" to "134990000"
                volume_str = stock["Volume"]
                if volume_str.endswith("M"):
                    volume_value = float(volume_str[:-1]) * 1000000  # Remove 'M' and multiply by 1 million
                elif volume_str.endswith("T"):
                    volume_value = float(volume_str[:-1]) * 1000000000
                else:
                    volume_value =  float(volume_str) 

                
                # Transform avg_vol_3_month values like "24.796M" to "24796000"
                avg_vol_3_month_str = stock["Avg Vol (3 month)"]
                if avg_vol_3_month_str.endswith("M"):
                    avg_vol_3_month_value = float(avg_vol_3_month_str[:-1]) * 1000000

                elif avg_vol_3_month_str.endswith("T"):
                    avg_vol_3_month_value = float(avg_vol_3_month_str[:-1]) * 1000000000
                else:
                    avg_vol_3_month_value = float(avg_vol_3_month_str)
                
                # Transform market_cap values like "2.259B" to "2259000000"
                market_cap_str = stock["Market Cap"]
                if market_cap_str.endswith("B"):
                    market_cap_value = float(market_cap_str[:-1]) * 1000000  # Remove 'B' and multiply by 1 billion
                elif market_cap_str.endswith("T"):
                    market_cap_value = float(market_cap_str[:-1]) * 1000000000  # Remove 'T' and multiply by 1 trillion
                else:
                    market_cap_value = float(market_cap_str)
                
              
   
              
              
                # Insert data into the database
                cursor.execute(insert_query, (
                    stock["Symbol"], stock["Name"], stock["Price"], stock["Change"],
                    percent_change_value, volume_value,avg_vol_3_month_value,market_cap_value
                  

                )) 
              
          # Commit the changes for each page
            conn.commit()

            # Increment the page number to navigate to the next page
            page_number += 1
            print('pagina '+str(page_number)+' '+'completata')
        else:
            print("Failed to retrieve the web page. Status code:", response.status_code)
            break

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print("All Stocks successfully inserted into the database.")
except Exception as e:
    print("Error:", e)
