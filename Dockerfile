FROM docker.io/alpine:latest

# Install dependencies
RUN apk update
RUN apk add python3

# Create user and switch
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app/blog
RUN chown appuser:appgroup /app/blog
USER appuser

# Alpine's system Python is externally managed (PEP 668), so pip can't
# install into it. A venv sidesteps that and needs no py-pip/ensurepip.
RUN python3 -m venv /app/blog/.venv

# Requirements first so code/article edits don't redo the pip install
COPY --chown=appuser:appgroup requirments.txt .
RUN /app/blog/.venv/bin/pip install -r requirments.txt

# Build from the local checkout (articles included). See .dockerignore.
COPY --chown=appuser:appgroup . .

# There's no .git in the image, so main.py reads the commit hash from here.
# Pass it with: --build-arg GIT_COMMIT=$(git rev-parse --short HEAD)
ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT

EXPOSE 5000

CMD ["/app/blog/.venv/bin/python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--access-logfile", "-", "main:app"]
