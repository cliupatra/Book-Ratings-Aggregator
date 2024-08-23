import requests
import json
from flask import Flask, request, jsonify

GOOGLE_API_KEY = '123'
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


def fetch_google_book_details(book_id):
    book = get_google_book(book_id)
    volume_info = book.get('volumeInfo')
    title = volume_info.get('title')
    author = volume_info.get('authors')
    average_rating = volume_info.get("averageRating", "No rating available")
    ratingsCount = volume_info.get('ratingsCount')
    return {'title': title, 'Author(s)': author, 'Ratings': average_rating, 'Ratings Count': ratingsCount, 'Book Id': book_id}


def fetch_openlibrary_book_details(book_id):
    book = get_open_library_book(book_id)
    work_id = book.get('works')[0].get('key')
    work_book = get_open_library_book(work_id.replace('/works/', ''))

    title = book.get('title')

    author_list = work_book.get('authors')
    author = get_author_name(author_list)

    ratings_summary = get_rating_summary(work_id)
    average_rating = ratings_summary.get('average', 'no rating available')
    ratingsCount = ratings_summary.get('count', 'No ratings count available')

    return {'title': title, 'Author(s)': author, 'Ratings': average_rating, 'Ratings Count': ratingsCount, 'work_id': work_id}


@app.route('/google_book', methods=['GET'])
def get_google_book_details():
    book_id = request.args.get('book_id')

    if book_id is None:
        return 'Requires query parameter'

    book_data = fetch_google_book_details(book_id)
    return book_data


def get_author_name(author_list):
    author_names = []
    for author in author_list:
        if author.get('author', 'None') == None:
            pass
        else:
            author_key = author.get('author').get('key')
            author_data = requests.get(
                f'{OPEN_LIBRARY_URL}{author_key}.json')
            author_name = author_data.json().get('name')
            author_names.append(author_name)

    return author_names


def get_rating_summary(work_id):
    ratings_response = requests.get(
        f'{OPEN_LIBRARY_URL}{work_id}/ratings.json')
    rating_data = ratings_response.json()
    rating_summary = rating_data.get('summary')
    return rating_summary


@app.route('/openlibrary_book', methods=['GET'])
def get_open_library_book_details():
    book_id = request.args.get('book_id')
    book_data = fetch_openlibrary_book_details(book_id)
    return book_data


def aggregate_book_ratings(google_book_id, openlibrary_book_id):
    google_ratings = fetch_google_book_details(google_book_id)
    open_library_ratings = fetch_openlibrary_book_details(openlibrary_book_id)

    return [google_ratings, open_library_ratings]


@app.route('/ratings', methods=['GET'])
def get_book_ratings():
    google_book_id = request.args.get('google_id')
    openlibrary_book_id = request.args.get('openlibrary_id')

    if google_book_id is None or openlibrary_book_id is None:
        return 'You are missing a query parameter'
    
    book_ratings = aggregate_book_ratings(google_book_id, openlibrary_book_id)

    average_rating = 0
    total_count = 0
    title = book_ratings[0].get('title').lower()
    author = book_ratings[0].get('Author(s)')

    for rating in book_ratings:
        if rating.get('title').lower() in title:
            average_rating += rating.get('Ratings') * rating.get('Ratings Count')
            total_count += rating.get('Ratings Count')
        else:
            return "Error: titles of the books don't match"
    
    title = title.title()
    average_rating = round(average_rating/total_count, 2)

    return {'title': title, 'Author(s): ': author, 'Average rating: ': average_rating, 'Ratings Count: ': total_count}


@app.route('/search_google', methods=['GET'])
def search_google_books():
    query = request.args.get('q')
    if query is None:
        return 'Need query paramter'
    google_response = requests.get(f'{GOOGLE_URL}', params={
                                   'q': query, 'key': GOOGLE_API_KEY})
    if google_response.status_code == 200:
        return google_response.json()
    else:
        return f'Error: {google_response.status_code}'


@app.route('/search_openlibrary', methods=['GET'])
def search_open_library():
    query = request.args.get('q')
    response = requests.get(
        f'{OPEN_LIBRARY_URL}/search.json?', params={'q': query})
    if response.status_code == 200:
        return response.json()
    else:
        return f'Error: {response.status_code}'





print(aggregate_book_ratings('Sm5AKLXKxHgC', 'OL49950319M'))

print(aggregate_book_ratings('o8Y5AwAAQBAJ','OL26884833M'))
if __name__ == '__main__':
    app.run(debug=True)
