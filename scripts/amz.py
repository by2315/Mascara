import requests
from bs4 import BeautifulSoup
import time
import json

'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.366'

def get_total_pages(search_query):
    # Format the search query for the Amazon URL
    formatted_query = search_query.replace(' ', '+')
    url = f'https://www.amazon.com/s?k={formatted_query}'

    # Define user agent header
    headers = ({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    })

    # Send a GET request to the search results page
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the pagination container
        pagination = soup.find('span', {'class': 's-pagination-item s-pagination-disabled'})
        if pagination:
            total_pages = int(pagination.text.strip())
            return total_pages

    return 0

## Need to Optimize out the Sponsored and Highly rated reviews because they will be duplicates
def search_amazon_mascara(search_query, num_pages):
    search_results = []

    total_pages = get_total_pages(search_query)
    if total_pages == 0:
        print("No search results found.")


    # Format the search query for the Amazon URL
    formatted_query = search_query.replace(' ', '+')

    for page in range(1, total_pages + 1):

        '#################'
        page=1
        '#################'

        print(page, 'Out of', total_pages)

        url = f'https://www.amazon.com/s?k={formatted_query}&page={page}'

        # Define user agent header
        headers = ({
            'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 10066.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'

        })

        # Send a GET request to the search results page
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the search result containers
            result_containers = soup.find_all('div', {'data-component-type': 's-search-result'})

            for container in result_containers:
                result = {}

                # Extract the product name
                '####################'
                product_name = result_containers[0].find('span', {'class': 'a-size-base-plus'})
                '####################'

                if product_name:
                    result['product_name'] = product_name.text.strip()
                else:
                    continue

                # Extract the product URL
                '####################'
                product_url = result_containers[0].find('a', {'class': 'a-link-normal'})
                '####################'

                if product_url:
                    result['product_url'] = 'https://www.amazon.com' + product_url['href']
                else:
                    continue

                # Extract the Review URL
                product_response = requests.get(result['product_url'], headers=headers)

                if product_response.status_code == 200:
                    product_soup = BeautifulSoup(product_response.content, 'html.parser')
                    review_url = product_soup.find('a', {'data-hook': 'see-all-reviews-link-foot'})

                    if review_url:
                        result['review_url'] = 'https://www.amazon.com' + review_url['href']
                    else:
                        continue

                result['reviews']=scrape_amazon_reviews(result['review_url'])

                search_results.append(result)

        # Add a delay of 2 seconds between requests to avoid overwhelming the server
        time.sleep(2)
    return search_results

#Need to Optimize to find all reviews
def scrape_amazon_reviews(review_url):

    reviews = []

    # Define user agent header
    review_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0'
    }

    for page_number in range(1, 1000):

        # Send a GET request to the product page
        review_response = requests.get(result['review_url'], headers=review_headers)

        print(review_response)

        if review_response.status_code == 200:

            review_soup = BeautifulSoup(review_response.text, 'html.parser')

            # Find the review containers

            review_containers = review_soup.find_all('div', {'data-hook':'review'})

            print(review_containers)

            if not (review_containers):
                return reviews

            for container in review_containers:
                review = {}

                # Extract the reviewer name
                reviewer = container.find('span', {'class': 'a-profile-name'})
                if reviewer:
                    review['reviewer'] = reviewer.text.strip()
                else:
                    review['reviewer'] = 'Anonymous'

                # Extract the review rating
                rating = container.find('span', {'class': 'a-icon-alt'})
                if rating:
                    review['rating'] = rating.text.strip().split()[0]
                else:
                    review['rating'] = 'Not available'

                # Extract the review text
                review_text = container.find('span', {'data-hook': 'review-body'})
                if review_text:
                    review['review_text'] = review_text.text.strip()
                else:
                    review['review_text'] = 'No review text available'

                reviews.append(review)


search_query = 'mascara'
num_pages =1
# Perform the search and get the search results
search_results = search_amazon_mascara(search_query, num_pages)

filename = 'amz_review_URL.txt'
with open(filename,'w')as f:
    f.write(json.dumps(search_results))

