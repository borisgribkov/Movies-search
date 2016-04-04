# Movies search

This project deals with searching for the movies in the open access [GroupLens](http://grouplens.org/) Database. Besides the search results this code utilizes movie genre - based recommendation scheme to suggest five more movies to look at. Info about each movie contains: title, year, user's rating and genres.

## Installation

Create and activate virtual environment::

    $ virtualenv venv

Install Python requirements::

    $ pip install -r requirements.txt

## Usage

    $ python -m movies

On the first run the program automatically download required data files and setup database.


## The functionality of the code is described below

Movies searching is based on the **SQLlite** database created during the first launch. To create it 'ratings.dat' and 'movies.dat' should be located in the project folder, please copy it or you will be asked to download it automatically. First file contains user's ratings and used to calculate the average rating, second file contains information about movie's title, year and genres. 

After database creation (it occurs only at the first launch) it's ready for the movies searching, this step contains some features like checking the user input with Eng_US dictionary (*import Enchant Py library*) and giving suggestions in case of incorrect input.

The final output includes not only direct searching results, but also **top-5** genre based recommended movies. 

## Recommendation scheme

To build recommendations it collects the number of the each found genre in the search results and creates **user genre-vector**. 
For example, if you have two *Action* movies and one *Comedy*, user vector contains 2 for *Action*, 1 for *Comedy* and 0 value for the other genres.

This **user genre vector** is multiplied  by the sparse **movie-genre matrix** (its dimensions: number of movies x genres number, in the our case it's about 10K x 20, filling about 10%, matirx filling: 1 - movie mathes with the genre, 0 - no match). Maximum multiplication result means best match between the searching results and the movies to recommend, top-5 movies are selected for the output. This recommenation scheme uses *NumPy and SciPy operations*, please note this.

You are welcome to use this searching tool, any comments and suggestions are always welcome. 

Thank you! 
