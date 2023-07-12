import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

# Find IP Address used by Webdriver in with this website (https://api.ipify.org?format=json)

products = []

chrome_options = Options()
# options.add_argument('--headless')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_argument('--disable-new-window')
# driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
# driver.get('https://api.ipify.org?format=json')
driver.get('https://www.amazon.com')

'---------'

'Add code for verifying amazon website '

'---------'

keyword = "Mascara"
try:
    search = driver.find_element(By.ID, 'twotabsearchtextbox')
    search.send_keys(keyword)
    search_button = driver.find_element(By.ID, 'nav-search-submit-button')
    search_button.click()

except NoSuchElementException:

    try:
        search = driver.find_element(By.ID, 'nav-bb-search')
        search.send_keys(keyword)
        search_button = driver.find_element(By.CLASS_NAME, 'nav-bb-button')
        search_button.click()

    except NoSuchElementException:
        print("No Element Found for 'twotabsearchtextbox' or 'nav-bb-search'!")
        sys.exit()

'---------'

'Add For Loop to loop through each product in all pages'

'---------'

# page 1
try:
    items = wait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
except NoSuchElementException:
    driver.refresh()
    try:

        items = wait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))

    except NoSuchElementException:
        print('NO products found!')
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

        if rating_box != []:
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

    # Find and Visit All Reviews URL for Product

    ##options_product = webdriver.ChromeOptions()
    ##options.add_argument('--headless')
    ##driver_prodcut = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver_product = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # driver_product.get('https://api.ipify.org?format=json')

    driver_product.get(product_url)

    try:
        review_url = driver_product.find_elements(By.XPATH,'//a[@data-hook="see-all-reviews-link-foot" and contains(@class, "a-link-emphasis a-text-bold")]')
    except NoSuchElementException:
        driver_product.refresh()
        review_url = driver_product.find_elements(By.XPATH,'//a[@data-hook="see-all-reviews-link-foot" and contains(@class, "a-link-emphasis a-text-bold")]')

    if review_url != []:
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
            last_review_page = 0

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

            next_page = driver_product.find_element(By.XPATH, '//li[@class="a-last"]//a')
            driver_product.get(next_page.get_attribute('href'))

            try:
                wait(driver_product, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@role, "main")]')))
            except NoSuchElementException:
                driver_product.refresh()

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

    # Close the Selenium webdriver
    driver_product.quit()

    products.append(product)

filename = 'amazon_reviews.txt'
with open(filename,'w')as f:
    f.write(json.dumps(products))

# Problems
# 1. Reviews contain different languages
# 2. Add verifying mechanism for amazon website vists
# 3. Change All items[1] to item
# 4. Convert downloaded image url to 64bit data (ChatGPT)
