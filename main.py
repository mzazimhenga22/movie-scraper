from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Use a realistic User-Agent header to mimic a browser.
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/115.0.0.0 Safari/537.36")
}

@app.route('/')
def index():
    return jsonify({"message": "Reelgood Scraper API is running"})

# ------------------------------
# Endpoint: Search for Movies
# ------------------------------
@app.route('/scrape/movie', methods=['GET'])
def scrape_movie():
    movie_name = request.args.get('movie_name')
    if not movie_name:
        return jsonify({"error": "movie_name parameter is required"}), 400

    # Reelgood search URL. (This is an example; adjust as needed.)
    search_url = f"https://reelgood.com/search?q={movie_name}"
    response = requests.get(search_url, headers=HEADERS)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch search results from Reelgood"}), 500

    soup = BeautifulSoup(response.content, "html.parser")
    # Example: Assume each search result is in an <a> with a data-testid attribute.
    results = soup.find_all("a", {"data-testid": "result-item"})
    movie_options = []
    movie_links = []
    counter = 1
    for result in results:
        # You may need to update these selectors based on Reelgood's HTML structure.
        title_tag = result.find("div", {"class": "result-title"})
        title = title_tag.get_text(strip=True) if title_tag else result.get_text(strip=True)
        link = result.get("href")
        if link and not link.startswith("http"):
            link = "https://reelgood.com" + link
        movie_options.append({"option": counter, "title": title})
        movie_links.append(link)
        counter += 1

    return jsonify({
        "movie_options": movie_options,
        "movie_links": movie_links
    })

# ------------------------------
# Endpoint: Retrieve Movie Stream Link
# ------------------------------
@app.route('/scrape/movie/stream', methods=['GET'])
def scrape_movie_stream():
    movie_url = request.args.get('movie_url')
    if not movie_url:
        return jsonify({"error": "movie_url parameter is required"}), 400

    response = requests.get(movie_url, headers=HEADERS)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch movie page from Reelgood"}), 500

    soup = BeautifulSoup(response.content, "html.parser")
    # Reelgood usually aggregates streaming availability rather than hosting streams.
    # For demonstration, we look for an <a> element that might link to a provider.
    stream_link_tag = soup.find("a", {"class": "streaming-link"})  # <-- Update selector as needed.
    if stream_link_tag:
        stream_link = stream_link_tag.get("href")
        if stream_link and not stream_link.startswith("http"):
            stream_link = "https://reelgood.com" + stream_link
        return jsonify({"stream_link": stream_link})
    else:
        return jsonify({"error": "Stream link not found"}), 404

# ------------------------------
# Endpoint: Search for TV Series
# ------------------------------
@app.route('/scrape/series', methods=['GET'])
def scrape_series():
    series_name = request.args.get('series_name')
    if not series_name:
        return jsonify({"error": "series_name parameter is required"}), 400

    # Use the same search endpoint; Reelgood may list both movies and TV.
    search_url = f"https://reelgood.com/search?q={series_name}"
    response = requests.get(search_url, headers=HEADERS)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch search results from Reelgood"}), 500

    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("a", {"data-testid": "result-item"})
    series_options = []
    series_links = []
    counter = 1
    for result in results:
        # Assume TV series items have an attribute or indicator, for example data-type="tv".
        data_type = result.get("data-type")
        if data_type and data_type.lower() == "tv":
            title_tag = result.find("div", {"class": "result-title"})
            title = title_tag.get_text(strip=True) if title_tag else result.get_text(strip=True)
            link = result.get("href")
            if link and not link.startswith("http"):
                link = "https://reelgood.com" + link
            series_options.append({"option": counter, "title": title})
            series_links.append(link)
            counter += 1

    return jsonify({
        "series_options": series_options,
        "series_links": series_links
    })

if __name__ == '__main__':
    # Render provides the port via the PORT environment variable.
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
