import requests

# Set your API key and URL
url = 'https://www.googleapis.com/books/v1/volumes'
key = 'AIzaSyBKGQBM9WjJRZpclWTOKPOZfa_qVj0wLcY'
book_id = 'zyTCAlFPjgYC?'

# # Make the request
# response = requests.get(f'{url}/{book_id}', {'key':key})

# # Check if the request was successful
# if response.status_code == 200:
#     data = response.json()
#     print(data)
# else:
#     print(f"Error {response.status_code}: {response.text}")


def search_google_books(query):
  response = requests.get(
    f'{url}/{query}', params={'key': key})
  if response.status_code == 200:
    print(response.json())
  else:
    return f'Error: {response.status_code}'  


search_google_books('zyTCAlFPjgYC')
    
    
