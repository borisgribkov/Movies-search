import numpy as np
from scipy.sparse import lil_matrix

def create_matrix(cur ,quest):

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


def recommender(quest, cur, genre_dict):

    matrix_film_genre, genre_to_row, film_to_col=create_matrix(cur, quest)

    #percent = float(matrix_film_genre.nnz) / len(film_to_col) / len(genre_to_row) * 100
    #print 'Matrix film-genre filling: %.2f%%' % percent

    user_vector=create_vector(genre_dict, genre_to_row)

    #print 'User vector', user_vector
    #percent_user = float(user_vector.nnz) / len(genre_to_row) * 100
    #print 'User-vector filling: %.2f%%' % percent_user, '\n'

    #print 'Matrix shape', matrix_film_genre.shape
    #print 'Vector shape', user_vector.shape

    final = user_vector.dot(matrix_film_genre).tolil()
    final = final.tocsr()

    #print 'Final result shape', final.shape

    # -------------Output----------

    sorting_length=5 # Recommendations number
    sort_ind=np.argsort(final.data)[-sorting_length:][::-1] # Data Sorting

    rec_result=list()

    recom_to_film=dict()
    for key in film_to_col:
        recom_to_film[film_to_col[key]]=key

    for i in sort_ind:
        #print 'Film - column index (NOT FILM INDEX!!!)', final.indices[i],'Recommendation coefficient', final.data[i]
        rec_result.append(recom_to_film[final.indices[i]])
    #print 'List of recommended movies:', rec_result

    return rec_result



