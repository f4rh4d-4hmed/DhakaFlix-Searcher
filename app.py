from flask import Flask, request, jsonify, render_template
import requests
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

servers = {
    "DHAKA-FLIX-7": "http://172.16.50.7/DHAKA-FLIX-7/",
    "DHAKA-FLIX-8": "http://172.16.50.8/DHAKA-FLIX-8/",
    "DHAKA-FLIX-9": "http://172.16.50.9/DHAKA-FLIX-9/",
    "DHAKA-FLIX-12": "http://172.16.50.12/DHAKA-FLIX-12/",
    "DHAKA-FLIX-14": "http://172.16.50.14/DHAKA-FLIX-14/",
}

allowed_extensions = ['.mp3', '.mp4', '.mkv', '.iso', '.zip']

def has_allowed_extension(filename):
    return any(filename.endswith(ext) for ext in allowed_extensions)

def get_icon(ext):
    icons = {
        '.mp4': 'fa fa-file-video-o',
        '.zip': 'fa-solid fa-file-archive',
        '.rar': 'fa-solid fa-file-archive',
        '.7z': 'fa-solid fa-file-archive',
        '.avi': 'fa-solid fa-film',
        '.iso': 'fa-solid fa-compact-disc',
        '.mp3': 'fa-solid fa-music',
        '.mkv': 'fa fa-file-video-o',
        '.apk': 'fa fa-file-o',
        '.exe': 'fa fa-file-o',
        '.pdf': 'fa fa-file-pdf-o',
        '.tar': 'fa fa-file-archive-o',
        '.gz': 'fa fa-file-archive-o',
        '.wav': 'fa fa-file-audio-o',
        '.ogg': 'fa fa-file-audio-o',
        '.rpm': 'fa fa-linux',
        '.deb': 'fa fa-linux',
    }
    return icons.get(ext, 'fa-solid fa-file falinux')

def fetch_results(server_name, base_url, query):
    search_results = []
    request_json = {
        "action": "get",
        "search": {
            "href": f"/{server_name}/",
            "pattern": query,
            "ignorecase": True
        }
    }

    try:
        response = requests.post(base_url, json=request_json, timeout=30)
        response_data = response.json()
        for item in response_data.get("search", []):
            href = item.get("href")
            if has_allowed_extension(href):
                full_link = base_url.rstrip('/') + href if not href.startswith(f"/{server_name}") else base_url.rstrip('/') + href.replace(f"/{server_name}", '', 1)
                ext = href.split('.')[-1]
                search_results.append({
                    "name": unquote(href.split('/')[-1]),
                    "url": full_link,
                    "ext": f".{ext}",
                    "icon": get_icon(f".{ext}")
                })
    except Exception as e:
        print(f"Error fetching data from {base_url}: {e}")
    return search_results

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    all_results = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_results, server_name, base_url, query) for server_name, base_url in servers.items()]
        for future in futures:
            all_results.extend(future.result())

    return render_template('index.html', search_results=all_results, search_performed=True)



@app.route('/')
def index():
    return render_template('index.html', search_results=[])

if __name__ == '__main__':
    app.run(debug=True)
