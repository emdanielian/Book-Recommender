import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image
import math

# SECTION 0: BASIC STREAMLIT APPEARANCE

# displays banner image of books
st.image('https://www.mainejewish.org/wp-content/uploads/2017/07/Books-Banner.jpg')

# title of streamlit page
st.title('Book Recommender')

# SECTION 1: LOADING DATA

# load/read the two datasets
goodreads = pd.read_csv('goodreads_books.csv')
categories = pd.read_csv('categories_books.csv')


# SECTION 2: DATA CLEANING 

# renaming the isbn column in "goodreads" to isbn 10 so that its consistent with what's in "categories"
goodreads.rename(columns = {'isbn':'isbn10'}, inplace = True)

# seeing if there are any missing values in the unique ID (isbn10) column
# both isbn 10 and 13 could be used to merge the datasets, both are accepted versions of isbn
# however, isbn 13 is a newer system than isbn 10 - still I will merge on isbn10 because its less digits
null_g = goodreads['isbn10'].isnull().sum()
null_c = categories['isbn10'].isnull().sum()
# null_g, null_c

# altogether I am eliminating isbn13 because the datasets have different datatypes for this col
# and we already have isbn10 so having both isn't necessary
del categories['isbn13']
del goodreads['isbn13']

# before we merge I'm eliminating the authors, title, average_rating, num_pages, published_year, and ratings_count 
# columns from "categories" because that information is repeated in "goodreads"
# kaggle community upvoted "goodreads" more so I'm going to accept its values over the categories values
# also, both datasets are equally as old, so one isn't preferred over the other for that reason
del categories['authors']
del categories['title']
del categories['average_rating']
del categories['num_pages']
del categories['published_year']
del categories['ratings_count']

# this ID is only unique to one dataset so it won't be of use
del goodreads['bookID']

# merging the two datasets on isbn10
# according to Kaggle documentation, "categories" got its isbns from "goodreads" so the values should be consistent
all_books = pd.merge(goodreads, categories, how="inner", on=["isbn10"])

# correcting datatypes for columns in merged data
all_books['average_rating'] = all_books['average_rating'].astype(float)
all_books['ratings_count'] = all_books['ratings_count'].astype(int)
all_books['num_pages'] = all_books['  num_pages'].astype(int)
all_books['categories'] = all_books['categories'].astype(str)

# SECTION 3: GROUPING SIMILAR GENRES

# A lot of the genres are similar, but just spelled/capitalized differently
# So lets map some similar values onto the original data
similar_genre = {'BIOGRAPHY & AUTOBIOGRAPHY': 'Biography & Autobiography', \
                'Political science': 'Political Science', \
                'Political leadership': 'Political Science',\
                'Political fiction': 'Political Science', \
                'Literary Criticism & Collections': 'Literary Criticism', \
                'LITERARY CRITICISM' : 'Literary Criticism', \
                'JUVENILE FICTION' : 'Juvenile Fiction', \
                'Humorous stories, American': 'Humor', \
                'Humorous stories' : 'Humor', \
                'Humorous stories, English': 'Humor', \
                'Humorous fiction': 'Humor', \
                'Comedy' : 'Humor', \
                'Detective and mystery stories, American': 'Detective and mystery stories', \
                'Detective and mystery stories, English' : 'Detective and mystery stories'
                }
# I could spend a lot of time grouping the genres, but that would take a while so I only did a few
# Automating this process would be lengthy and complicated - like do you sort "humorous fiction" with "fiction" or "humor"?

# actually replacing mapped valude in the allbooks genre column
all_books['categories'] = all_books['categories'].replace(similar_genre)


# SECTION 4: ELIMINATING INFREQUENT GENRES

# initializing the dictionary
frequency = {}

# creating a categories list based on just the categories genre in all_books
cate_list = all_books['categories']

# this fills a dictionary with all the genres (key) and how many times they appear (value)
# iterating over the list
for item in cate_list:
   # checking the element in dictionary
   if item in frequency:
      # incrementing the count
      frequency[item] += 1
   else:
      # initializing the count
      frequency[item] = 1

# makes a new frequency column that shows the frequency of each genre of each book
all_books['genre_frequency']= all_books['categories'].map(frequency)

# lets eliminate genres with less than or equal to 5 books so the reader can have a digestible list of genres
# otherwise there are a TON of genres the user would have to sift through (many of which are repeats of similar genres)
all_books = all_books[all_books['genre_frequency'] >= 5]

# lets also eliminate all books with no genre
all_books = all_books[all_books['categories'] != 'nan']
# great, now we have a list of books from relatively "popular" genres

# makes a list of all genres (or categories) in dataset
genre_list = []
for category in all_books['categories']:
    if category not in genre_list:
        genre_list.append(category)

# alphebetizes the genre list
genre_list = sorted(genre_list)
# we'll use this list later when displaying all the genres for the reader to select


# SECTION 5: BAYESIAN AVERAGE FOR REVIEWS

# so I want to create a "average" rating that weighs both the average rating on goodreads and the # of reviews
# this is so that books with 1 5-star rating don't get ranked higher in my recommender than books with 100 4-star ratings

# I used the bayesian average weighting method for weighing both average review with number of reviews
# the formula was taken from the following source
# https://www.algolia.com/doc/guides/solutions/ecommerce/relevance-optimization/tutorials/bayesian-average/

# c is a confidence measure, the document used 100 for simplicity
# I followed their suggested approach  to make c the 25th percentile rating count (which is about 184)
C = all_books['ratings_count'].quantile(q=0.25)

# m is the arithmetic average rating of all products
m = all_books['average_rating'].mean()

