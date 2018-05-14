FROM node:6
ARG PYTHON3=3
ENV PIP_PACKAGE=python${PYTHON3}-pip \
    PIP_CMD=pip$PYTHON3 \
    PYTHON_CMD=python$PYTHON3

RUN apt-get update \
    && apt-get install -y $PIP_PACKAGE \
    && rm -rf /var/lib/apt/lists/*
RUN $PIP_CMD install --upgrade pip setuptools
RUN npm install --quiet -g grunt-cli

COPY ["manage.py", "package.json", "example-config.json", "setup.py", "frontendbuild.sh", "Gruntfile.js", ".babelrc", ".eslintignore", ".eslintrc", "/app/src/"]
COPY ["regulations", "/app/src/regulations"]
COPY ["fr_notices", "/app/src/fr_notices"]
COPY ["notice_comment", "/app/src/notice_comment"]
WORKDIR /app/src/
RUN ./frontendbuild.sh
RUN $PIP_CMD install --no-cache-dir -e .[notice_comment] \
    && $PYTHON_CMD manage.py migrate

ENV PYTHONUNBUFFERED="1"
EXPOSE 8000
CMD $PYTHON_CMD manage.py runserver 0.0.0.0:8000
