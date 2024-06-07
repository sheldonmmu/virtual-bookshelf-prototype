import streamlit as st
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta
import base64
from PIL import Image
from io import BytesIO

CLIENT_ID = st.secrets["client_id"]
CLIENT_SECRET = st.secrets["client_secret"]

# OCLC API endpoints
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
    image_path = "logo.png"
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
            'limit': 48,
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

            for row_count in range(16):  # Iterate over 10 rows
                cols = st.columns(3)  # Create 3 columns per row

                for col_count in range(3):  # Iterate over 3 columns
                    index = row_count * 3 + col_count
                    if index < len(new_titles_data['briefRecords']):
                        title = new_titles_data['briefRecords'][index]
                        isbns = title.get('isbns', [])
                        oclc_number = title.get('oclcNumber', '')
                        cover_image = None

                        # for isbn in isbns:
                        #     # Call the longitood.com API to get the book cover URL https://github.com/w3slley/bookcover-api
                        #     api_url = f"http://bookcover.longitood.com/bookcover/{isbn}"
                        #     response = requests.get(api_url)
                        #     if response.status_code == 200:
                        #         cover_url = response.text.split('"url":"')[1].split('"}')[0]
                        #         cover_image = Image.open(BytesIO(requests.get(cover_url).content))
                        #         cover_image = cover_image.resize((750, 1125), resample=Image.BICUBIC)
                        #     if response.status_code =! 200:
                        #         api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
                        #         # psuedo code
                        #         # look for "thumbnail": 
                        #         # then take url and
                        #         cover_url = response.text.split('"url":"')[1].split('"}')[0]
                        #         cover_image = Image.open(BytesIO(requests.get(cover_url).content))
                        #         cover_image = cover_image.resize((750, 1125), resample=Image.BICUBIC)
                        #         break  # Exit the loop if a cover image is found

                        # Define the dimensions as variables
                        cover_width = 200
                        cover_height = 300

                        for isbn in isbns:
                            # Call the longitood.com API to get the book cover URL
                            api_url = f"http://bookcover.longitood.com/bookcover/{isbn}"
                            response = requests.get(api_url)
                            if response.status_code == 200:
                                cover_url = response.text.split('"url":"')[1].split('"}')[0]
                                cover_image = Image.open(BytesIO(requests.get(cover_url).content))
                                cover_image = cover_image.resize((cover_width, cover_height), resample=Image.BICUBIC)
                                break  # Exit the loop if a cover image is found
                            else:
                                # If the longitood.com API fails, try the Google Books API
                                api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
                                response = requests.get(api_url)
                                if response.status_code == 200:
                                    data = response.json()
                                    if 'items' in data and 'volumeInfo' in data['items'][0] and 'imageLinks' in data['items'][0]['volumeInfo']:
                                        cover_url = data['items'][0]['volumeInfo']['imageLinks'].get('thumbnail')
                                        if cover_url:
                                            cover_image = Image.open(BytesIO(requests.get(cover_url).content))
                                            cover_image = cover_image.resize((cover_width, cover_height), resample=Image.BICUBIC)
                                            break  # Exit the loop if a cover image is found

                        if cover_image is None:
                            # If no cover image is found, use the default image
                            default_cover_url = "https://source.unsplash.com/200x300/?lines"
                            cover_image = Image.open(BytesIO(requests.get(default_cover_url).content))
                            cover_image = cover_image.resize((200, 300), resample=Image.BICUBIC)

                        # Encode the cover image data as a base64 string
                        buffer = BytesIO()
                        cover_image.save(buffer, format='PNG')
                        cover_image_data = buffer.getvalue()
                        cover_image_base64 = base64.b64encode(cover_image_data).decode('utf-8')

                        # Display the book cover with a hyperlink
                        oclc_url = f"https://mmu.on.worldcat.org/oclc/{oclc_number}"
                        with cols[col_count]:
                            st.markdown(f"""
                                <div style="position: relative; padding: 10px 0;">
                                <a href="{oclc_url}">
                                    <img src="data:image/png;base64,{cover_image_base64}" alt="Book Cover" style="width: 100%;">
                                </a>
                                <div style="position: absolute; bottom: 10px; left: 0; right: 0; background-color: rgba(255, 255, 255, 0.9); padding: 5px; text-align: left; width: 100%; max-width: 200px; margin: 0 auto; height: 100px; display: flex; flex-direction: column; justify-content: flex-start;">
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