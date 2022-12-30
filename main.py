import requests
from bs4 import BeautifulSoup
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from postgrest import Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

# Make a request to the webpage
url = "https://ads-up.fr/publications/categorie/seo/"
response = requests.get(url)
html = response.text

# Parse the HTML
soup = BeautifulSoup(html, "html.parser")

# Find all articles
articles = soup.find_all("article", class_="loop-entry")

for article in articles:
    # Find the title and extract the text
    title = article.find("h3", {"data-equal": "posts-title"}).text
    # Find the link to the article
    article_link = article.find("div", class_="entry-bottom").find("a")['href']
    # Make a GET request to the link
    link_response = requests.get(article_link)
    link_html = link_response.text
    # Parse the HTML
    link_soup = BeautifulSoup(link_html, "html.parser")
    # Find the element with the class "edito-content-content"
    content = link_soup.find("div", class_="edito-content-content").get_text()
    # Find the category
    category_text = article.find("div", class_="publication-category").get_text()
    category = category_text.split("\n")[1]
    # Find the date published and extract the attribute value
    date_published = article.find("div", class_="entry-author").text

    # Insert the data into the database
    data = supabase.table("News").insert(
        {"title": title, "link": article_link, "tag": category, "date_published": date_published, "content": content}
    ).execute()
    assert len(data.data) > 0

