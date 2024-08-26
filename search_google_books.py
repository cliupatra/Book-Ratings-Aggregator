import requests
import json
from flask import Flask, request, jsonify

GOOGLE_API_KEY = 'AIzaSyARpVh4NR03PVxDUQlXZCY-C6tZvy-h89c'
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
    ratingsCount = volume_info.get(
        'ratingsCount', 'No one has rated the book yet')
    return {'title': title, 'Author(s)': author, 'Ratings': average_rating, 'Ratings Count': ratingsCount, 'Book ID': book_id}


def fetch_openlibrary_book_details(book_id):
    book = get_open_library_book(book_id)

    if 'works' not in book:
        return f'Error: {book_id} did not have Work ID not found in book data'

    work_id = book.get('works')[0].get('key')
    work_book = get_open_library_book(work_id.replace('/works/', ''))

    title = book.get('title')

    author_list = work_book.get('authors')
    if author_list is None:
        return 'Error: No Author available'

    author = get_author_name(author_list)

    ratings_summary = get_rating_summary(work_id)
    average_rating = ratings_summary.get('average', 'no rating available')
    ratingsCount = ratings_summary.get('count', 'No ratings count available')

    return {'title': title, 'Author(s)': author, 'Ratings': average_rating, 'Ratings Count': ratingsCount, 'Book ID' : book_id ,'Work Id': work_id}


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
            average_rating += rating.get('Ratings') * \
                rating.get('Ratings Count')
            total_count += rating.get('Ratings Count')
        else:
            return "Error: titles of the books don't match"

    title = title.title()
    average_rating = round(average_rating/total_count, 2)

    return {'title': title, 'Author(s): ': author, 'Average rating: ': average_rating, 'Ratings Count: ': total_count}


def search_google_books(query):
    google_response = requests.get(f'{GOOGLE_URL}', params={
                                   'q': query, 'maxResults': 10, 'startIndex': 0, 'key': GOOGLE_API_KEY})
    if google_response.status_code == 200:
        return google_response.json()
    else:
        return f'Error: {google_response.status_code}'


def search_open_library(query):
    encoded_query = query.replace(' ', '+')
    openlibrary_response = requests.get(
        f'{OPEN_LIBRARY_URL}/search.json?', params={'q': encoded_query, 'limit': 10})
    if openlibrary_response.status_code == 200:
        return openlibrary_response.json()
    else:
        return f'Error: {openlibrary_response.status_code}'


def organize_google_results(query):
    google_results = search_google_books(query)
    results_list = google_results.get('items')
    book_list = []
    for book in results_list:
        book_id = book.get('id')
        book_details = fetch_google_book_details(book_id)
        book_list.append(book_details)
    return book_list


def organize_openlibrary_results(query):
    openlibrary_results = search_open_library(query)
    results_list = openlibrary_results.get('docs')

    book_list = []

    for book in results_list:
        book_id = book.get('edition_key')[0]
        book_details = fetch_openlibrary_book_details(book_id)
        if book_details == 'Error: No Author available':
            pass
        else:
            book_list.append(book_details)
    return book_list


def aggregate_search_results(query):
    google_list = organize_google_results(query)
    openlibrary_list = organize_openlibrary_results(query)

    book_list = []
    for o_book in openlibrary_list:
        title = o_book.get('title')
        open_id = o_book.get('Book ID')
        book = {}
        for g_book in google_list:
            if title in g_book.get('title'):
                google_id = g_book.get('Book ID')
                book = {'Google ID' : google_id}
        book['Open ID'] = open_id
        book_list.append({title : book})
    return book_list


@app.route('/search', methods=['GET'])
def get_search_results():
    query = request.args.get('q')

    if query is None:
        return 'Error: query paramter required'

    google_results = aggregate_search_results(query)
    return google_results

# print(aggregate_book_ratings('Sm5AKLXKxHgC', 'OL49950319M'))

# print(aggregate_book_ratings('o8Y5AwAAQBAJ','OL26884833M'))

# google = fetch_openlibrary_book_details('OL26816842M')
# x = json.dumps(google, indent=4)
# print(x)

@app.route('/test_search', methods=['GET'])
def test_search():
    query = 'the iron trial'
    search_results = aggregate_search_results(query)
    return search_results


# google = organize_google_results('the iron trial')
# x = json.dumps(google, indent=4)
# print(x)

# google = organize_openlibrary_results('the iron trial')
# x = json.dumps(google, indent=4)
# print(x)

# google = fetch_google_book_details('zyTCAlFPjgYC')
# x = json.dumps(google, indent=4)
# print(x)

if __name__ == '__main__':
    app.run(debug=True)
