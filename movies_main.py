import numpy as np
import sqlite3
#import enchant
from scipy.sparse import lil_matrix

from db_creation import database_create
from db_request import  db_request_no_params, db_request_find_film
from recommender import recommender

#d = enchant.Dict("en_US")


def input_check(word):

    word_check=d.check(word)
    if word_check is False:

        print 'Maybe your input is not correct:', word
        words_new = d.suggest(word)
        print 'Suggested input instead:'
        print words_new, 'Number of suggestions 1 -', len(words_new)
        num = raw_input('Please choose the word from the list, to continue search with the initial word input 0:  ')

        try:
            num=int(num)
        except:
            print 'Incorrect input, exit!'
            exit()

        if num > 0:
            suggest = words_new[num-1]
        else:
            suggest = word

        print 'Looking for:', suggest

    else:
        print 'Checking the input... done!'
        suggest = word

    return suggest


def genre_dict_empty(cur):

    genre_dict=dict()
    request_genre = db_request_no_params(cur, 'get genre')

    for item in request_genre:
        genre_dict[item[0]]=genre_dict.get(item[0],0)
    return genre_dict


def print_result(search_result, genre_dict):

    id_local=None
    genres_out=dict()

    for item in search_result:

        genres_out[item[0]]=genres_out.get(item[0], '')+item[5]+' '
        genre_dict[item[4]]=genre_dict.get(item[4],0)+1

        if int(item[0]) == id_local:
            continue

        print 'Film id:', item[0], '||', item[1], '|| Year:', item[2], '||  Rating:', item[3]

        id_local = int(item[0])

    print 'Genres for the film id:', genres_out

def create_matrix(cur):

    # index genre_id -> row_id
    genre_to_row=dict()
    cur.execute('''SELECT Genre.id FROM Genre''')

    for row_id, genre in enumerate(cur):
        genre_to_row[genre[0]]=row_id

    # index film_id -> col_id
    film_to_col=dict()
    cur.execute('''SELECT Movie.id FROM Movie WHERE Movie.name NOT LIKE ?''', ('%' + quest + '%',))

    for col_id, id in enumerate(cur):
        film_to_col[id[0]]=col_id

    #print film_to_col
    #print genre_to_row

    #print 'Films columns:', len(film_to_col)
    #print 'Genres rows', len(genre_to_row)

    matrix_film_genre = lil_matrix((len(genre_to_row), len(film_to_col)))

    cur.execute('''SELECT Movie.id, Genre.id
        FROM Movie JOIN Connection JOIN Genre
        ON Connection.movie_id = Movie.id AND Connection.genre_id = Genre.id''')

    for id, genre in cur:
        row_id=genre_to_row.get(genre)
        col_id=film_to_col.get(id)
        #print row_id, col_id, name, genre
        if row_id is not None and col_id is not None:
            matrix_film_genre[row_id, col_id] = 1

    return matrix_film_genre, genre_to_row, film_to_col
def create_vector(genre_dict, genre_to_row):

    user_vector = lil_matrix((1, len(genre_dict)))

    for item in genre_dict:
        col_name=genre_to_row[item]
        user_vector[0 ,col_name]=genre_dict[item]
    return user_vector

def main():

    conn = sqlite3.connect('movies.sqlite')
    conn.text_factory = str
    cur = conn.cursor()

    try:
        db_request_no_params(cur, 'get genre')
        print ('Database connected!')
    except:
        print 'Creating the database...'
        database_create(cur)

    conn.commit()

    # Input
    quest = raw_input('Please select the movie to find:')
    if len(quest) < 1:
        print 'Sorry, empty input'
        exit()

    # Checking the input
    #quest=input_check(quest)

    # Searching
    genre_dict = genre_dict_empty(cur)
    search_result = db_request_find_film(cur, quest)

    if len(search_result) < 1:
        print 'Your film is not in the database, sorry'
        exit()

    print_result(search_result, genre_dict)

    #print 'All found genres :', genre_dict, '\n'  'Length:', len(genre_dict)
    print'\nCombined genre - based recommendations:\n'
    recommendation_results = recommender(quest, cur, genre_dict)

    for rec in recommendation_results:

        cur.execute('''SELECT Movie.id, Movie.name, Movie.year, Movie.rating, Genre.id, Genre.genre
            FROM Movie JOIN Connection JOIN Genre
            ON Connection.movie_id = Movie.id AND Connection.genre_id = Genre.id
            WHERE Movie.id LIKE ?''', (rec,))
        recom_out = cur.fetchall()

        print_result(recom_out, genre_dict)

    #print 'All found genres :', genre_dict, '\n'  'Length:', len(genre_dict)

    conn.close()

if __name__ == '__main__':
    main()