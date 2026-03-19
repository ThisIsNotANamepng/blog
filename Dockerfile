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

RUN pip3 install -r blog/requirments.txt
WORKDIR /app/blog

CMD ["python3", "main.py"]