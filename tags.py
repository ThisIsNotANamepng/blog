# Reads all of the tags in the articles/ directory and makes a 2 list of all articles, each list has [article name, tag1, tag2, tag3], also makes a list of all unique tags

import os

def parse_markdown_tags(filename):
    with open(filename, 'r') as file:
        content = file.read().split('\n')
        tags = content[0].split(',')

        if "#" in tags[0]:
            # This is the title, there are no tags for this article
            return ''
        
    return tags

def get_articles_with_tag(tag, type):
    # type is 'articles' or 'research'

    articles = []
    for filename in os.listdir(type):
        if filename.endswith('.md'):
            filepath = os.path.join(type, filename)
            tags = parse_markdown_tags(filepath)
            if tag in tags:
                articles.append({'title': filename[:-3], 'tags': tags})
    return articles
