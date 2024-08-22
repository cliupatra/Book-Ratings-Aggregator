import requests
import json
from flask import Flask, request, jsonify

GOOGLE_API_KEY = ''
GOOGLE_URL = f'https://www.googleapis.com/books/v1/volumes'

OPEN_LIBRARY_URL = 'https://openlibrary.org'

app = Flask(__name__)


def get_google_book(book_id):
    response = requests.get(
        f'{GOOGLE_URL}/{book_id}', params={'key': GOOGLE_API_KEY})
    if response.status_code == 200:
        return response.json()
    else:
        return f'Error: {response.status_code}'


def get_open_library_book(book_id):
    response = requests.get(f'{OPEN_LIBRARY_URL}/works/{book_id}.json')
    if response.status_code == 200:
        return response.json()
    else:
        return f'Error: {response.status_code}'


@app.route('/google_book/<book_id>', methods=['GET'])
def get_google_book_details(book_id):
    book = get_google_book(book_id)
    volume_info = book.get('volumeInfo')
    title = volume_info.get('title')
    author = volume_info.get('authors')
    average_rating = volume_info.get("averageRating", "No rating available")
    ratingsCount = volume_info.get('ratingsCount')
    return {'title': title, 'Author(s)': author, 'rating': average_rating, 'Ratings Count': ratingsCount, 'Book Id' : book_id}

def get_author_name(author_key):
    author_data = requests.get(f'{OPEN_LIBRARY_URL}{author_key}.json')
    return author_data.json()

def get_rating_summary(work_id):
    ratings_response = requests.get(f'{OPEN_LIBRARY_URL}{work_id}/ratings.json')
    rating_data = ratings_response.json()
    rating_summary = rating_data.get('summary')
    return rating_summary

@app.route('/openlibrary_book', methods=['GET'])
def get_open_library_book_details():
    book_id = request.args.get('book_id')
    book = get_open_library_book(book_id)

    work_id = book.get('works')[0].get('key')

    title = book.get('title')
    author = get_author_name(book.get('authors')[0].get('key'))
    author_name = author.get('name')

    ratings_summary = get_rating_summary(work_id)
    average_rating = ratings_summary.get('average', 'no rating available')
    ratingsCount = ratings_summary.get('count', 'No ratings count available')

    return {'title': title, 'Author(s)': author_name, 'Ratings' : average_rating, 'Ratings Count': ratingsCount, 'work_id' : work_id}


@app.route('/search_google', methods=['GET'])
def search_google_books():
    query = request.args.get('q')
    if query is None:
        return 'Need query paramter'
    google_response = requests.get(f'{GOOGLE_URL}', params={'q':query, 'key' : GOOGLE_API_KEY})
    if google_response.status_code == 200:
        return google_response.json()
    else:
        return f'Error: {google_response.status_code}'
    

@app.route('/search_openlibrary', methods=['GET'])
def search_open_library():
    query = request.args.get('q')
    response = requests.get(f'{OPEN_LIBRARY_URL}/search.json?', params={'q': query})
    if response.status_code == 200:
        return response.json()
    else:
        return f'Error: {response.status_code}'

if __name__ == '__main__':
    app.run(debug=True)
