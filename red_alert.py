from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

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

# Open the webpage
driver.get(url)

# Wait for the table to load
wait = WebDriverWait(driver, 20)  # You might need to adjust the wait time

# Set the date values using JavaScript
new_start_date = '15/05/2024'
new_end_date = '16/05/2024'

try:
    # Wait for the start date input to be present
    start_date_input = wait.until(EC.presence_of_element_located((By.ID, 'txtDateFrom')))
    end_date_input = wait.until(EC.presence_of_element_located((By.ID, 'txtDateTo')))

    # Update start date
    driver.execute_script("arguments[0].removeAttribute('readonly');", start_date_input)
    driver.execute_script("arguments[0].value = arguments[1];", start_date_input, new_start_date)

    # Update end date
    driver.execute_script("arguments[0].removeAttribute('readonly');", end_date_input)
    driver.execute_script("arguments[0].value = arguments[1];", end_date_input, new_end_date)

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

finally:
    # Close the browser
    driver.quit()

df = pd.DataFrame(alert_data)

# Display the DataFrame
print(df)

# Save as csv
df.to_csv('Israel_rocket_data')

print('Exported csv succesfully!')