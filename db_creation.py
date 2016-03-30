from db_request import db_request_no_params
from db_request import db_request_insert_data
from db_request import db_request_select_movie_id
from db_request import db_request_insert_genre
from db_request import db_request_select_genre_id
from db_request import db_request_create_connection


def average(rating, count):

    for film_id in rating:
        rating[film_id]=rating[film_id]/count[film_id]
        rating[film_id]= "%.3f" % rating[film_id]

    return rating

def rating_count():

    movies_rating = open('ratings.dat')

    rating=dict()
    count=dict()

    for item in movies_rating:
        movie_rating=item.rstrip().split('::')

        film_id=movie_rating[1]
        film_rating=float(movie_rating[2])

        count[film_id]=count.get(film_id,0)+1
        rating[film_id]=rating.get(film_id,0)+film_rating

    rating = average(rating, count)

    movies_rating.close()

    return rating

def database_create(cur):

    datamovies = open('movies.dat')

    db_request_no_params(cur, 'create_table')

    movies_rating = rating_count()

    for movie in datamovies:

        movie_search=movie.rstrip().split('::')

        movie_id = movie_search[0]
        name_year = movie_search[1]

        year = name_year[len(name_year)-5:len(name_year)-1]
        name = name_year[:len(name_year)-7]

        genres_list = movie_search[2].split('|')

        try: rating = movies_rating[movie_id]
        except: rating = 0

        db_request_insert_data(cur, name, year, rating)
        #cur.execute('INSERT INTO Movie (name, year, rating) VALUES (?, ?, ?)',
        #(name, year, rating))

        movie_id = db_request_select_movie_id(cur, name)
        #cur.execute('SELECT id FROM Movie WHERE name = ? ', (name, ))
        #movie_id = cur.fetchone()[0]


        for genre in genres_list:

            db_request_insert_genre(cur, genre)
            #cur.execute('INSERT OR IGNORE INTO Genre (genre) VALUES (?)',(genre,))

            genre_id = db_request_select_genre_id(cur, genre)
            #cur.execute('SELECT id FROM Genre WHERE genre = ? ', (genre, ))
            #genre_id = cur.fetchone()[0]

            db_request_create_connection(cur, movie_id, genre_id)
            #cur.execute('INSERT OR REPLACE INTO Connection (movie_id, genre_id) VALUES (?,?)',
            #(movie_id, genre_id))

    datamovies.close()