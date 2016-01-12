import re
import enchant 
import sqlite3

d = enchant.Dict("en_US")
datamovies = open('movies.dat')
ratingmovies = open('ratings.dat')

#Creating the database table

conn = sqlite3.connect('movies.sqlite')
conn.text_factory = str
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Movies')

cur.execute('CREATE TABLE Movies (Name TEXT, Year TEXT, Genre TEXT, Rating FLOAT)')

#Rating calculation from rating file

print 'Calculating the rating of the movies...'
rating=dict()
ratcount=dict()
  
for rat in ratingmovies:
         
    rat=rat.rstrip()
    movie_rat=rat.split('::')
        
    id_count=movie_rat[1]
    rat_count=float(movie_rat[2])
    
    ratcount[id_count]=ratcount.get(id_count,0)+1    
    rating[id_count]=rating.get(id_count,0)+rat_count
    
for rat1 in rating:
    rating[rat1]=rating[rat1]/ratcount[rat1]
    rating[rat1]= "%.3f" % rating[rat1]

print 'Creating the database...'     
 
#Parsing the movies file
        
movie_search=list()

for movie in datamovies:
    movie=movie.rstrip()
    movie_search=movie.split('::')
    
    name=movie_search[1]
    movie_id=movie_search[0]
    year=name[len(name)-5:len(name)-1]
    name=name[:len(name)-7]
    genre=movie_search[2]
    try: rating_t=rating[movie_id]
    except: rating_t=0
       
    #print 'Movie:', name, '|| Year:', year, '|| Genre:', movie_search[2], '|| Rating', rating[movie_id]
    cur.execute('INSERT INTO Movies (Name, Year, Genre, Rating) VALUES (?, ?, ?, ?)', 
    (name, year, genre, rating_t))
    
conn.commit()

#Input

quest = raw_input('Please select the movie to find:')
if len(quest)<1:
    print ('Sorry, empty input')
    exit()
    
#Checking the input
    
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

#Searching 
    
request = cur.execute("SELECT * FROM Movies WHERE Name LIKE ? ORDER BY Rating DESC", ('%' + quest + '%',)) 

request = cur.fetchall()
if len(request) <1:
    print 'Your film is not in the database, sorry'
    exit()

for item in request:
    print item[0], '||', item[1], '||', item[2], '|| Rating:', item[3]
    name_s=item[0]
    genre_s=item[2]
    rating_s=item[3]
    
    #print 'Movies with the similar rating:'
    #request_s = cur.execute("SELECT * FROM Movies WHERE Rating>=? AND Name!=? ORDER BY Rating LIMIT 5", (rating_s, name_s)) 
  
    print 'Similar genre, top 5 in rating:'
    request_s = cur.execute("SELECT * FROM Movies WHERE Genre LIKE ? AND Name!=? ORDER BY Rating DESC LIMIT 5", (genre_s, name_s)) 
        
    print '-----'
    for item_s in request_s:
         print '     ', item_s[0],'||', item_s[1],'||', item_s[2],'|| Rating:', item_s[3]
    print '-----'

conn.close()    
