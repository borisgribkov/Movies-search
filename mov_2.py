from scipy.sparse import lil_matrix
#import enchant
import numpy as np
import sqlite3

def average_c(dict_input, count):
   for i in dict_input:
        dict_input[i]=dict_input[i]/count[i]
        dict_input[i]= "%.3f" % dict_input[i]
   return dict_input

def rating_count():

    ratingmovies = open('ratings.dat')

    rating=dict()
    count=dict()

    for i in ratingmovies:
        i=i.rstrip()
        movie_rat=i.split('::')

        id_count=movie_rat[1]
        rat_count=float(movie_rat[2])

        count[id_count]=count.get(id_count,0)+1
        rating[id_count]=rating.get(id_count,0)+rat_count

    rating = average_c(rating, count)

    return rating

def input_check(quest):

    qcheck=d.check(quest)
    if qcheck is False:
        print 'Not sure that your input is correct:', quest
        quest_old=quest
        quest=d.suggest(quest)
        print 'Suggested input instead:'
        print quest, 'Number of suggestions 1 -' ,len(quest)
        num = raw_input('Please choose the word from the list, to continue search with the initial word input 0:  ')

        try:
            num=int(num)
        except:
            print 'Incorrect input, exit!'
            exit()

        if num>0:
            quest=quest[num-1]
        else:
            quest=quest_old

        print 'Looking for:', quest
    else:
        print 'Checking the input... done!'

    return quest

def database_create():

    datamovies = open('movies.dat')

    cur.executescript('''
    DROP TABLE IF EXISTS Movie;
    DROP TABLE IF EXISTS Genre;
    DROP TABLE IF EXISTS Connection;
    CREATE TABLE Movie (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name   TEXT,
        year   TEXT,
        rating FLOAT
    );
    CREATE TABLE Genre (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        genre  TEXT UNIQUE
    );
    CREATE TABLE Connection (
        movie_id   INTEGER,
        genre_id   INTEGER,
        PRIMARY KEY (movie_id, genre_id)
    );
    ''')

    #cur.execute('DROP TABLE IF EXISTS Movies_all_data')
    #cur.execute('CREATE TABLE Movies_all_data (Name TEXT, Year TEXT, Genre TEXT, Rating FLOAT)')

    rating = rating_count()
    movie_search=list()
    genre_list=list()

    for movie in datamovies:

        movie=movie.rstrip()
        movie_search=movie.split('::')

        name=movie_search[1]
        movie_id=movie_search[0]
        year=name[len(name)-5:len(name)-1]
        name=name[:len(name)-7]
        genre=movie_search[2]
        genre_list=genre.split('|')

        try: rating_t=rating[movie_id]
        except: rating_t=0

        #cur.execute('INSERT INTO Movies_all_data (Name, Year, Genre, Rating) VALUES (?, ?, ?, ?)',
        #(name, year, genre, rating_t))


        cur.execute('INSERT INTO Movie (name, year, rating) VALUES (?, ?, ?)',
        (name, year, rating_t))
        cur.execute('SELECT id FROM Movie WHERE name = ? ', (name, ))
        movie_id = cur.fetchone()[0]

        for genre_item in genre_list:
            cur.execute('INSERT OR IGNORE INTO Genre (genre) VALUES (?)',(genre_item,))
            cur.execute('SELECT id FROM Genre WHERE genre = ? ', (genre_item, ))
            genre_id = cur.fetchone()[0]

            cur.execute('INSERT OR REPLACE INTO Connection (movie_id, genre_id) VALUES (?,?)',
            (movie_id, genre_id))

    out=open('status.done','w')
    out.write('ok')

    return None

def genre_dict_empty(comb_genre,n):

    if n is 0:
        request_genre = cur.execute('''SELECT Genre.id FROM Genre''')
        request_genre = cur.fetchall()

    for item in request_genre:
        comb_genre[item[0]]=comb_genre.get(item[0],0)+n
    return comb_genre