# bayes average for a book = [(average rating * ratings count) + (C*m)]/ [ratings count + C]
# defining a new column with this average
all_books['bayes_average'] = (all_books['average_rating'] * all_books['ratings_count'] + C*m) / (all_books['ratings_count'] + C)
# this average is ONLY used internally to determine the rank of the books displayed to the reader
# this is NOT the star rating displayed to the user


# SECTION 6: GENERAL FUNCTION FOR NARROWING & DISPLAYING DATA
# this function is called in section 7

# we use this later for the star display - it rounds ratings to the nearest full star
all_books['rounded_rating'] = all_books['average_rating'].round()

# creates a function that narrows down data based on page # & displays book info
# it accepts a dataset either narrowed by genre or author, and the author/genre the user selected
def narrowed_general(narrowed_set, user_input):

    # NARROWING

    # narrows data based on "pages" or the book length the user is willing to read
    if pages == '<300':
        narrowed_pages = narrowed_set[narrowed_set['num_pages'] < 300]
    elif pages == '300-499':
        narrowed_pages = narrowed_set[(300 <= narrowed_set['num_pages'])  & (narrowed_set['num_pages'] <= 499)]
    elif pages == '500+':
        narrowed_pages = narrowed_set[500 <= narrowed_set['num_pages']]

    # this ranks the dataset based on our bayes average from earlier - so books with higher bayes average are higher up
    # it also narrows dataset based on how many recommendations the user wants
    displayed_df = narrowed_pages.sort_values(['bayes_average'], ascending=[False]).head(number_rec)

    # DISPLAYING

    # function that displays an image to user
    # accepts "column" (the name of a column, in our case the thumbnail column)
    # it uses the index of the book in question to identify the image/thumbnail of that book
    def display_image_to_user(column):
        # if theres no image available, do nothing
        if str(displayed_df[column][ind]) == 'nan':
            pass
        # if there is an image available, display the image
        else:
            st.image(displayed_df[column][ind])

    # function that displays text to the user
    # accepts "bolded" (label you want for the text displayed) and "column" (the name of a column)
    def display_text_to_user(bolded, column):
        # if theres no value available, do nothing
        if str(displayed_df[column][ind]) == 'nan':
            pass
        # if there is, display the text
        else:
            st.write("**" + bolded + ":**",str(displayed_df[column][ind]))

    # initializing a counter to show what # recommendation is shown (like if its recommendation #2 or #5)
    count = 0

    # if the user hasn't selected an author or genre yet, display nothing
    if user_input == "":
        pass
    # otherwise go ahead and show all the book info
    else: 
        for ind in displayed_df.index:
            count = count + 1
            # shows what number recommendation it is
            st.subheader("Book #" + str(count))
            # shows the book cover
            display_image_to_user('thumbnail')
            # shows the rating of the book (in visualized stars!)
            st.markdown("⭐" * int(displayed_df['rounded_rating'][ind]))
            # shows the name of the book and the author
            st.write("**Recommendation:** ", displayed_df['title'][ind], 'by ', displayed_df['authors'][ind])
            # shows the description of the book, but the user has to expand the description to see it (some are very long!)
            with st.expander("See Description"):
                if str(displayed_df['description'][ind]) == 'nan':
                    pass
                else:
                    st.write(str(displayed_df['description'][ind]))
            # shows the genre of the book
            display_text_to_user('Genre', 'categories')
            # shows how many pages the book is
            display_text_to_user('Page count', 'num_pages')
            # shows the ISBN of the book
            display_text_to_user('ISBN 10', 'isbn10')

# SECTION 7: SPECIFIC FUNCTION FOR NARROWING & DISPLAYING DATA BY AUTHOR/GENRE

# asks the user to select whether they want recommendations by author or genre
author_or_genre = st.sidebar.selectbox('Do you want to get book recommendations by author or genre?', (' ', 'Author', 'Genre'))

# if the user selects that they want recommendations by author, do the following
if author_or_genre == 'Author':
    # accepts user input for an author 
    author = st.sidebar.text_input('Author')

    # suggestion if there is no author typed in
    if author == "":
        st.subheader("Fill in the author on the right to get a recommendation!")
    # if there is an author typed in, do nothing
    else:
        pass

    # accepts user input for a page range
    pages = st.sidebar.selectbox('Page number', ('<300', '300-499', '500+'))

    # accepts user input for how many books the reader wants suggested
    number_rec = st.sidebar.number_input('Number of book recommendations', min_value = 0, max_value = 1000)

    # narrowing the dataframe based on what author the user wants
    narrowed_author = all_books[all_books['authors'].str.contains(author, case=False, na=False)]

    # feeds this narrowed dataframe, and the user-selected author into the narrowed_general function from section 6
    narrowed_general(narrowed_author, author)
        
# if the user selects that they want recommendations by genre, do the following
elif author_or_genre == 'Genre':
    # accepts user input for a genre
    genre = st.sidebar.selectbox('Genre', genre_list)

    # accepts user input for a page range
    pages = st.sidebar.selectbox('Page number', ('<300', '300-499', '500+'))

    # accepts user input for how many books the reader wants suggested
    number_rec = st.sidebar.number_input('Number of book recommendations', min_value = 0, max_value = 1000)

    # narrowing the dataframe based on what genre the user wants
    narrowed_genre = all_books[all_books['categories'] == genre]

    # feeds this narrowed dataframe, and the user-selected genre into the narrowed_general function from section 6
    narrowed_general(narrowed_genre, genre)

# if the user hasn't selected how they want their recommendations, ask them to fill in that info.
elif author_or_genre == ' ':
    st.subheader("Fill in blanks on the right to get a recommendation!")
