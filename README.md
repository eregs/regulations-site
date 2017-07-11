regulations-site
================
[![Build Status](https://travis-ci.org/eregs/regulations-site.svg?branch=master)](https://travis-ci.org/eregs/regulations-site)
[![Dependency Status](https://gemnasium.com/badges/github.com/eregs/regulations-site.svg)](https://gemnasium.com/github.com/eregs/regulations-site)
[![Code Climate](https://codeclimate.com/github/eregs/regulations-site/badges/gpa.svg)](https://codeclimate.com/github/eregs/regulations-site)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/423b7d7702754ff4baa8715465d75bbf/badge.svg)](https://www.quantifiedcode.com/app/project/423b7d7702754ff4baa8715465d75bbf)

A Django library implementing an interface for viewing regulations data. This
library combines all of the data from a parsed regulation and generates
navigable, accessible HTML, complete with associated information.

This repository is part of a larger eRegulations project. To read about it, please see
[https://eregs.github.io/](https://eregs.github.io/).

## Requirements

This library requires
* Python 2.7, 3.4, 3.5, or 3.6
* Django 1.8, 1.9, 1.10, or 1.11
* Node 6 or later

## API Docs

[regulations-site on Read The Docs](https://regulations-site.readthedocs.org/en/latest/)

## Local development

This library lives in two worlds, roughly translating to a Python Django app
and a Backbone Javascript app, which communicate through the Django templates.
To work on the library locally, you'll need to install components for both
systems.

We use [tox](https://tox.readthedocs.io) to test across multiple versions of
Python and Django. To run our Python tests, linters, and build our docs,
you'll need to install `tox` *globally* (Tox handles virtualenvs for us).

```bash
pip install tox
# If using pyenv, consider also installing tox-pyenv
```

The front-end development environment relies on on Node (version 6+) and npm
for package management. To install Node, we recommend
[nvm](https://github.com/creationix/nvm):

```sh
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.30.2/install.sh | bash # install nvm and run it's setup scripts
nvm install 6 # install node 6
nvm alias default 6 # set node 6 as the default
```

Alternately you can install Node by:

- Install a binary or installer from http://nodejs.org/download/
- If you're on OS X, you can use [Homebrew](http://brew.sh/)

Finally, you will need to install the frontend dependencies and Grunt command
line interface using npm:

```sh
cd regulations-site
npm install
npm install -g grunt-cli
```

Once all of the above is complete, you may run tests and linting across
available Python versions:

```sh
tox
```

Or run JS unit tests:

```sh
tox -e jstests
```

There are also a number of Grunt tasks (see below) to compile CSS, lint JS,
etc.

### Running as an application

While this library is generally intended to be used within a larger project,
it can also be ran as its own application via [Docker](https://www.docker.com)
or a local Python install. In both cases, we'll run in `DEBUG` mode.

Before we can run as an application, we'll need to define where it should look
for data. For example, to pull from ATF's data:

```sh
echo 'API_BASE = "https://regulations.atf.gov/api/"' >> local_settings.py
```

To run via Docker,
```bash
docker build . -t eregs/site   # only needed after code changes
docker run -p 8000:8000 eregs/site
```

To run via local Python, run the following inside a
[virtualenv](https://virtualenv.pypa.io/en/stable/):
```bash
pip install .
python manage.py migrate
./frontendbuild.sh
python manage.py runserver 0.0.0.0:8000
```

In both cases, you can find the site locally at
[http://localhost:8000](http://localhost:8000)

## JavaScript application 
The application code in JavaScript uses [Backbone.js](http://backbonejs.org/) as a foundation, though in some non-standard ways. If you plan to do work on this layer, it is recommended that you acquaint yourself with this [starter documentation](README_BACKBONE.md).

### Configuration JSON

In the root of the repository, copy `example-config.json` to `config.json` and edit as necessary. Grunt depends on these settings to carry out tasks.
- `testURL` is the environment that you would like tests to run on.
- `frontEndPath` is the path to the root of your codebase where the `css/` and `js/` directories are.
- `testPath` is the path to the functional test specs.

### Running Grunt tasks
There are a number of tasks configured in [Gruntfile.js](Gruntfile.js). On the
last lines, you will find tasks that group subtasks into common goals. These
include:

* `grunt test` runs JS lint and unit tests.
* `grunt mocha_stanbul` runs only JS unit tests.
* `grunt build-dev` builds a development version of the frontend assets.
* `grunt build-dist` or just `grunt` builds a production version of the
  frontend assets (including minification, etc.)

## Integration tests

We have a set of integration (or "functional") tests which run the library
through its paces and makes assertions by running a full browser. This
requires [Selenium](http://www.seleniumhq.org/) and may make use of [Sauce
Labs](https://saucelabs.com) for testing additional browsers.

### Configuration

By default, selenium runs tests via the [PhantomJS](http://phantomjs.org/)
browser (which requires separate installation). Alternatively, you can specify
which local browsers to test via the `UITESTS_LOCAL` environment variable,
e.g. "chrome".

To utilize Sauce Labs for a more complete set of browsers, you will need to
define two envrionment variables: `SAUCE_USERNAME` and `SAUCE_ACCESS_KEY` to
house account info. You'll also need to specify which browsers to test via the
`UITESTS_REMOTE` environment variable.

### Running

If running via Sauce Labs, you will first need to download and run [Sauce
Connect](https://saucelabs.com/docs/connect).

Then, you'll need to run the library as an application (see above) first;
we'll assume it's running on port 8000. See
[devops/integration-tests.sh](devops/integration-tests.sh) for an example
which utilizes Docker-compose.

Finally, to run the tests, execute

```sh
UITESTS_URL=http://localhost:8000 UITESTS_REMOTE=ie11 tox -e integration
# or
UITESTS_URL=http://localhost:8000 UITESTS_LOCAL=chrome tox -e integration
```

## Customization

To learn about customizing the templates and styles for an instance, see [Theming an instance](https://eregs.github.io/theming/).
