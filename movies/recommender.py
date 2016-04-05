import numpy as np
from scipy.sparse import lil_matrix

from . import db


def create_matrix(cur, quest):

    # index genre_id -> row_id
    genre_to_row = dict()
    db.get_genres(cur)

    for row_id, genre_id in enumerate(cur):
        genre_to_row[genre_id[0]] = row_id

    # index film_id -> col_id
    film_to_col = dict()
    db.movies_for_film_col(cur, quest)

    for col_id, movie_id in enumerate(cur):
        film_to_col[movie_id[0]] = col_id

    # print film_to_col
    # print genre_to_row

    # print 'Films columns:', len(film_to_col)
    # print 'Genres rows', len(genre_to_row)

    matrix_film_genre = lil_matrix((len(genre_to_row), len(film_to_col)))

    db.film_genre_for_matrix(cur)

    for mov_id, gen_id in cur:
        row_id = genre_to_row.get(gen_id)
        col_id = film_to_col.get(mov_id)
        # print row_id, col_id, name, genre
        if row_id is not None and col_id is not None:
            matrix_film_genre[row_id, col_id] = 1

    return matrix_film_genre, genre_to_row, film_to_col


def create_vector(genre_dict, genre_to_row):

    user_vector = lil_matrix((1, len(genre_dict)))

    for item in genre_dict:
        col_name = genre_to_row[item]
        user_vector[0, col_name] = genre_dict[item]
    return user_vector


def recommender(quest, cur, genre_dict):

    # ------ Building recommendations: (user vector) * (film genre matrix)

    matrix_film_genre, genre_to_row, film_to_col = create_matrix(cur, quest)

    percent_matrix = float(matrix_film_genre.nnz) / len(film_to_col) / len(genre_to_row) * 100
    print 'Matrix film - genre filling: %.2f%%' % percent_matrix

    user_vector = create_vector(genre_dict, genre_to_row)
    # print 'User vector', user_vector

    percent_user = float(user_vector.nnz) / len(genre_to_row) * 100
    print 'User - vector filling: %.2f%%' % percent_user, '\n'

    # print 'Matrix shape', matrix_film_genre.shape
    # print 'Vector shape', user_vector.shape

    # Multiplication of user-vector and film-genre matrix = recommendation results
    recommendations_vector = user_vector.dot(matrix_film_genre).tolil()
    recommendations_vector = recommendations_vector.tocsr()
    # print 'Final result shape', final.shape

    # -------------Output----------

    sorting_length = 5  # Number of the recommended movies
    sorted_ind = np.argsort(recommendations_vector.data)[-sorting_length:][::-1]  # Sorting to select top recommendations

    recommendations_result = list()
    recommendations_to_film = dict()

    for film_num in film_to_col:
        recommendations_to_film[film_to_col[film_num]] = film_num

    for index in sorted_ind:

        # print 'Film - column index (NOT FILM INDEX!!!)', final.indices[i],'Recommendation coefficient', final.data[i]
        recommendations_result.append(recommendations_to_film[recommendations_vector.indices[index]])
    # print 'List of recommended movies:', rec_result

    return recommendations_result
