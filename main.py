from flask import Flask, render_template, request, send_file, jsonify, redirect, session
import markdown
from pathlib import Path
import time
import tags
import csv 
import hashlib
import nh3
from datetime import datetime
import sqlite3
import os, random
import loaded_image_captions
import re
import requests
from bs4 import BeautifulSoup
import subprocess

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

    cmd = ["git", "rev-parse"]
    if short:
        cmd.append("--short")
    cmd.append("HEAD")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout.strip()

def get_last_commit_date(filepath):
    # Convert to relative path if absolute
    if os.path.isabs(filepath):
        try:
            # Get the git repo root
            repo_root = subprocess.check_output(
                ['git', 'rev-parse', '--show-toplevel'],
                stderr=subprocess.PIPE,
                text=True
            ).strip()
            filepath = os.path.relpath(filepath, repo_root)
        except subprocess.CalledProcessError:
            return None

    try:
        # Get the commit date in ISO 8601 format
        result = subprocess.check_output(
            ['git', 'log', '-1', '--format=%ai', '--', filepath],
            stderr=subprocess.PIPE,
            text=True
        ).strip()

        if not result:
            return None  # File not tracked by git

        # Parse the ISO 8601 date string
        # Format: 2023-10-15 14:30:25 +0200
        return datetime.fromisoformat(result)

    except subprocess.CalledProcessError:
        return None  # Not a git repo or other error


def get_last_commit_date_formatted(filepath, date_format="%Y-%m-%d"):
    commit_date = get_last_commit_date(filepath)

    if commit_date is None:
        return "File not tracked by git or not in a git repository"

    return commit_date.strftime(date_format)

def get_stats():
    global bose_jobs
    global bose_ram
    global bose_cpus
    global bose_gpus
    global stultus_urls

    with open("/stats.txt") as f:
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

global tagss
global articless
global total_articles
global total_words
global ghz_days
global current_commit
global edit_dates
global bose_jobs
global bose_ram
global bose_cpus
global bose_gpus
global stultus_urls

tagss = set()
articless = []
edit_dates = []

for filename in os.listdir('articles'):
    if filename.endswith('.md'):
        filepath = os.path.join('articles', filename)
        tagss.update(tags.parse_markdown_tags(filepath))

for filename in os.listdir('articles'):
    if filename.endswith('.md'):
        filepath = os.path.join('articles', filename)
        articless.append(filename[:-3])
        article_date = tags.get_article_date(filepath)
        if article_date:
            edit_dates.append(article_date)
        else:
            edit_dates.append(get_last_commit_date_formatted(filepath))

data = count_words_in_directory("articles")
total_articles = data[0]
total_words = data[1]

ghz_days = find_user_ghz_days("Jack Hagen")
current_commit = get_current_commit_hash()

get_stats()

# Visitor Pages ----------------

@app.route('/')
def index():
    global tagss
    global articless
    global total_articles
    global total_words
    global current_commit
    global edit_dates

    loaded_image = random.choice(os.listdir("static/images/homepage"))
    loaded_image_caption = loaded_image_captions.get_caption(loaded_image)

    sorted_pairs = sorted(zip(edit_dates, articless), reverse=True)
    edit_dates, articless = zip(*sorted_pairs) if sorted_pairs else ([], [])

    return render_template('index.html', tags=tagss, articles=articless, loaded_image_filepath=loaded_image, loaded_image_caption=loaded_image_caption, total_articles=total_articles, total_words=total_words, ghz_days=ghz_days, current_commit=current_commit, edit_dates=edit_dates, bose_cpus=bose_cpus, bose_ram=bose_ram, bose_gpus=bose_gpus, bose_jobs=bose_jobs, stultus_urls=stultus_urls)

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

    return render_template('tag.html', tag=tag, articles=articles)


@app.route('/articles/<article>')
def serve_article_markdown(article):

    if not Path("articles/"+article+".md").exists():
        return render_template('404.html')

    filepath = "articles/"+article+".md"
    metadata, content_start = tags.parse_metadata(filepath)

    with open(filepath, 'r') as file:
        content = file.readlines()

        content = content[content_start:]

        title = next((item for item in content if item.startswith('#')), None)[2:]
        content = ''.join(content)

    total_words = len(content.split())

    # Convert Markdown to HTML
    html = markdown.markdown(content)

    # Render the HTML with a template
    return render_template('article.html', content=html, title=title, total_words=total_words)

@app.route('/research')
@app.route('/research/')
def serve_research():
    return render_template('research.html')

@app.route('/now')
def now():
    # Page with current updates
    return render_template('now.html')

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
    readme_file = open("articles/Boilerplate.md", "r")
    content = markdown.markdown(readme_file.read(), extensions=["fenced_code"])

    html = markdown.markdown(content)

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
    app.run(host="0.0.0.0", debug=False, port=5000)
