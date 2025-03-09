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
    # Specify the binary location if needed (update if necessary)
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

@app.route('/')
def index():
    return jsonify({"message": "123Movies Scraper API is running"})

@app.route('/scrape/movie', methods=['GET'])
def scrape_movie():
    movie_name = request.args.get('movie_name')
    if not movie_name:
        return jsonify({"error": "movie_name parameter is required"}), 400

    # Construct the search URL for 123Movies clone.
    search_url = f"https://ww3.0123movies.com.co/?s={movie_name}"
    driver = init_driver()
    driver.get(search_url)

    try:
        # Wait up to 15 seconds for search results to appear.
        # Update the selector below after inspecting the website's HTML.
        results = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.movie-item'))
        )
    except Exception as e:
        driver.quit()
        return jsonify({"error": f"No results found or page took too long to load: {str(e)}"}), 404

    movie_options = []
    movie_links = []
    counter = 1

    for result in results:
        try:
            # Update this selector to match the title element on the page.
            title_element = result.find_element(By.CSS_SELECTOR, 'h2.movie-title')
            title = title_element.text.strip()
        except Exception:
            title = result.text.strip()

        try:
            # Assuming the movie link is on an <a> tag within the movie item.
            link = result.find_element(By.TAG_NAME, 'a').get_attribute("href")
        except Exception:
            link = ""

        movie_options.append({"option": counter, "title": title})
        movie_links.append(link)
        counter += 1

    driver.quit()
    return jsonify({
        "movie_options": movie_options,
        "movie_links": movie_links
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