# Iterate over each search result
for result in search_results:
    product_name = search_results['product_name']
    product_url = search_results['product_url']

    print(f'Product Name: {product_name}')
    print(f'Product URL: {product_url}')

    # Scrape the reviews for the product
    scraped_reviews = scrape_amazon_reviews(product_url)

    if scraped_reviews:
        for review in scraped_reviews:
            print(f'Reviewer: {review["reviewer"]}')
            print(f'Rating: {review["rating"]}')
            print(f'Review: {review["review_text"]}')
            print('---')

# Save the reviews to a text file
filename = 'amazon_reviews.txt'
save_reviews_to_file(scraped_reviews, filename)
print(f'Reviews saved to file: {filename}')

https://www.amazon.com/Covergirl-Lash-Blast-Mascara-Black/product-reviews/B00EMAM9BC/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&pageNumber=1
https://www.amazon.com/Covergirl-Lash-Blast-Mascara-Black/product-reviews/B00EMAM9BC/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=2
https://www.amazon.com/Covergirl-Lash-Blast-Mascara-Black/product-reviews/B00EMAM9BC/ref=cm_cr_getr_d_paging_btm_next_3?ie=UTF8&reviewerType=all_reviews&pageNumber=3

'---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'
from selenium import webdriver
'from selenium.webdriver.firefox.service import Service
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
'from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType

HOSTNAME = 'us.smartproxy.com'
PORT = '10000'
DRIVER = 'CHROME'

def smartproxy():
  prox = Proxy()
  prox.proxy_type = ProxyType.MANUAL
  prox.http_proxy = '{hostname}:{port}'.format(hostname = HOSTNAME, port = PORT)
  prox.ssl_proxy = '{hostname}:{port}'.format(hostname = HOSTNAME, port = PORT)
  if DRIVER == 'FIREFOX':
    capabilities = webdriver.DesiredCapabilities.FIREFOX
  elif DRIVER == 'CHROME':
    capabilities = webdriver.DesiredCapabilities.CHROME
  prox.add_to_capabilities(capabilities)
  return capabilities

def webdriver_example():
  if DRIVER == 'FIREFOX':
    browser = webdriver.Firefox(service=Service(GeckoDriverManager().install()), proxy=smartproxy())
  elif DRIVER == 'CHROME':
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), desired_capabilities=smartproxy())

  browser.get('https://www.amazon.com/Covergirl-Lash-Blast-Mascara-Black/product-reviews/B00EMAM9BC/ref=cm_cr_dp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=4')

  print(browser.page_source)
  browser.quit()

if __name__ == '__main__':
  webdriver_example()

'---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'
  from selenium import webdriver
  from selenium.webdriver.common.by import By
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC


  def scrape_amazon_reviews(url):
      # Set up Selenium webdriver
      driver = webdriver.Chrome()
      driver.get(url)

      # Wait for the review section to load
      WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'cm_cr-review_list')))

      # Extract the review elements
      review_elements = driver.find_elements(By.XPATH, '//div[@data-hook="review"]')

      products = []
      for review_element in review_elements:
          product = {}

          # Extract reviewer name
          reviewer_element = review_element.find_element(By.XPATH, './/span[@class="a-profile-name"]')
          review['reviewer'] = reviewer_element.text.strip()

          # Extract review rating
          rating_element = review_element.find_element(By.XPATH, './/i[@data-hook="review-star-rating"]')
          review['rating'] = rating_element.get_attribute('aria-label').strip().split()[0]

          # Extract review text
          review_text_element = review_element.find_element(By.XPATH, './/span[@data-hook="review-body"]')
          review['review_text'] = review_text_element.text.strip()

          reviews.append(review)

      # Close the Selenium webdriver
      driver.quit()

      return reviews


  # Example usage
  url = 'https://www.amazon.com/product-reviews/PRODUCT_ID'
  reviews = scrape_amazon_reviews(url)

  for review in reviews:
      print(f'Reviewer: {review["reviewer"]}')
      print(f'Rating: {review["rating"]}')
      print(f'Review: {review["review_text"]}')
      print('---')

