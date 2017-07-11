FROM node:6

RUN apt-get update \
    && apt-get install -y python-pip \
    && pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*
RUN npm install --quiet -g grunt-cli

COPY ["manage.py", "package.json", "example-config.json", "setup.py", "frontendbuild.sh", "Gruntfile.js", ".babelrc", ".eslintignore", ".eslintrc", "/app/src/"]
COPY ["regulations", "/app/src/regulations"]
COPY ["fr_notices", "/app/src/fr_notices"]
WORKDIR /app/src/
RUN ./frontendbuild.sh
RUN pip install --no-cache-dir -e . \
    && python manage.py migrate

ENV PYTHONUNBUFFERED="1"
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
