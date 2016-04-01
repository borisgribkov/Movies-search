from db_request import (db_request_no_params, db_request_insert_data, db_request_select_movie_id,
                        db_request_insert_genre, db_request_select_genre_id, db_request_create_connection)


def average(rating, count):

    for film_id in rating:
        rating[film_id] = rating[film_id]/count[film_id]
        rating[film_id] = "%.3f" % rating[film_id]

    return rating


def rating_count():

    movies_rating = open('ratings.dat')

    rating = dict()
    count = dict()

    for item in movies_rating:
        movie_rating = item.rstrip().split('::')

        film_id = movie_rating[1]
        film_rating = float(movie_rating[2])

        count[film_id] = count.get(film_id, 0)+1
        rating[film_id] = rating.get(film_id, 0)+film_rating

    rating = average(rating, count)

    movies_rating.close()

    return rating


def database_create(cur):

    data_movies = open('movies.dat')

    db_request_no_params(cur, 'create_table')

    movies_rating = rating_count()

    for movie in data_movies:

        movie_search = movie.rstrip().split('::')

        movie_id = movie_search[0]
        name_year = movie_search[1]

        year = name_year[len(name_year)-5:len(name_year)-1]
        name = name_year[:len(name_year)-7]

        genres_list = movie_search[2].split('|')

        try:
            rating = movies_rating[movie_id]
        except: rating = 0

        db_request_insert_data(cur, name, year, rating)
        movie_id = db_request_select_movie_id(cur, name)

        for genre in genres_list:

            db_request_insert_genre(cur, genre)
            genre_id = db_request_select_genre_id(cur, genre)
            db_request_create_connection(cur, movie_id, genre_id)

    data_movies.close()
