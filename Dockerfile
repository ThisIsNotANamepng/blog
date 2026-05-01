FROM dhi.io/alpine-base:3.23-alpine3.23-dev

# Install dependencies
RUN apk update
RUN apk add git
RUN apk add python3
RUN apk add py-pip
RUN python3 -m ensurepip

# Create user and switch
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
RUN chown appuser:appgroup /app
USER appuser

RUN git clone --depth=1 https://github.com/ThisIsNotANamepng/blog.git

# Articles live in a separate repo and are pulled at container startup
ENV ARTICLES_REPO_URL=https://github.com/ThisIsNotANamepng/blog_articles.git

RUN pip3 install -r blog/requirments.txt
WORKDIR /app/blog

# Drop any articles bundled with the code clone — main.py refreshes them on boot.
RUN rm -rf articles

CMD ["python3", "main.py"]