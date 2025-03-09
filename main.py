from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

app = Flask(__name__)

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode.
    chrome_options.add_argument("--disable-gpu")
    # Add other options if necessary (e.g., --no-sandbox)
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

    search_url = f"https://reelgood.com/search?q={movie_name}"
    driver = init_driver()
    driver.get(search_url)
    # Wait for the page to load dynamic content.
    time.sleep(5)  # Consider using WebDriverWait for a more robust solution.

    # Find elements using Selenium.
    results = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="result-item"]')
    movie_options = []
    movie_links = []
    counter = 1
    for result in results:
        try:
            title_element = result.find_element(By.CSS_SELECTOR, 'div.result-title')
            title = title_element.text.strip()
        except Exception:
            title = result.text.strip()
        link = result.get_attribute("href")
        if link and not link.startswith("http"):
            link = "https://reelgood.com" + link
        movie_options.append({"option": counter, "title": title})
        movie_links.append(link)
        counter += 1

    driver.quit()
    return jsonify({
        "movie_options": movie_options,
        "movie_links": movie_links
    })

@app.route('/scrape/movie/stream', methods=['GET'])
def scrape_movie_stream():
    movie_url = request.args.get('movie_url')
    if not movie_url:
        return jsonify({"error": "movie_url parameter is required"}), 400

    driver = init_driver()
    driver.get(movie_url)
    time.sleep(5)

    try:
        stream_link_element = driver.find_element(By.CSS_SELECTOR, 'a.streaming-link')
        stream_link = stream_link_element.get_attribute("href")
        if stream_link and not stream_link.startswith("http"):
            stream_link = "https://reelgood.com" + stream_link
    except Exception:
        driver.quit()
        return jsonify({"error": "Stream link not found"}), 404

    driver.quit()
    return jsonify({"stream_link": stream_link})

@app.route('/scrape/series', methods=['GET'])
def scrape_series():
    series_name = request.args.get('series_name')
    if not series_name:
        return jsonify({"error": "series_name parameter is required"}), 400

    search_url = f"https://reelgood.com/search?q={series_name}"
    driver = init_driver()
    driver.get(search_url)
    time.sleep(5)

    results = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="result-item"]')
    series_options = []
    series_links = []
    counter = 1
    for result in results:
        # Check if the result is tagged as TV (assuming a "data-type" attribute indicates this).
        data_type = result.get_attribute("data-type")
        if data_type and data_type.lower() == "tv":
            try:
                title_element = result.find_element(By.CSS_SELECTOR, 'div.result-title')
                title = title_element.text.strip()
            except Exception:
                title = result.text.strip()
            link = result.get_attribute("href")
            if link and not link.startswith("http"):
                link = "https://reelgood.com" + link
            series_options.append({"option": counter, "title": title})
            series_links.append(link)
            counter += 1

    driver.quit()
    return jsonify({
        "series_options": series_options,
        "series_links": series_links
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
