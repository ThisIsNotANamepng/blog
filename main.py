from flask import Flask, render_template, request, send_file, jsonify, redirect, session
import markdown
from pathlib import Path
import time
import tags
import csv 
import hashlib
import nh3
import sqlite3
import os, random
import loaded_image_captions
import pseudo_resume
import re
import requests
from bs4 import BeautifulSoup
import subprocess

ARTICLES_DIR = 'articles'
# Python-Markdown's core dialect has no ``` fences - without this, code blocks
# in articles render as literal backticks and mangled paragraphs.
MARKDOWN_EXTENSIONS = ['fenced_code', 'tables']
app = Flask(__name__)

app.secret_key = b'm#HS3Z65D&TFIyg(&^**d76^*fd66d!TjT6Kzr'

# Helper Functions ---------------

def sanitize_input(input_string):
    """Sanitize the input data using nh3."""
    return nh3.clean(input_string)

def count_words_in_file(filepath):
    """Count words in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            # Split on whitespace and filter out empty strings
            words = re.findall(r'\b\w+\b', text.lower())
            return len(words)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 0

def count_words_in_directory(directory):
    """Count words in all .md files in a directory."""
    total_words = 0
    file_count = 0

    # Use Path for cleaner path handling
    path = Path(directory)

    # Find all .md files recursively
    for md_file in path.rglob('*.md'):
        words = count_words_in_file(md_file)
        total_words += words
        file_count += 1

    return file_count, total_words
        
def find_user_ghz_days(username):
    url = "https://www.mersenne.org/report_top_500/"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table body containing user data
    tbody = soup.find('tbody')
    if not tbody:
        # Fallback: search all tables
        tables = soup.find_all('table')
        for table in tables:
            result = search_table_for_user(table, username)
            if result is not None:
                return result
        return None

    return search_table_for_user(tbody, username)

def search_table_for_user(container, username):
    rows = container.find_all('tr')

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 3:
            # Member name is in the 2nd column (index 1)
            name_cell = cells[1]
            user_name = name_cell.get_text(strip=True)

            # Check for exact match or case-insensitive match
            if user_name.lower() == username.lower():
                # Total GHz Days is in the 3rd column (index 2)
                ghz_days_text = cells[2].get_text(strip=True)
                try:
                    ghz_days = int(ghz_days_text.replace(',', ''))
                    return ghz_days
                except ValueError:
                    return None

    return None

def get_current_commit_hash(short=True):
    # The Docker image has no .git, so the build passes the hash in instead.
    if os.environ.get("GIT_COMMIT"):
        return os.environ["GIT_COMMIT"]

    cmd = ["git", "rev-parse"]
    if short:
        cmd.append("--short")
    cmd.append("HEAD")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except (subprocess.CalledProcessError, OSError):
        return "unknown"

    return result.stdout.strip()

def get_stats():
    global bose_jobs
    global bose_ram
    global bose_cpus
    global bose_gpus
    global stultus_urls

    with open("/stats.txt", "r") as f:
        stuff = f.readlines()

    for i in stuff:
        if "stultus_urls" in i:
            stultus_urls = i[14:-1]
            continue
        elif "jobs" in i:
            bose_jobs = i[6:-1] 
            continue
        elif "cpu_cores" in i:
            bose_cpus = i[11:-1]
            continue
        elif "ram" in i:
            bose_ram = i[5:-1]
            continue
        elif "gpus" in i:
            bose_gpus = i[6:-1]
            continue


# Article Generation ----------------

global ghz_days
global current_commit
global bose_jobs
global bose_ram
global bose_cpus
global bose_gpus
global stultus_urls


def render_article(filepath, metadata, content_start):
    """Turn one article into everything article.html needs."""
    with open(filepath, 'r') as file:
        content = file.readlines()[content_start:]

    heading = next((item for item in content if item.startswith('#')), None)
    # An article with no heading falls back to its filename instead of taking
    # down every worker at startup.
    title = heading[2:] if heading else os.path.basename(filepath)[:-3]
    content = ''.join(content)

    return {
        'content': markdown.markdown(content, extensions=MARKDOWN_EXTENSIONS),
        'title': title,
        'total_words': len(content.split()),
        'edit_date': metadata.get('date') or None,
    }


def build_article_index():
    """Read and render every article once, at startup.

    Everything the request handlers need lives in the returned dict, so serving
    a page is a dict lookup - no disk reads or markdown rendering per request.
    """
    tagss = set()
    articless = []
    edit_dates = []
    pages = {}

    for filename in os.listdir(ARTICLES_DIR):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(ARTICLES_DIR, filename)
        metadata, content_start = tags.parse_metadata(filepath)
        tagss.update(metadata['tags'])
        articless.append(filename[:-3])

        edit_dates.append(metadata.get('date', '') or None)

        pages[filename[:-3]] = render_article(filepath, metadata, content_start)

    # Sort newest-first once, here, so the handlers only ever read.
    # Undated articles sort last rather than blowing up the None/str compare.
    sorted_pairs = sorted(zip(edit_dates, articless),
                          key=lambda pair: (pair[0] or '', pair[1]), reverse=True)
    edit_dates, articless = zip(*sorted_pairs) if sorted_pairs else ((), ())

    file_count, word_count = count_words_in_directory(ARTICLES_DIR)

    # /boilerplate renders the whole file, metadata lines included.
    boilerplate_path = os.path.join(ARTICLES_DIR, 'Boilerplate.md')
    boilerplate = None
    if os.path.isfile(boilerplate_path):
        with open(boilerplate_path, 'r') as readme_file:
            boilerplate = markdown.markdown(readme_file.read(), extensions=MARKDOWN_EXTENSIONS)

    return {
        'tags': tagss,
        'articles': articless,
        'edit_dates': edit_dates,
        'total_articles': file_count,
        'total_words': word_count,
        'pages': pages,
        'boilerplate': boilerplate,
    }

article_index = build_article_index()

#UNCOMMENT
#ghz_days = find_user_ghz_days("Jack Hagen")
ghz_days=1
current_commit = get_current_commit_hash()

get_stats()

# Visitor Pages ----------------

@app.route('/')
def index():
    global current_commit

    articles = article_index

    loaded_image = random.choice(os.listdir("static/images/homepage"))
    loaded_image_caption = loaded_image_captions.get_caption(loaded_image)

    return render_template('index.html', tags=articles['tags'], articles=articles['articles'], loaded_image_filepath=loaded_image, loaded_image_caption=loaded_image_caption, total_articles=articles['total_articles'], total_words=articles['total_words'], ghz_days=ghz_days, current_commit=current_commit, edit_dates=articles['edit_dates'], bose_cpus=bose_cpus, bose_ram=bose_ram, bose_gpus=bose_gpus, bose_jobs=bose_jobs, stultus_urls=stultus_urls)

@app.route('/tag/<tag>')
def tag(tag):
    tag = nh3.clean(tag)

    for char in tag:
        if not char.isalpha() and char != " ":
            return 'Are you trying to hack me?'

    if tag not in article_index['tags']:
        return "You can't do that"

    articles = tags.get_articles_with_tag(tag, 'articles')

    return render_template('tag.html', tag=tag, articles=articles)


@app.route('/articles/<article>')
def serve_article_markdown(article):

    page = article_index['pages'].get(article)

    if page is None:
        return render_template('404.html')

    # Markdown was rendered at startup in build_article_index()
    return render_template('article.html', **page)

@app.route('/research')
@app.route('/research/')
def serve_research():
    return render_template('research.html')

@app.route('/projects')
@app.route('/projects/')
def projects():
    return render_template('projects.html')

@app.route('/now')
def now():
    # Page with current updates
    return render_template('now.html')

@app.route('/pseudo_resume')
@app.route('/pseudo-resume')
def pseudo_resume_page():
    """Interactive version of articles/Pseudo Resume.md."""
    return render_template('pseudo_resume.html', **pseudo_resume.page_data())

@app.route('/resume')
def resume():
    pdf_path = 'static/Resume.pdf'
    return send_file(pdf_path, as_attachment=False)

@app.route('/gpg')
def gpg_path():
    return send_file("static/misc/jack_hagen_public.gpg", as_attachment=False)


@app.route('/boilerplates')
@app.route('/boilerplate')
def boilerplate():
    html = article_index['boilerplate']

    if html is None:
        return render_template('404.html')

    # Render the HTML with a template
    return render_template('article.html', content=html, title="Boilerplate")


# Utilities -----------------

@app.errorhandler(404)
def page_not_found(error):
    # Render the custom 404 error page
    return render_template('404.html'), 404

@app.route('/robots.txt')
def robots():
    return send_file('static/robots.txt')

@app.route('/security.txt')
@app.route('/.well-known/security.txt')
def security_warn():
    return send_file('static/security.txt')



@app.route('/senate')
def senate_baby():

    return render_template('senate.html')

@app.route('/test')
def test_baby():

    return render_template('test.html')

@app.route('/pictures')
def pictures():

    images = loaded_image_captions.get_images()

    return render_template("pictures.html", images=images)


if __name__ == '__main__':
    #app.run(host="0.0.0.0", debug=True)
    app.run(host="0.0.0.0", debug=False, port=5001)
