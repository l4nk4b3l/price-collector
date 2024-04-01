import json
import csv
from urllib import parse


from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()
driver.implicitly_wait(15)

# Load page
driver.get("https://suchen.mobile.de/fahrzeuge/search.html?dam=false&fr=2020%3A&isSearchRequest=true&ml=%3A10000&ms=13900%3B%3B%3Bduke+125&od=up&ref=srp&refId=055e9561-8387-2c8b-e5cf-dbd48d41de35&s=Motorbike&sb=p&vc=Motorbike")

# Accept cookies
cookie = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/button")
cookie.click()

page = 1


class Listing:
    def __init__(self, id, mileage, price):
        self.id = id
        self.mileage = mileage
        self.price = price

listings = []

while True:
    # Get the page count. Page = data-testid="srp-pagination"
    pager = driver.find_element(By.XPATH, "//*[@data-testid='srp-pagination']")
    nextPageButton = pager.find_element(By.XPATH, "./ul/li[last()]")

    # Get all data from page
    # We are looking for the price and go up three divs
    elems = driver.find_elements(By.XPATH, "//*[@data-testid='price-label']/ancestor::div[3]")

    for elem in elems:
        price = elem.find_element(By.XPATH, ".//*[@data-testid='price-label']").text.rstrip(' €')
        url = elem.find_element(By.XPATH, "./a").get_attribute("href")
        id = query_def=parse.parse_qs(parse.urlparse(url).query)['id'][0]
        print("Price: " + price)
        print("Link: " + url)
        print("id: " + id)

        text = elem.find_element(By.XPATH, ".//*[@data-testid='listing-details-attributes']/div").text
        mileage = "0"

        # Examples:
        # 'EZ 01/2020 • 6.929 km • 11 kW (15 PS) • 125 cm³'
        # 'Neufahrzeug • 11 kW (15 PS) • 125 cm³'
        if text.startswith('EZ'):
            mileage = text.split('•')[1].strip().rstrip(' km')

        print("Mileage: " + mileage)
        print("Debug:  " + elem.find_element(By.XPATH, ".//*[@data-testid='listing-details-attributes']/div").text)
        print('\n')
        listing = Listing(id, mileage, price)
        listings.append(listing)

    # Go to next page
    if nextPageButton.text != 'Weitere Angebote':
        break

    nextPageButton.click()
    page = page + 1

driver.close()

with open('listings.csv', mode='w', encoding='utf-8') as listings_file:
    listing_writer = csv.writer(listings_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

    for listing in listings:
        listing_writer.writerow([listing.id, listing.mileage, listing.price])