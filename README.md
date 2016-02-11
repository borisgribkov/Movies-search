# Movies-search

Looking through the movies database

The source files have been taken from : http://files.grouplens.org/datasets/movielens/ml-10m-README.html University of Minnesota or the GroupLens Research Group.

The key ideas are (step by step): 

1) Calculating the rating for the each movie using 300MB Ratings file, which contains user's ratings for each movie.
2) Parsing the Movies.dat file and adding everything (title, year, rating, id) into the Database using SQL. 
3) User request input and checking it using Eng_US dictionary (import enchant).
4) Finally, searching the user input the database using SQL requests.
