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
import shutil
import loaded_image_captions
#import pseudo_resume
import re
import requests
from bs4 import BeautifulSoup
import subprocess
import threading

ARTICLES_DIR = 'articles'
# Python-Markdown's core dialect has no ``` fences - without this, code blocks
# in articles render as literal backticks and mangled paragraphs.
MARKDOWN_EXTENSIONS = ['fenced_code', 'tables']
ARTICLES_REPO_URL = os.environ.get(
    'ARTICLES_REPO_URL',
    'https://github.com/ThisIsNotANamepng/blog_articles.git',
)
# How stale the articles may get before the next visitor triggers a check.
ARTICLES_SYNC_INTERVAL = int(os.environ.get('ARTICLES_SYNC_INTERVAL', 600))

_sync_lock = threading.Lock()
_sync_in_flight = False
_last_sync_check = 0.0


def _git(*args, cwd=None):
    return subprocess.run(
        ['git', *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    ).stdout.strip()


def clone_articles():
    """Throw away whatever is on disk and take a fresh shallow clone."""
    if os.path.exists(ARTICLES_DIR):
        shutil.rmtree(ARTICLES_DIR)
    _git('clone', '--depth=1', ARTICLES_REPO_URL, ARTICLES_DIR)


def sync_articles():
    """Update the articles repo if upstream moved. True if the files changed."""
    if not os.path.isdir(os.path.join(ARTICLES_DIR, '.git')):
        clone_articles()
        return True

    # ls-remote is a single handshake that transfers no objects, so the routine
    # every-10-minutes case costs almost nothing and never pulls a repo.
    remote = _git('ls-remote', ARTICLES_REPO_URL, 'HEAD').split()[0]
    local = _git('rev-parse', 'HEAD', cwd=ARTICLES_DIR)

    if remote == local:
        return False

    _git('fetch', '--depth=1', 'origin', 'HEAD', cwd=ARTICLES_DIR)
    _git('reset', '--hard', 'FETCH_HEAD', cwd=ARTICLES_DIR)
    _git('clean', '-fd', cwd=ARTICLES_DIR)
    return True

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


def build_article_index():
    """Read every article off disk and return one immutable-ish snapshot.

    Everything the request handlers need lives in the returned dict so a refresh
    can swap it in with a single assignment - no half-updated globals.
    """
    tagss = set()
    articless = []
    edit_dates = []

    for filename in os.listdir(ARTICLES_DIR):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(ARTICLES_DIR, filename)
        tagss.update(tags.parse_markdown_tags(filepath))
        articless.append(filename[:-3])

        edit_dates.append(tags.get_article_date(filepath) or None)

    # Sort newest-first once, here, so the handlers only ever read.
    # Undated articles sort last rather than blowing up the None/str compare.
    sorted_pairs = sorted(zip(edit_dates, articless),
                          key=lambda pair: (pair[0] or '', pair[1]), reverse=True)
    edit_dates, articless = zip(*sorted_pairs) if sorted_pairs else ((), ())

    file_count, word_count = count_words_in_directory(ARTICLES_DIR)

    return {
        'tags': tagss,
        'articles': articless,
        'edit_dates': edit_dates,
        'total_articles': file_count,
        'total_words': word_count,
    }


def _refresh_articles():
    """Background worker: check upstream, rebuild the index if anything moved."""
    global article_index
    global _sync_in_flight

    try:
        if sync_articles():
            article_index = build_article_index()
            print('Articles updated from upstream')
    except (subprocess.SubprocessError, OSError) as e:
        # Keep serving the copy we already have and try again next interval.
        print(f'Article sync failed: {e}')
    finally:
        with _sync_lock:
            _sync_in_flight = False


@app.before_request
def refresh_articles_if_stale():
    """Let a visitor trigger a sync, but never make them wait on it.

    The request is served from the articles already on disk; whoever shows up
    after the background thread finishes gets the new ones.
    """
    global _last_sync_check
    global _sync_in_flight

    now = time.monotonic()

    with _sync_lock:
        if _sync_in_flight or now - _last_sync_check < ARTICLES_SYNC_INTERVAL:
            return
        _last_sync_check = now
        _sync_in_flight = True

    threading.Thread(target=_refresh_articles, daemon=True).start()


if not os.path.isdir(os.path.join(ARTICLES_DIR, '.git')):
    clone_articles()

article_index = build_article_index()
_last_sync_check = time.monotonic()

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

    if not Path("articles/"+article+".md").exists():
        return render_template('404.html')

    filepath = "articles/"+article+".md"
    metadata, content_start = tags.parse_metadata(filepath)

    edit_date = metadata.get('date') or None

    with open(filepath, 'r') as file:
        content = file.readlines()

        content = content[content_start:]

        title = next((item for item in content if item.startswith('#')), None)[2:]
        content = ''.join(content)

    total_words = len(content.split())

    # Convert Markdown to HTML
    html = markdown.markdown(content, extensions=MARKDOWN_EXTENSIONS)

    # Render the HTML with a template
    return render_template('article.html', content=html, title=title, total_words=total_words, edit_date=edit_date)

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

#@app.route('/pseudo_resume')
#@app.route('/pseudo-resume')
#def pseudo_resume_page():
#    """Interactive version of articles/Pseudo Resume.md."""
#    return render_template(
#        'pseudo_resume.html',
#        search_blob=pseudo_resume.search_blob,
#        **pseudo_resume.page_data()
#    )

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
    with open("articles/Boilerplate.md", "r") as readme_file:
        html = markdown.markdown(readme_file.read(), extensions=MARKDOWN_EXTENSIONS)

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
