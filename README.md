# Movies-search

Looking through the movies database

The source files have been taken from : http://files.grouplens.org/datasets/movielens/ml-10m-README.html University of Minnesota or the GroupLens Research Group.

The key ideas are (step by step): 

1) Calculating the rating for the each movie using 300MB Ratings file, which contains user's ratings for each movie.
2) Parsing the Movies.dat file and adding everything (title, year, rating, id) into the Database using SQL. 
3) User request input and checking it using Eng_US dictionary (import enchant).
4) Finally, searching the user input the database using SQL requests.


---------------------------

Ver_2 has released.

Updades comparing to the previous version:
1) Database creation occurs only at the first launch, after The code only reads it.
2) Database with many-to-many relationships containing Movies table, Genres table and Connection table
3) The code has been re-builded and some functions have been added.

4) Recommendation system has included which takes into account movie's genres. 
   Recommendations ensures creation of input vector (genre vector), movie-genre matrix, vector-matrix multiplication and sorting.
   Everything using NumPy and SciPy
