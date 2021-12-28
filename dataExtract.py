# Importing Libraries
import time
import csv
from csv import writer
from bs4 import BeautifulSoup
from selenium import webdriver
import os
from datetime import datetime

# Defining constants
URL = 'https://athleticgreens.com/reviews/en' # Target URL
CHROME_BIN_LOCATION = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" # Location of Chrome.exe
CHROME_DRIVER_LOCATION = 'resources\\chromedriver.exe' # Location of chrome driver
REVIEWS_SCROLL_HEIGHT = 0.5 # Scroll height where reviews section starts
DATA_FILE_FOLDER = 'data' # extract folder location

RESOURCE_LOCATION = os.getcwd()  + '\\resources' # Setting up location of resources
DATA_FILE_NAME = 'data_{}.csv'.format(datetime.now().strftime('%Y-%m-%d--%H-%M-%S'))
DATA_FILE_LOCATION = DATA_FILE_FOLDER + '\\' + DATA_FILE_NAME

# Initialize counters
count_page = 0
count_reviews = 0


# Checks if resource location is added as a system path. Adds it if not
if(RESOURCE_LOCATION not in os.environ["PATH"]):
    os.environ["PATH"] += os.pathsep + RESOURCE_LOCATION


# Open Chrome in Incognito
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.binary_location =  CHROME_BIN_LOCATION


# Create a browser instance
browser = webdriver.Chrome(CHROME_DRIVER_LOCATION, options=options)



# Load the target page
browser.get(URL)
time.sleep(0.5) # Pause to let the page open
# Scroll to the reviews section
siteHeight = browser.execute_script("return document.body.scrollHeight") # Get full page height 
scrollHeight = siteHeight * REVIEWS_SCROLL_HEIGHT # Get the height at which reviews is present. We have it hardcoded here
browser.execute_script("window.scrollTo(0,{})".format(scrollHeight)) # Scroll to reviews section
time.sleep(2) # Let the reviews section load

soup = BeautifulSoup(browser.page_source, 'html.parser') # Parse page using BS4
maxReviews = soup.find('span', {'class':'reviews-qa-label font-color-gray'}).text.split()[0] # Get a count of max reviews

# Start parsing reviews on every page
while count_reviews < int(maxReviews):
    list_reviews = []

    buttons = browser.find_elements_by_xpath('/html/body/div[2]/div/div/main/div/section[5]/div/div/div/div/div[5]/div[4]/nav/div/a')
    print(count_page, count_reviews, maxReviews)
    for button in buttons:
        if count_page == 0:
            break
        if button.text!="":
            if int(button.text) == count_page + 1:
                button.click()
                break
    time.sleep(2)

    soup = BeautifulSoup(browser.page_source, 'html.parser')
    reviews = soup.find_all('div', {'class': lambda e: 'yotpo-review yotpo-regular-box' in e if e else False})
    for review in reviews:
        name = review.find('span', {'class': 'y-label yotpo-user-name yotpo-font-bold pull-left'}).text
        rating = review.find('span', {'class': 'sr-only'}).text
        dt = review.find('span', {'class': 'y-label yotpo-review-date'}).text
        heading = review.find('div', {'class': 'content-title yotpo-font-bold'}).text
        text = review.find('div', {'class': 'content-review'}).text

        element = [name, rating, dt, heading, text]
        list_reviews.append(element)

    with open(DATA_FILE_LOCATION, 'a', encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(list_reviews)
    
    count_reviews = count_reviews + len(list_reviews)
    count_page = count_page + 1

