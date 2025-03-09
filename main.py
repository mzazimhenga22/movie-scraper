from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

app = Flask(__name__)

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode.
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Specify the path to the Chrome binary installed in your Docker image.
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


@app.route('/')
def index():
    return jsonify({"message": "Reelgood Scraper API is running"})

@app.route('/scrape/movie', methods=['GET'])
def scrape_movie():
    movie_name = request.args.get('movie_name')
    if not movie_name:
        return jsonify({"error": "movie_name parameter is required"}), 400

    # Build the search URL
    search_url = f"https://reelgood.com/search?q={movie_name}"
    driver = init_driver()
    driver.get(search_url)

    try:
        # Wait up to 15s for search results to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-testid="content-listing-link"]'))
        )
    except Exception as e:
        driver.quit()
        return jsonify({"error": f"No results or page took too long to load: {str(e)}"}), 404

    # Now find all result links
    result_links = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="content-listing-link"]')
    movie_options = []
    movie_links = []
    counter = 1

    for link_element in result_links:
        try:
            # Title is in <span data-testid="content-listing-title">Inception</span>
            title_element = link_element.find_element(By.CSS_SELECTOR, 'span[data-testid="content-listing-title"]')
            title = title_element.text.strip()
        except Exception:
            # Fallback: get text from the link itself
            title = link_element.text.strip()

        href = link_element.get_attribute("href")
        if href and not href.startswith("http"):
            href = "https://reelgood.com" + href

        movie_options.append({"option": counter, "title": title})
        movie_links.append(href)
        counter += 1

    driver.quit()
    return jsonify({
        "movie_options": movie_options,
        "movie_links": movie_links
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
