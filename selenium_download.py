import time  # Library for adding delays (to wait for elements/actions)
import os  # Library for file handling and environment variables
import glob  # Library for finding file paths using patterns
import shutil  # Library for moving/renaming files
import pandas as pd  # Pandas for working with dataframes and Excel conversion
import json  # Library for parsing JSON data
from selenium import webdriver  # WebDriver is used to automate browser actions
from selenium.webdriver.common.by import By  # Library for finding elements by different strategies (like ID, XPATH, etc.)
from selenium.webdriver.chrome.options import Options  # Allows us to customize Chrome browser settings for Selenium
from webdriver_manager.chrome import ChromeDriverManager  # Automatically manage ChromeDriver versions

# Define the download directory using an environment variable from GitHub Actions.
# If the environment variable is not found, it falls back to '/default/path'
DOWNLOAD_DIR = os.getenv('GITHUB_WORKSPACE', '/default/path')

# Set up Chrome browser options for Selenium (e.g., headless mode and file download settings)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Headless mode to run the browser without a GUI (useful for CI/CD)
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,  # Directory where downloaded files will be saved
    "download.prompt_for_download": False,  # Disable download prompts to avoid user interaction
    "download.directory_upgrade": True,  # Automatically move downloaded files to the correct directory
    "safebrowsing.enabled": True  # Enable safe browsing to avoid warnings on file downloads
})

# Automatically download and set up the ChromeDriver using webdriver-manager
driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=chrome_options)

# Function to download the file using Selenium
def download_file():
    try:
        # Step 1: Navigate to the website's file download page
        driver.get("http://the-internet.herokuapp.com/download")

        # Step 2: Find the link to the file ('some-file.txt') and click it to start the download
        file_link = driver.find_element(By.LINK_TEXT, 'some-file.txt')
        file_link.click()

        # Step 3: Wait for the download to complete
        time.sleep(5)  # Wait for 5 seconds to ensure the file is fully downloaded (adjust this as needed)
    finally:
        # Close the browser when done, even if an error occurs
        driver.quit()

# Function to find the most recently downloaded .txt file in the download directory
def find_latest_downloaded_file():
    # Get a list of all .txt files in the download directory, sorted by modification time (most recent last)
    log_files = sorted(glob.glob(os.path.join(DOWNLOAD_DIR, '*.txt')), key=os.path.getmtime)

    # If no .txt files are found, print an error and return None
    if not log_files:
        print("No log files found.")
        return None

    # Get the most recently downloaded file (last in the sorted list)
    latest_log_file = log_files[-1]
    print(f"Latest downloaded log file: {latest_log_file}")
    
    # Rename the file with a timestamp for clarity
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    renamed_file = os.path.join(DOWNLOAD_DIR, f"logs_{current_time}.txt")
    shutil.move(latest_log_file, renamed_file)  # Move and rename the file to include the timestamp

    # Return the renamed file path
    return renamed_file

# Function to convert the downloaded .txt file into an Excel file
def convert_txt_to_excel(txt_file, excel_output):
    try:
        # Read the content of the .txt file (assuming it contains JSON)
        with open(txt_file, 'r') as file:
            content = file.read()  # Read the entire file content as a string
            json_data = json.loads(content)  # Parse the string as JSON data
        
        # Convert the JSON data into a Pandas DataFrame
        df = pd.DataFrame(json_data)

        # Save the DataFrame to an Excel file
        df.to_excel(excel_output, index=False)  # index=False avoids saving DataFrame row numbers
        print(f"Conversion complete. Data saved to {excel_output}")
    except Exception as e:
        # If there's an error (e.g., file is not JSON), print the error
        print(f"Error converting to Excel: {e}")

# The main entry point of the script
if __name__ == "__main__":
    # Step 1: Download the file using Selenium
    download_file()

    # Step 2: Find the most recent downloaded .txt file
    latest_file = find_latest_downloaded_file()

    # Step 3: Convert the downloaded .txt file to an Excel file
    if latest_file:
        # Generate a filename for the Excel output
        excel_output = os.path.join(DOWNLOAD_DIR, f'logs_output_{time.strftime("%Y-%m-%d")}.xlsx')
        
        # Convert the .txt file to Excel
        convert_txt_to_excel(latest_file, excel_output)
