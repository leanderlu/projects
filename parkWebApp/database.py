from bs4 import BeautifulSoup
import requests
from cassandra.cluster import Cluster
from uuid import uuid4
import re

cluster = Cluster(['0.0.0.0'], port = 9042)
session = cluster.connect("park")

'''session.execute("""
    INSERT INTO parks (rating_overall, rating_DECIMAL, rating_camping)                
""")'''
'''session.execute("""
    CREATE TABLE park.parks (
    park_ID UUID PRIMARY KEY,
    name TEXT,
    location TEXT,
    description TEXT,
    rating_overall DECIMAL,
    rating_hiking DECIMAL,
    rating_camping DECIMAL
);
""")

session.execute("""
    CREATE TABLE park.users (
    username TEXT PRIMARY KEY,
    password TEXT
);
""")'''

session.execute("""
    CREATE TABLE park.destinations_visited (
    review_ID UUID PRIMARY KEY,
    username TEXT,
    park_ID UUID,
    review TEXT,
    rating_overall DECIMAL,
    rating_camping DECIMAL,
    rating_hiking DECIMAL
);
""")

'''url = "https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
table = soup.find('table', {'class': 'wikitable'})

parks_data = []
rows = table.find_all('tr')
for row in rows[1:]:  # Skipping the header row
    header = row.find('th')
    cols = row.find_all('td')
    if header:
        tempName = header.text.strip()
        tempNameTwo = tempName.replace('\xa0', ' ')
        name = re.sub(r'[^\w\s]', '', tempNameTwo)
        location = re.split(r'\d', cols[1].text)[0].strip()  
        tempDescription = cols[5].text.strip() 
        description = re.sub(r'(.*\.)[^.]*$', r'\1', tempDescription)
        description = description.replace('\xa0', ' ') 
    else:
        tempName = cols[0].text.strip() 
        tempNameTwo = tempName.replace('\xa0', ' ')
        name = re.sub(r'[^\w\s]', '', tempNameTwo)
        location = re.split(r'\d', cols[2].text)[0].strip() 
        tempDescription = cols[6].text.strip() 
        description = re.sub(r'(.*\.)[^.]*$', r'\1', tempDescription) 
        description = description.replace('\xa0', ' ')  

    parks_data.append({'name': name, 'location': location, 'description': description})

query = "INSERT INTO parks (park_ID, name, location, description) VALUES (uuid(), ?, ?, ?)"
prepared = session.prepare(query)

for park in parks_data:
    name = park['name']
    location = park['location']
    description = park['description']
    try:
        session.execute(prepared, (name, location, description))
    except Exception as e:
        print(f"An error occurred while inserting {name}: {e}")

  
rows = session.execute("SELECT park_id FROM parks")

for row in rows:
    update_query = """
        UPDATE parks
        SET rating_overall = 0, rating_hiking = 0, rating_camping = 0
        WHERE park_id = %s
    """
    session.execute(update_query, [row.park_id])'''    