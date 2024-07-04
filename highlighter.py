from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def get_most_viewed_parts(youtube_url):
    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(options=options)
    
    # Open the YouTube video URL
    driver.get(youtube_url)
    
    try:
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ytp-heat-map-path')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        path_element = soup.find('path', class_='ytp-heat-map-path')
        
        if not path_element:
            print("Heat map data not found.")
            return []
        path_data = path_element.get('d')
        timestamps = parse_path_data(path_data)
        formatted_timestamps = [convert_to_minutes_seconds(ts) for ts in timestamps]
        return formatted_timestamps

    finally:
        # Close the Selenium WebDriver
        driver.quit()

def parse_path_data(path_data):
    # Split the path data into commands and values
    commands = path_data.split(' ')
    
    # Initialize lists to store timestamps and other data
    timestamps = []
    x_values = []
    y_values = []
    
    # Parse the commands to extract x and y values
    for i in range(0, len(commands), 3):
        if commands[i] == 'M' or commands[i] == 'C':
            x = float(commands[i+1].split(',')[0])
            y = float(commands[i+1].split(',')[1])
            x_values.append(x)
            y_values.append(y)
    
    # Determine the timestamps based on x-values and y-values
    i = 11
    while i < len(x_values):
        print(x_values[i])
        if y_values[i] < 10:  # Stricter threshold to identify "most viewed" parts
            timestamps.append(round(x_values[i]))  # Round x-values to nearest integer
            # Skip the next 30 seconds (assuming 1 unit in x-values corresponds to 1 second)
            i += 30
        else:
            i += 1
    print(x_values)
    return timestamps

def convert_to_minutes_seconds(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"

# Example usage
youtube_url = 'https://www.youtube.com/watch?v=yW1peuwi5vM'
timestamps = get_most_viewed_parts(youtube_url)
print("Most viewed parts of the video:", timestamps)
