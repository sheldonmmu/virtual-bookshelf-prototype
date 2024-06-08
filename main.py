import streamlit as st
import requests
from requests.exceptions import ConnectTimeout, RequestException
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import base64

CLIENT_ID = st.secrets["client_id"]
CLIENT_SECRET = st.secrets["client_secret"] # OCLC API endpoints
TOKEN_URL = 'https://oauth.oclc.org/token'
NEW_TITLES_URL = 'https://discovery.api.oclc.org/new-titles'

# Streamlit app
def app():
    # browser tab config
    st.set_page_config(page_title="New Books", page_icon="🔖")
    
    # logo and page title section
    # Function to read and encode the image
    def get_image_as_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    # Path to your local image
    image_path = "assets\logo.png"
    alt_text = "MMU Library"

    # Get the base64 encoded image
    image_base64 = get_image_as_base64(image_path)

    # Create the HTML code with the base64 image and alt text
    html_code = f"""
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <img src="data:image/png;base64,{image_base64}" alt="{alt_text}" style="margin-right: 20px;">
        <h1 style="margin: 0;">New Books</h1>
    </div>
    """
       # Render the HTML in Streamlit
    st.markdown(html_code, unsafe_allow_html=True)

    # Step 1: Get an access token using oauth library
    scope = ['new-titles']
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    client = BackendApplicationClient(client_id=CLIENT_ID, scope=scope)
    oauth = OAuth2Session(client=client)

    try:
        token = oauth.fetch_token(token_url=TOKEN_URL, auth=auth)
        print("Access token obtained successfully.")

        # Step 2: Call the New Titles API
        headers = {
            'Accept': 'application/json'
        }
        params = {
            'limit': 50,
            'startDate': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'heldBySymbol': ['U@M'],
            'itemType': 'book',
            'orderBy': 'DateAddedDsc',
            #'topic': '34000000'  # conspectus subject - Language, Linguistics & Literature (everything)
        }
        new_titles_response = oauth.get(NEW_TITLES_URL, headers=headers, params=params)
        new_titles_response.raise_for_status()  # Raise an exception if the request failed
        print("New Titles API response received successfully.")

        # Step 3: Process the response
        new_titles_data = new_titles_response.json()
        print("New Titles API response data:", new_titles_data)

        if 'briefRecords' in new_titles_data:
            print("briefRecords found in the response.")
            row_count = 0  # Keep track of the current row

            for row_count in range(8):  # Iterate over 8 rows
                cols = st.columns(6)  # Create 6 columns per row

                for col_count in range(6):  # Iterate over 6 columns
                    index = row_count * 6 + col_count
                    if index < len(new_titles_data['briefRecords']):
                        title = new_titles_data['briefRecords'][index]
                        isbns = title.get('isbns', [])
                        oclc_number = title.get('oclcNumber', '')
                        cover_image = None

                        # Define the dimensions as variables
                        cover_width = 128
                        cover_height = 184

                        for isbn in isbns:
                            try:
                                # If the longitood.com API fails, try the Google Books API
                                api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
                                response = requests.get(api_url, timeout=5)  # Set a timeout of 5 seconds
                                response.raise_for_status()  # Raise an exception if the request failed
                                data = response.json()
                                if 'items' in data and 'volumeInfo' in data['items'][0] and 'imageLinks' in data['items'][0]['volumeInfo']:
                                    cover_url = data['items'][0]['volumeInfo']['imageLinks'].get('thumbnail')
                                    if cover_url:
                                        cover_image = requests.get(cover_url).content
                                        break  # Exit the loop if a cover image is found
                            except (ConnectTimeout, RequestException):
                                print(f"Error occurred while fetching cover image from Google Books API for ISBN: {isbn}")

                        if cover_image is None:
                            default_image_path = "assets/default_books.jpg"
                            if os.path.exists(default_image_path):
                                with open(default_image_path, 'rb') as f:
                                    cover_image = f.read()

                        # Define oclc_url here
                        oclc_url = f"https://mmu.on.worldcat.org/oclc/{oclc_number}"

                        # Display the book cover with title overlay
                        with cols[col_count]:
                            st.markdown(f"""
                                <div style="position: relative; padding: 10px 0;">
                                <a href="{oclc_url}">
                                <img src="data:image/jpeg;base64,{base64.b64encode(cover_image).decode('utf-8')}" alt="Book Cover" style="width: 100%;">
                                </a>
                                <div style="position: absolute; bottom: 10px; left: 0; right: 0; background-color: rgba(255, 255, 255, 0.8); padding: 5px; text-align: left; width: 100%; max-width: 128px; margin: 0 auto; height: 100px; display: flex; flex-direction: column; justify-content: flex-start;">
                                <a href="{oclc_url}" style="color: black; text-decoration: none; max-width: 100%; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                                {(title.get('title', 'N/A')[:60] + '...' if len(title.get('title', 'N/A')) > 60 else title.get('title', 'N/A'))}
                                </a>
                                </div>
                                </div>
                            """, unsafe_allow_html=True)

        else:
            print("No briefRecords found in the response.")
            st.write("No new titles found.")

    except requests.exceptions.HTTPError as err:
        st.error(err)
    except BaseException as err:
        st.error(err)

if __name__ == "__main__":
    app()
