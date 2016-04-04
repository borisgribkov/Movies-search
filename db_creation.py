import urllib
import zipfile


from db_request import (create_table, insert_data, select_movie_id,
                        insert_genre, select_genre_id, create_connection)


def open_file(file_name):

    try:
        data = open('ml-10M100K/'+file_name)

    except:

        print 'Please copy ', file_name,' into the project folder or download it from MovieLens'
        download_start = raw_input('Start download? Press Y to start')

        if download_start == 'y':

            urllib.urlretrieve('http://files.grouplens.org/datasets/movielens/ml-10m.zip', 'ml-10m.zip')

            zip_file = zipfile.ZipFile('ml-10m.zip')
            zip_file.extractall()

            data = open('ml-10M100K/'+file_name)

        else:
            quit()

    return data


def average(rating, count):

    for film_id in rating:
        rating[film_id] = rating[film_id]/count[film_id]
        rating[film_id] = "%.3f" % rating[film_id]

    return rating


def rating_count():

    movies_rating = open_file('ratings.dat')

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

    data_movies = open_file('movies.dat')

    create_table(cur)

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

        insert_data(cur, name, year, rating)
        movie_id = select_movie_id(cur, name)

        for genre in genres_list:

            insert_genre(cur, genre)
            genre_id = select_genre_id(cur, genre)
            create_connection(cur, movie_id, genre_id)

    data_movies.close()
