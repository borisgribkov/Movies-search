def db_request_no_params(cur, request):

    if request == 'create_table':
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

    if request == 'get genre':
        cur.execute('''SELECT Genre.id FROM Genre''')
        request_genre = cur.fetchall()
        return request_genre


def db_request_insert_data(cur, name, year, rating):
    cur.execute('INSERT INTO Movie (name, year, rating) VALUES (?, ?, ?)', (name, year, rating))


def db_request_select_movie_id(cur, name):
    cur.execute('SELECT id FROM Movie WHERE name = ? ', (name, ))
    movie_id = cur.fetchone()[0]
    return movie_id


def db_request_insert_genre(cur, genre):
    cur.execute('INSERT OR IGNORE INTO Genre (genre) VALUES (?)', (genre,))


def db_request_select_genre_id(cur, genre):
    cur.execute('SELECT id FROM Genre WHERE genre = ? ', (genre, ))
    genre_id = cur.fetchone()[0]
    return genre_id


def db_request_create_connection(cur, movie_id, genre_id):
    cur.execute('INSERT OR REPLACE INTO Connection (movie_id, genre_id) VALUES (?,?)', (movie_id, genre_id))


def db_request_find_film(cur, quest):
    cur.execute('''SELECT Movie.id, Movie.name, Movie.year, Movie.rating, Genre.id, Genre.genre
        FROM Movie JOIN Connection JOIN Genre
        ON Connection.movie_id = Movie.id AND Connection.genre_id = Genre.id
        WHERE Movie.name LIKE ? ORDER BY Movie.rating DESC''', ('%' + quest + '%',))
    request = cur.fetchall()
    return request
