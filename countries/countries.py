import sqlite3
import requests

# URL to fetch countries and continents data
URL = "https://restcountries.com/v3.1/all?fields=name,region,cca2"

DATABASE = 'countries.db'

def fetch_countries_data():
    """Fetch countries and their continents from the API."""
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)
        return []

def insert_data(countries_data):
    """Insert fetched countries and continents data into the database."""
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        
        # Ensure continents table is prepared for new entries
        continents = set(country["region"] for country in countries_data if "region" in country)
        for continent in continents:
            c.execute("INSERT OR IGNORE INTO continents (name) VALUES (?)", (continent,))
        
        # Fetch continents' IDs
        c.execute("SELECT id, name FROM continents")
        continent_ids = {name: id for id, name in c.fetchall()}
        
        # Insert countries with the correct continent mapping and ISO2 code
        for country in countries_data:
            if "region" in country and country["region"]:  # Check if region is present and not empty
                continent_id = continent_ids[country["region"]]
                country_name = country["name"]["common"]
                iso2_code = country["cca2"]
                c.execute("INSERT OR IGNORE INTO countries (name, continent_id, iso2) VALUES (?, ?, ?)",
                          (country_name, continent_id, iso2_code))

        conn.commit()

if __name__ == "__main__":
    countries_data = fetch_countries_data()
    if countries_data:
        insert_data(countries_data)
        print("Database updated with countries and continents.")
    else:
        print("No data to update.")
