from flask import Flask, render_template, request
import markdown
from pathlib import Path
import olympics
import time
import tags
import os
import csv 

app = Flask(__name__)

@app.route('/')
def index():
    tagss = set()
    researchh = set()
    articless = set()

    for filename in os.listdir('articles'):
        if filename.endswith('.md'):
            filepath = os.path.join('articles', filename)
            tagss.update(tags.parse_markdown_tags(filepath))

    for filename in os.listdir('research'):
        if filename.endswith('.md'):
            filepath = os.path.join('articles', filename)
            researchh.add(filename[:-3])

    for filename in os.listdir('articles'):
        if filename.endswith('.md'):
            filepath = os.path.join('articles', filename)
            articless.add(filename[:-3])


    return render_template('index.html', tags=tagss, articles=articless, research=researchh)

@app.route('/tag/<tag>')
def tag(tag):
    articles = tags.get_articles_with_tag(tag)
    return render_template('tag.html', tag=tag, articles=articles)

@app.route('/research')
def serve_research():
    return render_template('research.html')

@app.route('/boilerplate')
def serve_boilerplate():
    return render_template('boilerplates.html')

@app.route('/articles/<article>')
def serve_aricle_markdown(article):

    if Path("articles/"+article+".md").exists() == False:
        return render_template('404.html')

    with open("articles/"+article+".md", 'r') as file:
        content = file.readlines()[1:]
        content = ''.join(content)

    # Convert Markdown to HTML
    html = markdown.markdown(content)

    # Render the HTML with a template
    #return md.convert(content)
    return render_template('article.html', content=html)


@app.route('/research/<research>')
def serve_specific_research(research):

    if Path("research/"+research+".md").exists() == False:
        return render_template('404.html')

    with open("research/"+research+'.md', 'r') as file:
        content = file.read()
        
    # Convert Markdown to HTML
    html = markdown.markdown(content)

    # Render the HTML with a template
    return render_template('article.html', content=html)

@app.route('/tag/<research>')
def serve_tags(research):
    articles = tags.get_articles_with_tag(tag)
    return render_template('tag.html', tag=tag, articles=articles)


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
    gold_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    silver_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    bronze_medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    medals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    populations = [52081799, 52428290, 123890000, 5338900, 203080756, 68449000, 41012563, 27282542, 5562363, 2825544]
    athletes = [141, 72, 393, 195, 276, 573, 315, 460, 107, 58]

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

@app.route('/boilerplate')
def boilerplate():
    readme_file = open("README.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(), extensions=["fenced_code"]
    )

    return md_template_string

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
