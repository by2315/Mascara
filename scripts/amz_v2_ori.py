import json
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

def webdriver_options():
    chrome_options = Options()
    # options.add_argument('--headless')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-new-window')
    return chrome_options

def search_amazon(keyword,driver):
    try:
        search = driver.find_element(By.ID, 'twotabsearchtextbox')
        search.send_keys(keyword)
        search_button = driver.find_element(By.ID, 'nav-search-submit-button')
        search_button.click()
        return  (driver)
    except NoSuchElementException:
        try:
            search = driver.find_element(By.ID, 'nav-bb-search')
            search.send_keys(keyword)
            search_button = driver.find_element(By.CLASS_NAME, 'nav-bb-button')
            search_button.click()
        except NoSuchElementException:
            print("No Search Bar, Couldn't search because didn't find element 'twotabsearchtextbox' or 'nav-bb-search'!")
            sys.exit()

def scrape_page(driver,products):
    try:
        items = wait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
    except NoSuchElementException:
        driver.refresh()
        try:
            items = wait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
        except NoSuchElementException:
            print('No products found!')
            sys.exit()
    for item in items:
        product = {}

        # Extract Product Name
        try:
            name = item.find_element(By.XPATH, '//span[@class="a-size-base-plus a-color-base a-text-normal"]')
            product['name'] = name.text
        except NoSuchElementException:
            product['name'] = []
            pass

        # Extract Product Asin
        try:
            product_asin = item.get_attribute("data-asin")
            product['asin'] = product_asin
        except NoSuchElementException:
            product['asin'] = []
            pass

        # Extract Product Price
        try:
            whole_price = item.find_elements(By.XPATH, './/span[@class="a-price-whole"]')
            fraction_price = item.find_elements(By.XPATH, './/span[@class="a-price-fraction"]')

            if whole_price != [] and fraction_price != []:
                price = '.'.join([whole_price[0].text, fraction_price[0].text])
            else:
                price = 0
            product['price'] = price
        except NoSuchElementException:
            product['price'] = []

        # Extract Rating
        try:
            rating_box = item.find_elements(By.XPATH, './/div[@class="a-row a-size-small"]/span')

            if rating_box:
                rating = rating_box[0].get_attribute('aria-label')
                rating_num = rating_box[1].get_attribute('aria-label')
            else:
                ratings, ratings_num = 0, 0

            product['rating'] = rating
            product['rating_Num'] = rating_num
        except NoSuchElementException:
            product['rating'] = []
            product['rating_Num'] = []

        # find link

        product_url = item.find_element(By.XPATH,
                                        './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute(
            "href")
        product['product_url'] = product_url

        # Find and open All Reviews URL for Product

        driver_product = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver_options())
        driver_product.get(product_url)

        try:
            wait(driver_product , 30).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "a-section a-spacing-none")]')))
        except NoSuchElementException:
            driver_product.refresh()

        try:
            review_url = driver_product.find_elements(By.XPATH,'//a[@data-hook="see-all-reviews-link-foot" and contains(@class, "a-link-emphasis a-text-bold")]')
        except NoSuchElementException:
            driver_product.refresh()
            review_url = driver_product.find_elements(By.XPATH,'//a[@data-hook="see-all-reviews-link-foot" and contains(@class, "a-link-emphasis a-text-bold")]')

        if review_url:
            product['review_url'] = review_url[0].get_attribute('href')
        else:
            product['review_url'] = "none"

        driver_product.get(product['review_url'])

        try:
            wait(driver_product, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@role, "main")]')))

        except NoSuchElementException:
            driver_product.refresh()

        # Extract Reviews for product

        reviews = []
        last_review_page = 0

        while last_review_page != 1:

            try:
                next_page = driver_product.find_element(By.XPATH, '//li[@class="a-last"]//a')

                #Extract review elements
                try:
                    review_elements = driver_product.find_elements(By.XPATH, '//div[@data-hook="review"]')
                except NoSuchElementException:
                    print("No Reviews Found in Page")
                    break

                for review_element in review_elements:
                    review = {}

                    # Extract reviewer name
                    try:
                        reviewer_element = review_element.find_element(By.XPATH, './/span[@class="a-profile-name"]')
                        review['reviewer'] = reviewer_element.text.strip()
                    except NoSuchElementException:
                        review['reviewer'] = 'None'
                        pass

                    # Extract review rating
                    try:
                        rating_element = review_element.find_element(By.XPATH, './/i[@data-hook="review-star-rating"]')
                        rating = rating_element.find_element(By.XPATH, './/span[@class="a-icon-alt"]')
                        review['rating'] = rating.get_attribute('textContent').strip().split()[0]
                    except NoSuchElementException:
                        review['rating'] = 'None'
                        pass

                    # Extract review text
                    try:
                        review_text_element = review_element.find_element(By.XPATH, './/span[@data-hook="review-body"]')
                        review['review_text'] = review_text_element.text.strip()
                    except NoSuchElementException:
                        review['review_text'] = 'None'
                        pass

                    # Extract picture
                    try:
                        review_images_element = review_element.find_elements(By.XPATH,
                                                                             './/div[@class="review-image-tile-section"]//img')
                        review_images_url = [image.get_attribute('src') for image in review_images_element]
                        review['img'] = review_images_url
                    except NoSuchElementException:
                        review['img'] = 'None'
                        pass

                    reviews.append(review)

                next_page = driver_product.find_element(By.XPATH, '//li[@class="a-last"]//a')
                driver_product.get(next_page.get_attribute('href'))

                #Check if next page is loaded
                try:
                    wait(driver_product, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@role, "main")]')))
                except NoSuchElementException:
                    driver_product.refresh()

                last_review_page = 0

            except NoSuchElementException:
                last_review_page = 1
                review_elements = driver_product.find_elements(By.XPATH, '//div[@data-hook="review"]')

                for review_element in review_elements:
                    review = {}

                    # Extract reviewer name
                    try:
                        reviewer_element = review_element.find_element(By.XPATH, './/span[@class="a-profile-name"]')
                        review['reviewer'] = reviewer_element.text.strip()
                    except NoSuchElementException:
                        review['reviewer'] = 'None'
                        pass

                    # Extract review rating
                    try:
                        rating_element = review_element.find_element(By.XPATH, './/i[@data-hook="review-star-rating"]')
                        rating = rating_element.find_element(By.XPATH, './/span[@class="a-icon-alt"]')
                        review['rating'] = rating.get_attribute('textContent').strip().split()[0]
                    except NoSuchElementException:
                        review['rating'] = 'None'
                        pass

                    # Extract review text
                    try:
                        review_text_element = review_element.find_element(By.XPATH, './/span[@data-hook="review-body"]')
                        review['review_text'] = review_text_element.text.strip()
                    except NoSuchElementException:
                        review['review_text'] = 'None'
                        pass

                    # Extract picture
                    try:
                        review_images_element = review_element.find_elements(By.XPATH,
                                                                             './/div[@class="review-image-tile-section"]//img')
                        review_images_url = [image.get_attribute('src') for image in review_images_element]
                        review['img'] = review_images_url
                    except NoSuchElementException:
                        review['img'] = 'None'
                        pass
                    reviews.append(review)

            product['reviews'] = reviews

        # Close the driver product webdriver
        driver_product.quit()
        products.append(product)
    return products

# Find IP Address used by Webdriver in with this website (https://api.ipify.org?format=json)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver_options())
driver.get('https://www.amazon.com')
products = []
keyword = "Mascara"
search_amazon(keyword,driver)
scrape_page(driver,products)

last_product_page = 0
while last_product_page != 1:
    try:
        pagination = driver.find_element(By.XPATH,
                                         '//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]').get_attribute(
            'href')
        scrape_page(driver,products)

        # Open the Next Product Search Page
        last_product_page = 0
        pagination = driver.find_element(By.XPATH,
                                         '//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]').get_attribute(
            'href')
        driver.get(pagination)

    except NoSuchElementException:
        last_product_page = 1
        scrape_page(driver, products)

driver.quit()

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

filename = f'{keyword}_amazon_reviews_{timestamp}.txt'

filepath = os.path.join('Users/bill/Desktop/Know Project/scrap_data', filename)

with open(filename,'w')as f:
    f.write(json.dumps(products))

# Problems
# Convert downloaded image url to 64bit data (ChatGPT)



