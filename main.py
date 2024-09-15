from flask import Flask, render_template, request, send_file, jsonify, redirect, session
import markdown
from pathlib import Path
import time
import tags
import os
import csv 
import hashlib
import nh3
from datetime import datetime
import sqlite3

app = Flask(__name__)

app.secret_key = b'm#HS3Z65D&TFIyg(&^**d76^*fd66d!TjT6Kzr'

# Helper Functions ---------------

def get_db():
    """Open a new database connection."""
    conn = sqlite3.connect('badusb_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database."""
    with get_db() as db:
        db.execute('''
        CREATE TABLE IF NOT EXISTS data_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description_title TEXT NOT NULL,
            data_type TEXT NOT NULL,
            data_string TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        db.commit()

def sanitize_input(input_string):
    """Sanitize the input data using nh3."""
    return nh3.clean(input_string)


# Article Generation ----------------

global tagss
global researchh
global articless

tagss = set()
researchh = set()
articless = set()

for filename in os.listdir('articles'):
    if filename.endswith('.md'):
        filepath = os.path.join('articles', filename)
        tagss.update(tags.parse_markdown_tags(filepath))

for filename in os.listdir('research'):
    if filename.endswith('.md'):
        filepath = os.path.join('research', filename)
        tagss.update(tags.parse_markdown_tags(filepath))

for filename in os.listdir('research'):
    if filename.endswith('.md'):
        filepath = os.path.join('articles', filename)
        researchh.add(filename[:-3])

for filename in os.listdir('articles'):
    if filename.endswith('.md'):
        filepath = os.path.join('articles', filename)
        articless.add(filename[:-3])

# Visitor Pages ----------------

@app.route('/')
def index():
    global tagss
    global researchh
    global articless

    return render_template('index.html', tags=tagss, articles=articless, research=researchh)

@app.route('/tag/<tag>')
def tag(tag):
    global tagss
    
    tag = nh3.clean(tag)

    for char in tag:
        if not char.isalpha() and char != " ":
            return 'Are you trying to hack me?'

    if tag not in tagss:
        return "You can't do that"

    articles = tags.get_articles_with_tag(tag, 'articles')
    research = tags.get_articles_with_tag(tag, 'research')

    return render_template('tag.html', tag=tag, articles=articles, research=research)

@app.route('/research')
def serve_research():
    return render_template('research.html')

@app.route('/articles/<article>')
def serve_article_markdown(article):

    if not Path("articles/"+article+".md").exists():
        return render_template('404.html')

    with open("articles/"+article+".md", 'r') as file:
        content = file.readlines()

        if "#" not in content[0]: content = content[1:]
            
        title = next((item for item in content if item.startswith('#')), None)[2:]
        content = ''.join(content)

    # Convert Markdown to HTML
    html = markdown.markdown(content)

    # Render the HTML with a template
    return render_template('article.html', content=html, title=title)


@app.route('/research/<research>')
def serve_specific_research(research):

    if not Path("research/"+research+".md").exists():
        return render_template('404.html')
    
    with open("research/"+research+'.md', 'r') as file:
        content = file.readlines()

        if "#" not in content[0]: content = content[1:]

        title = next((item for item in content if item.startswith('#')), None)[2:]
        content = ''.join(content)
        
    # Convert Markdown to HTML
    html = markdown.markdown(content)

    # Render the HTML with a template
    return render_template('article.html', content=html, title=title)

@app.route('/boilerplates')
@app.route('/boilerplate')
def boilerplate():
    readme_file = open("articles/Boilerplate.md", "r")
    content = markdown.markdown(readme_file.read(), extensions=["fenced_code"])

    html = markdown.markdown(content)

    # Render the HTML with a template
    return render_template('article.html', content=html, title="Boilerplate")


    return md_template_string

"""
# I don't know what this is
@app.route('/tag/<research>')
def serve_tags():
    articles = tags.get_articles_with_tag(tag)
    return render_template('tag.html', tag=tag, articles=articles)
"""
# Family Olympics ----------------

"""
@app.route('/olympics')
def family_olympics():
# Handles the family olympics data

    with open("last_saved.txt", 'r') as timesaved:
        timed = timesaved.read()

        timed = timed[0:timed.index(".")]

        if (int(timed)+61)<time.time():
            olympics.scrape_olympic_data()

    countries = []
    names = []
    gold_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    silver_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    bronze_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    total_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    populations = [52081799, 52428290, 123890000, 5338900, 203080756, 68449000, 41012563, 27282542, 5562363, 2825544, 5089478]
    athletes = [141, 72, 393, 195, 276, 573, 315, 460, 107, 58, 134]

    with open('scraped.csv', mode='r') as file:
        index = 1
        reader = csv.reader(file)
        for row in reader:
            if index == 1:
                countries = row
            elif index == 2:
                names = row
            elif index == 3:
                gold_medals = row
            elif index == 4:
                silver_medals = row
            elif index == 5:
                bronze_medals = row
            elif index == 6:
                medals = row
            index+=1

    gold_medals = olympics.convert_to_integers(gold_medals)
    silver_medals = olympics.convert_to_integers(silver_medals)
    bronze_medals = olympics.convert_to_integers(bronze_medals)
    medals = olympics.convert_to_integers(medals)
    total_medals=medals

    medals_per_capita = olympics.medals_per_capita(medals, populations)
    medals_per_athlete = olympics.medals_per_capita(medals, athletes)

    combined_list = []
    for name, country, medals in zip(names, countries, medals_per_athlete):
        combined_list.append({
            'name': name,
            'country': country,
            'medals_per_athlete': medals
        })

    combined_list = sorted(combined_list, key=lambda x: x['medals_per_athlete'], reverse=True)

    return render_template('olympics.html', gold_medals = gold_medals, silver_medals = silver_medals, bronze_medals = bronze_medals, medals = total_medals, countries = countries, medals_per_capita = medals_per_capita, medals_per_athlete = medals_per_athlete, leaderboard = combined_list)
"""


# BadUSB Endpoint ----------------

@app.route('/badusb_sendinfo_bou_bao_ber_bwe_bgh_hop_pop_cop_qop_asl_alqpc_meht_bqaf', methods=['POST'])
def register_badusb_info():

    try:
        # Extracting JSON data from the request
        data = request.get_json()

        # Check if the required fields are in the request
        if not all(k in data for k in ('description_title', 'data_type', 'data_string')):
            return jsonify({'error': 'Missing required fields. Nothing submitted here is private, do not submit information or post to this server if you are not the original author. Nothing submitted to this url will be saved, kept private or secure.'}), 400

        # Sanitize input data
        description_title = sanitize_input(data['description_title'])
        data_type = sanitize_input(data['data_type'])
        data_string = sanitize_input(data['data_string'])

        # Get the current timestamp
        timestamp = datetime.now()

        # Insert the data into the SQLite database
        with get_db() as db:
            db.execute('''
            INSERT INTO data_entries (description_title, data_type, data_string, timestamp)
            VALUES (?, ?, ?, ?)
            ''', (description_title, data_type, data_string, timestamp))
            db.commit()

        return jsonify({'message': 'Data received and saved successfully. Nothing submitted here is private, do not submit information or post to this server if you are not the original author. Nothing submitted to this url will be saved, kept private or secure.'}), 200

    except Exception as e:
        return jsonify({'error': str(e) + '. Nothing submitted here is private, do not submit information or post to this server if you are not the original author. Nothing submitted to this url will be saved, kept private or secure.'}), 500
    
    # Download helper scripts from github if necessary

@app.route('/badusb_view_info_goduqwgdowudvqpuqobnmzqoihsieyfvywiveafisdyhvjbweofjbewuvw354678iyesvbwyae', methods=['GET'])
def view_data():
    """Render an HTML page with a table of all data from the database, sorted by timestamp. Uses the saved session password from the color picker as authentication because I'm lazy"""

    if 'password' in session:
        if session.get('password') != "3cd71abb4a6b6be8422ab9cfbb3c28e906cf8f71f73e78a023b08d1a386e16e7":
            print(session.get('password'))
            return render_template('404.html')
    else:
        print("not in session")
        return render_template('404.html')
        
    with get_db() as db:
        data_entries = db.execute('''
        SELECT description_title, data_type, data_string, timestamp
        FROM data_entries
        ORDER BY timestamp DESC
        ''').fetchall()

    return render_template('view_badusb_data.html', data_entries=data_entries)

# Lamp Stuff ----------------

@app.route('/lampgetqthhbhbuhohoahlxakkhcv', methods=['GET'])
def get_color():
    # For the lamp
    # Returns the encrypted color code from color.txt

    with open("color.txt", 'r') as f:
        color = f.read()
    
    return color

@app.route('/lampchangewqubmzbiqcwcwcwcwecqqwcszcwecwev', methods=['POST'])
def change():
    # For the lamp
    # Takes a color code and a password
    # If the password is right, it saves the code to color.txt 

    json_data = request.get_json()
    
    # Check if JSON data is None
    if json_data is None:
        return jsonify({"Go": "away"}), 400
    
    color = json_data.get('color')
    password = json_data.get('pas')
    
    if color is None or password is None:
        return jsonify({"Go": "away"}), 400
    
    with open("password.txt", 'r') as f:
        good_password = f.read()
    
    if password!=good_password:
        return jsonify({"Go": "away"}), 400
    else:
        with open("color.txt", 'w') as f:
            print(color)
            towrite=""

            for i in color: 
                if i not in ["[", "]", " "]:
                    towrite+=str(i)
                towrite+=","

            towrite=towrite[0:-1]
            print(towrite)

            f.write(towrite)
            
    #print(color, password)

    return ''

@app.route('/lamp_color_picker')
def lamp_color_picker():
    # The route for the lamp color picker for browsers
    return render_template('color.html')

@app.route('/lamp_color_picker_api_ljbwefobwejflwejfljwef12edwqdqdsf', methods=['POST'])
def lamp_color_picker_api():
    # The route for the color picker to send the color to
    color = request.form.get('color')
    password = request.form.get('password')

    password = hashlib.sha256(password.encode()).hexdigest()

    if 'password' in session and password == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855":
        password = session['password']

    if password != "3cd71abb4a6b6be8422ab9cfbb3c28e906cf8f71f73e78a023b08d1a386e16e7":
        return redirect("/")
    
    session['password'] = password

    # Translate color to rgb values and put in color.txt
    color = color.lstrip('#')
    with open("color.txt", "w") as file: file.write(str(tuple(int(color[i:i+2], 16) for i in (0, 2, 4)))[1:-1].replace(" ", ""))

    return redirect("/lamp_color_picker")

@app.route('/robots.txt')
def robots():
    return send_file('static/robots.txt')

@app.route('/security.txt')
@app.route('/.well-known/security.txt')
def security_warn():
    return send_file('static/security.txt')

if __name__ == '__main__':
    #app.run(host="0.0.0.0", debug=True)
    app.run(host="127.0.0.1", debug=True)
