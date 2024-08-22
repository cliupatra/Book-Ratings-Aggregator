import requests
import json
from flask import Flask, request, jsonify

GOOGLE_API_KEY = ''
GOOGLE_URL = f'https://www.googleapis.com/books/v1/volumes'

OPEN_LIBRARY_URL = 'https://openlibrary.org'

app = Flask(__name__)


def search_google_books(book_id):
    response = requests.get(
        f'{GOOGLE_URL}/{book_id}', params={'key': GOOGLE_API_KEY})
    if response.status_code == 200:
        return response.json()
    else:
        return f'Error: {response.status_code}'


def get_open_library_book(book_id):
    response = requests.get(f'{OPEN_LIBRARY_URL}/books/{book_id}.json')
    if response.status_code == 200:
        return response.json()
    else:
        return f'Error: {response.status_code}'


# def search_open_library(query):
#     encoded_query = query.replace(' ', '+')
#     response = requests.get(OPEN_LIBRARY_URL, params={'q': encoded_query})
#     if response.status_code == 200:
#         return jsonify(response.json())
#     else:
#         return f'Error: {response.status_code}'


@app.route('/book/<book_id>', methods=['GET'])
def get_google_book_details(book_id):
    book = search_google_books(book_id)
    volume_info = book.get('volumeInfo')
    title = volume_info.get('title')
    author = volume_info.get('authors')
    average_rating = volume_info.get("averageRating", "No rating available")
    ratingsCount = volume_info.get('ratingsCount')
    return {'title': title, 'Author(s)': author, 'rating': average_rating, 'Ratings Count': ratingsCount}


@app.route('/openlibrary', methods=['GET'])
def get_open_library_book_details():
    book_id = request.args.get('book_id')
    book = get_open_library_book(book_id)
    return book


# @app.route('/search', methods=['GET'])
# def search_book():
#     query = request.args.get('query') or request.args.get('q')

#     if query == None:
#         return jsonify({'error': 'query parameter is required'})

#     google_data = search_google_books(query)
#     open_library_data = search_open_library(query)

#     return google_data


if __name__ == '__main__':
    app.run(debug=True)
