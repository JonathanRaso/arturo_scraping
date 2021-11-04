#%%
import os
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as rq
#%%
def imdb_film_pages_urls():
    # fetching film pages' urls
    pages_urls = []

    page_start = 1
    while page_start <= 250:
        url = f'https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start={page_start}&ref_=adv_nxt'
        pages_urls.append(url)
        page_start = page_start + 50

    return pages_urls

#%%
imdb_urls = imdb_film_pages_urls()
#%%
def imdb_films_content(imdb_urls):
    # parsing html content from request response
    pages_content = []

    # fetch requests in US format
    headers = {"Accept-Language": "en-US,en;q=0.5"}

    for page in imdb_urls:
        response = rq.get(page, headers=headers)
        if response.status_code != 200:
            print("Error fetching page")
        else:
            pages_content.append(response.content)

    return pages_content

#%%
imdb_pages_content = imdb_films_content(imdb_urls)
#%%
def imdb_film_df(imdb_pages_content):
    # collect film needed information
    film_infos = []

    for content in imdb_pages_content:
        soup = bs(content, "html.parser")
        for film_content in soup.find_all("div", class_="lister-item mode-advanced"):
            film_infos.append(film_content)

    # list with fetched data
    film_data = []

    # fetch film info from html hashes
    for info in film_infos:
        title = (info.find("h3", class_="lister-item-header").findChildren()[1]).get_text(strip=True)
        year = (info.h3.findChildren()[2]).get_text(strip=True)[1:5]
        runtime = (info.find("p", class_="text-muted").findChildren()[2]).get_text(strip=True)[0:3]
        genre = (info.find("p", class_="text-muted").find("span", class_="genre")).get_text(strip=True)
        certificate = info.find("span", class_ ="certificate").get_text(strip=True)
        rating = (info.find("div", class_="ratings-bar").find("div", class_='inline-block ratings-imdb-rating').findChildren()[1]).get_text(strip=True)
        director = info.find_all('p', class_="")[0].a.text.strip()

        # define list to fill in all fetched data
        film_data.append([title, year, runtime, genre, certificate, rating, director])

        # define dataframe containing top 250 films data
        top250_film = pd.DataFrame(film_data, columns = ['title', 'year', 'runtime', 'genre', 'certificate', 'rating', 'director'])

    return top250_film

#%%
topfilm = imdb_film_df(imdb_pages_content)
#%%
def rotten_scores_fetch(topfilm):
    # define empty list
    score_data = []

    # define header language for getting data in english
    headers = {"Accept-Language": "en-US,en;q=0.5"}

    # define static part of the url
    uri = 'https://www.rottentomatoes.com/m/'

    # loop through titles in the dataframe
    for title in topfilm['title']:
        changed_title = title.replace(" ", "_").replace("The_", "").replace(":", "").replace(".", "").replace("'", "").replace("-", "").replace(",", "").replace("ä", "").replace("__","_")
        url = f'{uri}{changed_title}'
        data = rq.get(url, headers=headers)

        if data.status_code == 404:
            score_list = ['not found', 'not_found']
            score_data.append(score_list)

        else:
            soup = bs(data.text, 'html.parser')

            audience_score = soup.find("score-board")["audiencescore"]
            tomato_score = soup.find("score-board")["tomatometerscore"]

            score_list = [tomato_score, audience_score]
            score_data.append(score_list)

    return score_data

#%%
rotten_scores = rotten_scores_fetch(topfilm)
#%%
def final_df(rotten_scores, topfilm):
    # define data folder containing csv
    dir_name = '../data'

    # store imdb_dataframe in final_df
    final_df = topfilm

    # create score_df with score_data from previous function
    score_df = pd.DataFrame(rotten_scores, columns = ['tomato_meter','audience_score'])

    # create new columns in our final dataframe
    final_df['tomato_meter'] = score_df['tomato_meter']
    final_df['audience_score'] = score_df['audience_score']

    # check if dir_name already exists before creating csv file
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        print("Directory " , dir_name ,  " Created ")
    else:
        print("Directory " , dir_name ,  " already exists")

    # export the dataframe with to_csv()
    final_df.to_csv(f'{dir_name}/top_250_films.csv', encoding='utf-8', index=False)