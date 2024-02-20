import re
import requests
from flask import Flask, render_template, request
import json
from urllib.parse import unquote

#Regex
FACEBOOK_VIDEO_REGEX = r"https?://(?:www\.)?facebook\.com/(?:[^/?]+/)?(?:videos|watch)(?:\?.*v=|/)(\d+)"


app = Flask(__name__)
def decode_facebook_url(url):
    # Decode escape characters in the URL
    return json.loads('"' + url + '"')

def get_facebook_video_links(video_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',  # Adjust language preference as needed
        'Referer': 'https://www.facebook.com/',  # The URL of the page that linked to the resource being requested
        'Upgrade-Insecure-Requests': '1',  # Indicates that the client supports a newer version of HTTP
        'DNT': '1',  # Do Not Track setting, indicating the user's preference regarding tracking
        'Connection': 'keep-alive',  # Specifies options that are desired for a particular connection
        'Cache-Control': 'max-age=0',  # Specifies directives for caching mechanisms in both requests and responses
        'Sec-Fetch-Dest': 'document',  # Indicates how a particular type of resource will be used
        'Sec-Fetch-Mode': 'navigate',  # Specifies how a particular resource is fetched
        'Sec-Fetch-Site': 'same-origin',  # Indicates the site of the resource being fetched
        'Sec-Fetch-User': '?1',  # Indicates whether or not user credentials are sent with the request
    }


    response = requests.get(video_url, headers=headers)
    if response.status_code == 200:
        data = response.text

        # Extract SD link
        sd_link_match = re.search(r'browser_native_sd_url":"([^"]+)"', data)
        sd_link = sd_link_match.group(1) if sd_link_match else None
        if sd_link:
            sd_link = sd_link.replace("\\/", "/")  # Replace escaped slashes

        # Extract HD link
        hd_link_match = re.search(r'browser_native_hd_url":"([^"]+)"', data)
        hd_link = hd_link_match.group(1) if hd_link_match else None
        if hd_link:
            hd_link = hd_link.replace("\\/", "/") 
            hd_link = hd_link.replace("\\u00253D\\u00253D", "%3D%3D")  # Replace problematic substring

        # Extract thumbnail URI
        thumbnail_uri_match = re.search(r'"preferred_thumbnail":"(https?:\/\/[^"]+)"', data)
        thumbnail_uri = thumbnail_uri_match.group(1) if thumbnail_uri_match else None

        
        return sd_link, hd_link, thumbnail_uri
    else:
        return None, None, None
    
    
@app.route('/', methods=['GET', 'POST'])
def index():
    download_link = None
    sd_link = None
    hd_link = None
    thumbnail_uri = None
    error_message = None

    if request.method == 'POST':
        video_url = request.form['video_url']
        if is_facebook_video_url(video_url):
            sd_link, hd_link, thumbnail_uri = get_facebook_video_links(video_url)
            if sd_link or hd_link:
                download_link = True  # Flag to show download buttons
            else:
                error_message = 'No download links found for the provided Facebook video URL.'
        else:
            error_message = 'Please enter a valid Facebook video URL.'

    return render_template('index.html', download_link=download_link, sd_link=sd_link, hd_link=hd_link, thumbnail_uri=thumbnail_uri, error_message=error_message)


def is_facebook_video_url(url):
    return bool(re.match(FACEBOOK_VIDEO_REGEX, url))

if __name__ == '__main__':
    app.run(debug=True)
