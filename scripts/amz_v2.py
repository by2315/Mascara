import json
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options

def webdriver_options():
    chrome_options = Options()
    Options.add_argument('--headless')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-new-window')
    return chrome_options
def search_amazon(search_product_name):

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver_options())
    driver.get('https://www.amazon.com')

    #Search Product Name in Search Bar of Amazon
    try:
        search = driver.find_element(By.ID, 'twotabsearchtextbox')
        search.send_keys(search_product_name)
        search_button = driver.find_element(By.ID, 'nav-search-submit-button')
        search_button.click()
    except NoSuchElementException:
        try:
            driver.refresh()
            search = driver.find_element(By.ID, 'nav-bb-search')
            search.send_keys(search_product_name)
            search_button = driver.find_element(By.CLASS_NAME, 'nav-bb-button')
            search_button.click()
        except NoSuchElementException:
            print("No Search Bar, Couldn't search because didn't find element 'twotabsearchtextbox' or 'nav-bb-search'!")
            sys.exit()

    #Index through each product in search result and scrap product data
    products = []

    last_product_page = 0
    while last_product_page != 1:
        try:
            pagination = driver.find_element(By.XPATH,
                                             '//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]').get_attribute(
                'href')
            products.append(scrape_page(driver, products))

            #Save Products Dataset
            save_products(keyword, products)

            # Open the Next Product Search Page
            last_product_page = 0
            driver.get(pagination)

        except NoSuchElementException:
            last_product_page = 1
            scrape_page(driver, products)

            # Save Products Dataset
            save_products(keyword, products)

    driver.quit()
    return products
def scrape_page(web_driver,products_dataset):
    try:
        items = wait(web_driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
    except NoSuchElementException:
        web_driver.refresh()
        try:
            items = wait(web_driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
        except NoSuchElementException:
            print('No products found!')
            return products_dataset
    for item in items:
        product = scrap_product(item)
        products_dataset.append(product)

    return products_dataset
def scrap_product(individual_item):
    product = {}
    # Extract Product Name
    try:
        name = individual_item.find_element(By.XPATH, '//span[@class="a-size-base-plus a-color-base a-text-normal"]')
        product['name'] = name.text
    except NoSuchElementException:
        product['name'] = []
        pass

    # Extract Product Asin
    try:
        product_asin = individual_item.get_attribute("data-asin")
        product['asin'] = product_asin
    except NoSuchElementException:
        product['asin'] = []
        pass

    # Extract Product Price
    try:
        whole_price = individual_item.find_elements(By.XPATH, './/span[@class="a-price-whole"]')
        fraction_price = individual_item.find_elements(By.XPATH, './/span[@class="a-price-fraction"]')

        if whole_price != [] and fraction_price != []:
            price = '.'.join([whole_price[0].text, fraction_price[0].text])
        else:
            price = 0
        product['price'] = price
    except NoSuchElementException:
        product['price'] = []

    # Extract Rating
    try:
        rating_box = individual_item.find_elements(By.XPATH, './/div[@class="a-row a-size-small"]/span')

        if rating_box:
            rating = rating_box[0].get_attribute('aria-label')
            rating_num = rating_box[1].get_attribute('aria-label')
        else:
            rating, rating_num = 0, 0

        product['rating'] = rating
        product['rating_Num'] = rating_num
    except NoSuchElementException:
        product['rating'] = []
        product['rating_Num'] = []

    # Find Product URL and Open URL
    product_url = individual_item.find_element(By.XPATH,
                                    './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute(
        "href")
    product['product_url'] = product_url

    driver_product = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver_options())
    driver_product.get(product_url)

    try:
        wait(driver_product, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "a-section a-spacing-none")]')))
    except (NoSuchElementException, TimeoutException) as e:
        driver_product.refresh()

    # Find and open All Reviews URL for Product
    try:
        review_url = driver_product.find_elements(By.XPATH,
                                                  '//a[@data-hook="see-all-reviews-link-foot" and contains(@class, "a-link-emphasis a-text-bold")]')
    except (NoSuchElementException, TimeoutException) as e:
        driver_product.refresh()
        review_url = driver_product.find_elements(By.XPATH,
                                                  '//a[@data-hook="see-all-reviews-link-foot" and contains(@class, "a-link-emphasis a-text-bold")]')

    ############
    print(review_url[0].get_attribute('href'))
    ############

    if review_url != []:
        product['review_url'] = review_url[0].get_attribute('href')
        driver_product.get(product['review_url'])
        try:
            wait(driver_product, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@role, "main")]')))
        except (NoSuchElementException, TimeoutException) as e:
            try:
                driver_product.refresh()
                wait(driver_product, 30).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@role, "main")]')))
            except (NoSuchElementException, TimeoutException) as e:
                return product

    else:
        product['review_url'] = []
        product['reviews'] = []
        return product


    # Extract Reviews for product
    reviews = []
    last_review_page = 0

    while last_review_page != 1:

        try:
            next_page = driver_product.find_element(By.XPATH, '//li[@class="a-last"]//a')

            reviews.append(scrap_product_reviews(driver_product,reviews))

            driver_product.get(next_page.get_attribute('href'))

            # Check if next page is loaded
            try:
                wait(driver_product, 30).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@role, "main")]')))
            except NoSuchElementException:
                driver_product.refresh()

            last_review_page = 0

        except NoSuchElementException:
            last_review_page = 1
            reviews.append(scrap_product_reviews(driver_product,reviews))

    product['reviews'] = reviews

    # Close the driver product webdriver
    driver_product.quit()

    return product
def scrap_product_reviews(web_driver_product_reviews, review_dataset):
    # Extract review elements

    try:
        review_elements = web_driver_product_reviews.find_elements(By.XPATH, '//div[@data-hook="review"]')
    except NoSuchElementException:
        print("No Reviews Element Found in Page")
        review={}
        review_dataset.append(review)
        return review_dataset

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
            review['img'] = [image.get_attribute('src') for image in review_images_element]
        except NoSuchElementException:
            review['img'] = 'None'
            pass

        #Append review to review_dataset
        review_dataset.append(review)

    return review_dataset
def save_products(product_name, products_dataset):
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    file_name = f'{product_name}_amazon_reviews_{current_time}.txt'

    with open(file_name, 'w') as f:
        f.write(json.dumps(products_dataset))

keyword = "Mascara"
search_amazon(keyword)

# Problems
# Convert downloaded image url to 64bit data (ChatGPT)
# Add Checking Mechanism to compare newly added product to existing product



