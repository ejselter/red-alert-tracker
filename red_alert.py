from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime, timedelta
import time
start_time = time.time()


# Set up options for the WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure the browser runs in headless mode.
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Path to the chromedriver executable
webdriver_service = Service(executable_path=r"C:\Users\eitan\chromedriver-win64\chromedriver-win64\chromedriver.exe")  # Update this path as needed

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Define the URL
url = "https://www.oref.org.il//12481-en/Pakar.aspx"

# Function to set date range and scrape data
def scrape_data(start_date, end_date):
    # Open the webpage
    driver.get(url)

    # Wait for the table to load
    wait = WebDriverWait(driver, 20)  # You might need to adjust the wait time


    # Wait for the start date input to be present
    start_date_input = wait.until(EC.presence_of_element_located((By.ID, 'txtDateFrom')))
    end_date_input = wait.until(EC.presence_of_element_located((By.ID, 'txtDateTo')))

    # Update start date
    driver.execute_script("arguments[0].removeAttribute('readonly');", start_date_input)
    driver.execute_script("arguments[0].value = arguments[1];", start_date_input, start_date)

    # Update end date
    driver.execute_script("arguments[0].removeAttribute('readonly');", end_date_input)
    driver.execute_script("arguments[0].value = arguments[1];", end_date_input, end_date)

    # Trigger change events if necessary
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", start_date_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", end_date_input)

    # Wait for the table to update
    time.sleep(5)  # Adjust the sleep time if necessary to allow the table to update

    # Find and click all "show more" links
    show_more_links = driver.find_elements(By.CLASS_NAME, "alertShowMore")
    for link in show_more_links:
        driver.execute_script("arguments[0].click();", link)

    # Locate all date headers and their corresponding alert tables
    alert_data = []

    # Find all elements (both date headers and alert tables)
    all_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'alertTableDate') or contains(@class, 'alert_table')]")

    current_date = None

    for element in all_elements:
        if 'alertTableDate' in element.get_attribute('class'):
            current_date = element.text
            #print(current_date, 'current date')
        elif 'alert_table' in element.get_attribute('class'):
            category = element.find_element(By.CLASS_NAME, "alertTableCategory").text
            alert_details = element.find_elements(By.CLASS_NAME, "alertDetails")
            
            for alert in alert_details:
                alert_time = alert.find_element(By.CLASS_NAME, "alertTableTime").text
                location = alert.text.replace(alert_time, '').strip()
                alert_data.append({"date": current_date, "category": category, "time": alert_time, "location": location})
                #print(f"date: {current_date}, category: {category}, time: {time}, location: {location}")
    return alert_data


# Function to dynamically adjust date ranges based on the number of data points
def get_alert_data_within_limits(overall_start_date, overall_end_date, max_data_points=2000):
    date_format = '%d/%m/%Y'
    all_data = []

    current_end_date = overall_end_date
    current_start_date = current_end_date - timedelta(days=30)  # Start with a month

    last_loop = False    #debugging variable to escape while loop after last time around

    while current_start_date >= overall_start_date:
        print(f"Trying date range from {current_start_date.strftime(date_format)} to {current_end_date.strftime(date_format)}")
        data = scrape_data(current_start_date.strftime(date_format), current_end_date.strftime(date_format))

        if len(data) >= max_data_points:
            print(f"Reached limit with {len(data)} data points. Reducing date range.")
            current_end_date -= timedelta(days=1)
            while True:
                data = scrape_data(current_end_date.strftime(date_format), current_end_date.strftime(date_format))
                if len(data) < max_data_points:
                    break
                current_end_date -= timedelta(days=1)
        else:
            print(f"Collected {len(data)} data points from {current_start_date.strftime(date_format)} to {current_end_date.strftime(date_format)}")
            all_data.extend(data)
            current_end_date = current_start_date - timedelta(days=1)
            current_start_date = current_end_date - timedelta(days=30)
            
            if last_loop:   #break after last loop aroun
                break

            if current_start_date < overall_start_date:
                current_start_date = overall_start_date
                last_loop = True       #set last_loop if start_date is reached

    return all_data


# Define the overall date range
overall_start_date = datetime.strptime('01/03/2024', '%d/%m/%Y')
overall_end_date = datetime.strptime('26/06/2024', '%d/%m/%Y')

# Scrape data within limits
all_alert_data = get_alert_data_within_limits(overall_start_date, overall_end_date)



# Close the browser
driver.quit()

df = pd.DataFrame(all_alert_data)

# Display the DataFrame
print(df)

# Save as csv
df.to_csv('Israel_rocket_data_'+str(overall_start_date.date()), index=False)

print('Exported csv succesfully!')
print("--- %s seconds ---" % (time.time() - start_time))
