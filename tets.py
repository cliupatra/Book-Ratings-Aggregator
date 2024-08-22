import requests
import json

# Set your API key and URL
GOOGLE_URL = 'https://www.googleapis.com/books/v1/volumes?'
GOOGLE_API_KEY = '123'
book_id = 'zyTCAlFPjgYC?'

# # Make the request
# response = requests.get(f'{url}/{book_id}', {'key':key})

# # Check if the request was successful
# if response.status_code == 200:
#     data = response.json()
#     print(data)
# else:
#     print(f"Error {response.status_code}: {response.text}")


# def search_google_books(query):
#   response = requests.get(
#     f'{url}/{query}', params={'key': key})
#   if response.status_code == 200:
#     print(response.json())
#   else:
#     return f'Error: {response.status_code}'


# search_google_books('zyTCAlFPjgYC')

def search_google_books():
    query = 'flowers'
    if query is None:
        return 'Need query paramter'
    google_response = requests.get(f'{GOOGLE_URL}', params={
                                   'q': query, 'key': GOOGLE_API_KEY})
    
    return google_response.json()



str = json.dumps(search_google_books(), indent=4)
print(str)