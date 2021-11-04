# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 09:51:21 2021

@author: SImplon.co
"""

# Import libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

# Defining directory name for csv creation
dir_name = './data'

# Defining headers for fetching movies in english
headers = {"Accept-Language": "en-US,en;q=0.5"}

def imdb_fetch():
    # Define header language for getting data in english
    # headers = {"Accept-Language": "en-US,en;q=0.5"}
    
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
            
        # CHange starting page for the request        
        page += 50
        
    return movies_data    

def create_imdb_dataframe(data):
    imdb_data = data
    # Create dataframe from movies_data list
    movies_df = pd.DataFrame (imdb_data, columns = ['title', 'year_of_release', 'duration_in_minutes', 'genre'])
    
    # Keep only useful characters and change type of duration_in_minutes
    movies_df["duration_in_minutes"] = movies_df["duration_in_minutes"].str[:3].astype(int)
    movies_df["year_of_release"] = movies_df["year_of_release"].str[1:5]
    
    # Check if dir_name already exists before creating csv file
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        print("Directory " , dir_name ,  " Created ")
    else:    
        print("Directory " , dir_name ,  " already exists")
        
    # Export the dataframe with to_csv()    
    movies_df.to_csv(f'{dir_name}/top_250_imdb_eng_scraper_module.csv', encoding='utf-8', index=False)
    
    return movies_df

def rotten_scores_fetch(imdb_dataframe):
    # Define empty list
    score_data = []

    # Define header language for getting data in english
    headers = {"Accept-Language": "en-US,en;q=0.5"}
    
    # Define static part of the url
    uri = 'https://www.rottentomatoes.com/m/'
    
    # Loop through titles in the dataframe
    for title in imdb_dataframe['title']:
        changed_title = title.replace(" ", "_").replace("The_", "").replace(":", "").replace(".", "").replace("'", "").replace("-", "").replace(",", "").replace("ä", "").replace("__","_")   
        url = f'{uri}{changed_title}'
        data = requests.get(url, headers=headers)
        
        if data.status_code == 404:
            score_list = ['not found', 'not_found']
            score_data.append(score_list)
    
        else:
            soup = BeautifulSoup(data.text, 'html.parser')
    
            audience_score = soup.find("score-board")["audiencescore"]
            tomato_score = soup.find("score-board")["tomatometerscore"]
    
            score_list = [tomato_score, audience_score]
    
            score_data.append(score_list)
            
    return score_data

def create_rotten_df(score_data, imdb_dataframe):
    # Store imdb_dataframe in final_df
    final_df = imdb_dataframe
    
    # Create score_df with score_data from previous function
    score_df = pd.DataFrame(score_data, columns = ['tomato_meter','audience_score'])
    
    # Create new columns in our final dataframe
    final_df['tomato_meter'] = score_df['tomato_meter']
    final_df['audience_score'] = score_df['audience_score']
    
    # Check if dir_name already exists before creating csv file
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        print("Directory " , dir_name ,  " Created ")
    else:    
        print("Directory " , dir_name ,  " already exists")
        
    # Export the dataframe with to_csv()    
    final_df.to_csv(f'{dir_name}/top_250_imdb_with_rottenscore.csv', encoding='utf-8', index=False)

    return final_df            