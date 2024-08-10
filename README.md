# Blog

Internal use blog storage

Topic/branches

hpc
programming
security
security/cryptography
boilerplate

Each article.md file has the tags on the first line, and the name of the file is the title of the article


TODO:
    - Make tags case insensitive
    - Come up with a blog name
    - Pass article name to tab title
    - List articles by date posted
    - Allow articles to not have tags and not have the first line of file appear in the tags section of
    - Add a linked table of contents to the boilerplates
    - Consider adding an admin page to tell it to update and usage monitoring (dashboard of how many people, especially unknown people for private pages like /olympics)
    - Research forwarding traffic to another service (IE forwarding domain.tld/minecraft to the minecraft server)
    - Make it index all articles when the server boots up. I designed the tag and article search system to grab all of the tags and article names from the files, assuming that they could be hot swapped, but I can't, so I might as well switch to a one time generated index
    - Remove metadata from /static/files