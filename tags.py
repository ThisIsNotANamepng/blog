import os

def parse_metadata(filename):
    """Parse key:value metadata lines from the top of a markdown file.
    Returns a dict of metadata (e.g. {'tags': [...], 'date': '2025-01-01'})
    and the line index where content (non-metadata) begins.
    """
    metadata = {}
    content_start = 0

    with open(filename, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '':
            content_start = i + 1
            continue
        if ':' in stripped and not stripped.startswith('#'):
            key, _, value = stripped.partition(':')
            key = key.strip().lower()
            value = value.strip()
            if key == 'tags':
                metadata['tags'] = [t.strip() for t in value.split(',') if t.strip()]
            else:
                metadata[key] = value
            content_start = i + 1
        else:
            break

    if 'tags' not in metadata:
        metadata['tags'] = []

    return metadata, content_start


def parse_markdown_tags(filename):
    metadata, _ = parse_metadata(filename)
    return metadata.get('tags', [])


def get_article_date(filename):
    metadata, _ = parse_metadata(filename)
    return metadata.get('date', '')


def get_articles_with_tag(tag, directory):
    articles = []
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            filepath = os.path.join(directory, filename)
            article_tags = parse_markdown_tags(filepath)
            if tag in article_tags:
                articles.append({'title': filename[:-3], 'tags': article_tags})
    return articles
