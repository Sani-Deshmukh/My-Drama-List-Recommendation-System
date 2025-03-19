import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random 
import os

BASE_URL = "https://mydramalist.com/shows?page="  # UPDATED URL
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

#global user index to maintain username to index mapping in the matrix
USER_INDEX = 0
DRAMA_INDEX = 0
COLD_START = []

SEEN = set()

''' Initializes URL and loops through all shows while filtering for actresses, articles, discussion...
    Gets the shows TITLE, RATING, and calls helper for extracting reviews
'''
def get_drama_list(page):
    global USER_INDEX, DRAMA_INDEX, USERNAME_TO_INDEX
    url = BASE_URL + str(page)
    response = requests.get(url, headers=HEADERS)
    if (response.status_code != 200):
        print(f"Scraping {url} - Status Code: {response.status_code}")  # Debugging

    if response.status_code == 404:
        print("Error 404: Page Not Found. Check the URL structure!")
        return []

    if response.status_code != 200:
        print(f"Failed to retrieve page {page}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    drama_data = []

    dramas = soup.find_all("div", class_="box")
    if not dramas:
        print(f"Warning: No dramas found on page {page}. MDL may have changed its structure.")
        

    for drama in dramas:
        title_tag = drama.find("h6", class_="text-primary")
        rating_tag = drama.find("span", class_="score")
        link_tag = drama.find("a")
        
        title = title_tag.text.strip() if title_tag else "N/A"
        rating = rating_tag.text.strip() if rating_tag else "N/A"
        
        # cold start.... or show doesn't exist: deal with cold starts later
        if rating == "N/A" or title == "N/A":
            continue 

        drama_url = link_tag["href"] if link_tag and "href" in link_tag.attrs else None
        
        if drama_url and ("article" in drama_url or "people" in drama_url 
            or "stats" in drama_url or "discussion" in drama_url or title in SEEN):
                continue    #filters articles and actors 
        SEEN.add(title)
        # Reviews
        results = get_drama_reviews(drama_url) if drama_url else []

        if (title_tag and rating_tag and results): #only add relevant entries
            for entry in results:
                username, overall_rating, story, acting, music, rewatch = entry[0], entry[1], entry[2], entry[3], entry[4], entry[5]
                
                # No available username for review is cold start
                if (username == "N/A"):
                    continue
               
                drama_data.append({
                    "Username": username,
                    "Title": title,
                    "Rating": rating,
                    "overall_rating": overall_rating,
                    "story": story,
                    "acting": acting,
                    "music": music,
                    "rewatch": rewatch
                })
    
    return drama_data


''' Extracts reviews fir teh current shows
    Reviews from EACH user can be broken down into categories:
        - Overall Rating
        - Story 
        - Acting/Cast 
        - Music 
        - Rewatch value
    - Every user has values for one of these so the tensor will end up being n * m * 5 if SVD 
    
    - The raw text of the review can also be extracted as a parameter to 
        learn on based on sentiment analysis but this could be more advanced analysis 
'''

import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_drama_reviews(drama_url):
    if not drama_url:
        return [("N/A", "N/A", "N/A", "N/A", "N/A", "N/A")]  # Default empty values

    results = []
    page = 1
    all_review_ids = set()  # Store all unique IDs across pages

    while True:
        full_url = f"https://mydramalist.com{drama_url}/reviews?page={page}"
        response = requests.get(full_url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Failed to fetch {full_url}, stopping review scraping.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = soup.find_all("div", class_="review")
        
        if not reviews:  
            break

        # Extract review IDs from this page
        current_review_ids = {review.get("id") for review in reviews if review.get("id")}

        # If all these IDs are already in all_review_ids, we are repeating a page
        if current_review_ids.issubset(all_review_ids):
            break
        
        # Otherwise, add them to the global set
        all_review_ids.update(current_review_ids)

        for review in reviews:
            try:
                username_tag = review.find("a", class_="text-primary")
                username = username_tag.text.strip() if username_tag else "Unknown User"

                # Extract overall rating
                overall_rating_tag = review.find("div", class_="rating-overall").find("span", class_="score")
                overall_rating = overall_rating_tag.text.strip() if overall_rating_tag else "N/A"

                if not username and not overall_rating:
                    continue

                # Extract category ratings (Story, Acting, Music, Rewatch)
                category_ratings = {"Story": "N/A", "Acting": "N/A", "Music": "N/A", "Rewatch": "N/A"}
                category_mapping = {
                    "Story": "Story",
                    "Acting/Cast": "Acting",
                    "Music": "Music",
                    "Rewatch Value": "Rewatch"
                }

                rating_divs = review.find_all("div", class_="list-group review-rating")
                if rating_divs:
                    for rating_div in rating_divs:
                        for sub_div in rating_div.find_all("div"):
                            text_parts = sub_div.text.strip().split()

                            if len(text_parts) > 1:
                                cat_name_str = " ".join(text_parts[:-1])
                                rating_value = text_parts[-1]
                                mapped_name = category_mapping.get(cat_name_str, None)

                                if mapped_name:
                                    category_ratings[mapped_name] = rating_value

                results.append((username, overall_rating, category_ratings["Story"], 
                                category_ratings["Acting"], category_ratings["Music"], category_ratings["Rewatch"]))

            except Exception as e:
                print(f"Skipping a review due to error: {e}")
                continue

        # Move to the next page
        page += 1
        time.sleep(2) 

    return results if results else [("N/A", "N/A", "N/A", "N/A", "N/A", "N/A")]


import os

def scrape_all_dramas(start_page=1, pages=250):
    """Scrape multiple pages of dramas and save to CSV while avoiding duplicates"""
    csv_filename = "mdl_dramas_1.csv"
    
    # Load existing data if CSV exists
    if os.path.exists(csv_filename):
        existing_df = pd.read_csv(csv_filename)
        existing_titles = set(existing_df["Title"].astype(str))  # Track already saved titles
    else:
        existing_df = None
        existing_titles = set()

    for page in range(start_page, pages + 1):
        print(f"Scraping page {page}...")

        drama_list = get_drama_list(page)
        if not drama_list:
            time.sleep(10)
            drama_list = get_drama_list(page)

        if drama_list:
            df = pd.DataFrame(drama_list)
            df = df[~df["Title"].isin(existing_titles)]
            
            if not df.empty:
                df.to_csv(csv_filename, mode='a', index=False, header=not os.path.exists(csv_filename))
                print(f"✅ Saved page {page} to {csv_filename}. ({len(df)} new rows)")
            
            # Update the set of saved titles
            existing_titles.update(df["Title"].astype(str))

        time.sleep(random.uniform(10, 15))  

    print("🎉 Scraping completed! Data saved to mdl_dramas_2.csv")

    
    
scrape_all_dramas(start_page=1, pages=36)
