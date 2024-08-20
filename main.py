from flask import Flask, render_template, request, send_file, jsonify, redirect, session
import markdown
from pathlib import Path
import time
import tags
import os
import csv 
import hashlib
import nh3

app = Flask(__name__)

app.secret_key = b'm#HS3Z65D&TFIyg(&^**d76^*fd66d!TjT6Kzr'

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

@app.route('/boilerplates')
@app.route('/boilerplate')
def serve_boilerplate():
    return render_template('boilerplates.html')

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

"""
# I don't know what this is
@app.route('/tag/<research>')
def serve_tags():
    articles = tags.get_articles_with_tag(tag)
    return render_template('tag.html', tag=tag, articles=articles)
"""

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

@app.route('/boilerplate')
def boilerplate():
    readme_file = open("README.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(), extensions=["fenced_code"]
    )

    return md_template_string

@app.route('/lampgetqthhbhbuhohoahlxakkhcv', methods=['GET'])
def get_color():
    # For the lamp
    # Returns the encrypted color code from color.txt
    # Is one letter so bots can't crawl for it but also makes the request smaller

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

    print(session)

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