def create_matrix():

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

    for id,genre in cur:
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

def print_result(request):

    global genre_dict
    id_local=None
    genre_out=dict()

    for item in request:

        genre_out[item[0]]=genre_out.get(item[0], '')+item[5]+' '
        genre_dict[item[4]]=genre_dict.get(item[4],0)+1

        if int(item[0]) == id_local:
            continue

        print 'Film id:', item[0], '||', item[1], '|| Year:', item[2], '||  Rating:', item[3]

        id_local = int(item[0])

    print 'Genres for the film id:', genre_out
    return None

#d = enchant.Dict("en_US")

conn = sqlite3.connect('movies.sqlite')
conn.text_factory = str
cur = conn.cursor()

try:
    status=open('status.done')
    status=status.read()

    cur.execute('''SELECT Genre.id FROM Genre''')
    cur.fetchall()

    print ('Database connected!')
except:
    print 'Creating the database...'
    database_create()

conn.commit()

#Input
quest = raw_input('Please select the movie to find:')
if len(quest)<1:
    print ('Sorry, empty input')
    exit()

#Checking the input
#quest=input_check(quest)

#Searching

genre_dict=dict()
genre_dict=genre_dict_empty(genre_dict, 0)

#request = cur.execute("SELECT * FROM Movies_all_data WHERE Name LIKE ? ORDER BY Rating DESC", ('%' + quest + '%',))

request = cur.execute('''SELECT Movie.id, Movie.name, Movie.year, Movie.rating, Genre.id, Genre.genre
    FROM Movie JOIN Connection JOIN Genre
    ON Connection.movie_id = Movie.id AND Connection.genre_id = Genre.id
    WHERE Movie.name LIKE ? ORDER BY Movie.rating DESC''', ('%' + quest + '%',))

request = cur.fetchall()

if len(request) <1:
    print 'Your film is not in the database, sorry'
    exit()

print_result(request)

#print 'All found genres :', genre_dict, '\n'  'Length:', len(genre_dict)

#-------------------------------------------Recommendations scheme-----------------------------------------------

print('\n Combined genre-based recommendations: \n')

matrix_film_genre, genre_to_row, film_to_col=create_matrix()

percent = float(matrix_film_genre.nnz) / len(film_to_col) / len(genre_to_row) * 100
print 'Matrix film-genre filling: %.2f%%' % percent


user_vector=create_vector(genre_dict, genre_to_row)

#print 'User vector', user_vector
percent_user = float(user_vector.nnz) / len(genre_to_row) * 100
print 'User-vector filling: %.2f%%' % percent_user, '\n'

#print 'Matrix shape', matrix_film_genre.shape
#print 'Vector shape', user_vector.shape


final = user_vector.dot(matrix_film_genre).tolil()
final = final.tocsr()

#print 'Final result shape', final.shape

#----------------------------------------------Output-------------------------------------------:

sorting_length=5
sort_ind=np.argsort(final.data)[-sorting_length:][::-1]

rec_result=list()

recom_to_film=dict()
for key in film_to_col:
    recom_to_film[film_to_col[key]]=key

for i in sort_ind:
    #print 'Film column index (NOT FILM INDEX!!!)', final.indices[i],'Recommendation coefficient', final.data[i]
    rec_result.append(recom_to_film[final.indices[i]])
#print 'List of recommended movies:', rec_result

for rec in rec_result:

    cur.execute('''SELECT Movie.id, Movie.name, Movie.year, Movie.rating, Genre.id, Genre.genre
        FROM Movie JOIN Connection JOIN Genre
        ON Connection.movie_id = Movie.id AND Connection.genre_id = Genre.id
        WHERE Movie.id LIKE ?''', (rec,))
    recom_out = cur.fetchall()

    print_result(recom_out)

#print 'All found genres :', genre_dict, '\n'  'Length:', len(genre_dict)

conn.close()