from flask import Flask, render_template, request
import markdown
from pathlib import Path
import olympics
import time
import tags
import os

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
    print(len(articles))
    return render_template('tag.html', tag=tag, articles=articles)

@app.route('/research')
def serve_research():
    return render_template('research.html')

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
    print(research)

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

    with open("last_saved.txt", 'r') as timesaved:
        timed = timesaved.read()

        timed = timed[0:timed.index(".")]

        if (int(timed)+61)<time.time():
            olympics.scrape_olympic_data()

    return render_template('olympics.html')

@app.route('/boilerplate')
def boilerplate():
    readme_file = open("README.md", "r")
    md_template_string = markdown.markdown(
        readme_file.read(), extensions=["fenced_code"]
    )

    return md_template_string

if __name__ == '__main__':
    app.run(debug=True)
