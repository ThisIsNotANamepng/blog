import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_olympic_data():

    countries = ["🇰🇷 South Korea", "🇰🇪 Kenya", "🇯🇵 Japan", "🇳🇿 New Zealand", "🇧🇷 Brazil", "🇫🇷 France", "🇨🇦 Canada", "🇦🇺 Australia", "🇳🇴 Norway", "🇯🇲 Jamaica", "🇮🇪 Ireland"]
    people = ["Jack", "Mary", "George", "Greg", "Laura", "Sam", "Sean", "LeAnn", "Jennifer", "David", "Jonah"]
    gold_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    silver_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    bronze_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ranks = []

    url = 'https://en.wikipedia.org/wiki/2024_Summer_Olympics_medal_table'
    table_class = 'wikitable'

    # Send a GET request to the Wikipedia URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table with the specified class
        table = soup.find('table', class_=table_class)
        
        if table:
            # Extract data from the table
            data = []
            rows = table.find_all('tr')
            for row in rows:
                row_data = []
                cells = row.find_all(['th', 'td'])
                for cell in cells:
                    row_data.append(cell.get_text(strip=True))
                if row_data:
                    data.append(row_data)
                    
        else:
            print("Table not found.")
    else:
        print("Failed to retrieve the webpage.")

    if data:
        for row in data:
            if len(row)>5:
                del row[0]
            
            for country in countries:
                print(country[3:], row[0])
                if country[3:] in row[0]:
                    print(row[2])
                    country_index=countries.index(country)
                    gold_medals[country_index]=(row[1])
                    silver_medals[country_index]=(row[2])
                    bronze_medals[country_index]=(row[3])
                    total_medals[country_index]=(row[4])
                    ranks.append(row[0])

                    #print(country[3:])
                    #print(row[5])
            
    data = [countries, people, gold_medals, silver_medals, bronze_medals, total_medals, ranks]

    save_scraped(data)

def save_scraped(lists, filename='scraped.csv'):
    with open("last_saved.txt", 'w') as timesaved:
        timesaved.write(str(time.time()))

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for lst in lists:
            writer.writerow(lst)

def load_lists_from_csv(filename):
    loaded_lists = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            loaded_lists.append(row)
    return loaded_lists

def convert_to_integers(str_list):
    int_list = []
    for s in str_list:
        try:
            num = int(s)
            int_list.append(num)
        except ValueError:
            pass  # You can choose to skip or handle invalid entries here
    return int_list

def medals_per_capita(list1, list2):
    # Check if the lists are of the same length
    if len(list1) != len(list2):
        raise ValueError("Lists must have the same length")

    # Use list comprehension to create a new list of division results
    result = [list1[i] / list2[i] for i in range(len(list1))]
    
    return result

