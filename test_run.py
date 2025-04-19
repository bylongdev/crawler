from scraper.gmaps_scraper import GoogleMapsScraper 
import time

start_time = time.time()

browser = GoogleMapsScraper()
result = browser.search_business()

# print(result)

# input("Enter the business name: ")
browser.close()

end_time = time.time()
execution_time = end_time - start_time  
print(f"\nExecution time: {execution_time:.2f} seconds")
print("Browser closed successfully.")