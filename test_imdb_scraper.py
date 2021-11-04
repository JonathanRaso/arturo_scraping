# Import libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd

# Define header language for getting data in english
headers = {"Accept-Language": "en-US,en;q=0.5"}

# Create a list for later use (adding each movie data into this list)
movies_data = []

# Starting page
page = 1

# Looping through the five page of top 250 movies
while page <= 250:
    url = f'https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start={page}'

    # Getting data from imdb url
    data = requests.get(url, headers=headers)

    # Add html data to BeautifulSoup
    soup =  BeautifulSoup(data.text, 'html.parser')

    # Loop through each div with the content that we need (class = 'lister-item-content')
    for div in soup.find_all('div', { 'class' : 'lister-item-content' }):
        # Get movie's title and keep only the text
        title = div.find('a')
        title_text = title.text
        # Get movies's year and keep only the text
        year = div.find("span", class_="lister-item-year").text
        # Get movies's runtime and keep only the text
        runtime = div.find('span', {'class':'runtime'}).text
        # Get movies's genre and keep only the text
        genre = div.find('span', {'class':'genre'}).text.strip()

        # Add data of each movie in a list
        data_list = [title_text, year, runtime, genre]

        # Add all these data into a movies_data list
        movies_data.append(data_list)
            
    page += 50


# Create dataframe from movies_data list
movies_df = pd.DataFrame (movies_data, columns = ['title', 'year_of_release', 'duration_in_minutes', 'genre'])

# Keep only useful characters and change type of duration_in_minutes
movies_df["duration_in_minutes"] = movies_df["duration_in_minutes"].str[:3].astype(int)
movies_df["year_of_release"] = movies_df["year_of_release"].str[1:5]

# Export the dataframe with to_csv() 
movies_df.to_csv('data/top_250_imdb_eng_scraper.csv', encoding='utf-8', index=False)