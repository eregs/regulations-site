Django Architecture
===================

Traditional Django apps contain models to store and retrieve data from a
database, templates with which to convert these models into HTML, and thin
views to connect the two. Generally, each request loads some subset of the
models and shoves them through a template.

Regulations-site differs in some fundamental ways. It is model-less, at least
in the Django sense; it loads data from an external API and represents the
results as a ``dict`` (as opposed to converting them into objects). Rather
than use a single template per request, the templating layer is used
frequently and recursively; single requests may often trigger *dozens* (in
some cases, *hundreds*) of templates to be processed. As a result, caching is
critical to the application; we buffer AJAX calls in the browser, rendered
templates, template file lookup, and API results.

Here, we'll dive into several of these components to get a sense of their
general workings as well as history and context which led to their creation.
We'll highlight the more abnormal bits, shining light on warts.

Generator
---------

The eRegs UI was originally built as a simple HTML generator, rendering an
*entire* regulation. As a result, much of the logic has lived in the
``generator`` module, which has largely no conception of the HTTP
request/response life-cycle. Instead, it is aware of a connection to a backend
API, how to associate the types of data served by that API with each other,
and how to render the results as HTML.

The ``HTMLBuilder`` class is king, primarily due to its ``process_node()``
method, which takes "node" data (i.e. a plain text representation of a
regulation, structured as a tree of nested paragraphs) and combines it with
"layer" data (i.e. meta/derived data about the tree, such as citations,
definitions, etc.) and converts them into HTML. For each node in the tree,
layers are applied (see below) in sequence, each successively extending and
replacing the node's ``"marked_up"`` field with HTML corresponding to the
layer's updates. Each node (still represented as a ``dict``) is also given
extra attributes which will be used when rendering the Node in templates. To
summarize, the ``HTMLBuilder`` effectively adorns Nodes with new fields,
including one representing the Node's text, as HTML.

Within Django's views, the resulting Node structure is passed off to a
template. This time the tree is walked *within the template*, such that each
Node is converted into an appropriate chunk of HTML and concatenated with its
siblings. Perhaps confusingly, templates are passed the Node data as a
"skeleton" of a full regulation -- the single section (or whatever component
we care about) is "wrapped" with empty Nodes until it looks like a full
regulation. This means that, from the template perspective, there is largely
only *one* entry point for views, regardless of whether that view is
generating a section, a single paragraph, or an entire regulation. The
practice no doubt stems from the original, full-regulation-generation
functionality.

  There's a tremendous amount of refactoring that should happen here. We
  shouldn't be walking the tree twice (once within ``HTMLBuilder`` and once
  within the templates) -- it'd make more sense to remove the former altogether.
  Further, a conversion from the ``dict`` to a class would seem appropriate, to
  make it obvious where to look for functionality. Though the skeleton concept
  has merit, the hoops it causes us to jump through are rather strange. Perhaps
  a better solution would be to select an appropriate template automatically
  based on its type, position in the tree, etc.

Views
-----

There are three primary categories for our views: "sidebar", "partial", and
"chrome". The first two stem from our AJAX needs; for browsers with the
capability, we AJAX load in content as the user clicks around. The "partial"
endpoints correspond to the center content of the page (e.g. a regulation
section, search results, the diff view, etc.). When a user clicks to load a
new section, their browser will make two AJAX requests, one for the center
content and one for the sidebar content.

The "chrome" endpoints wrap these two other types of views with navigation,
CSS includes, headers, etc. (i.e. the application's "chrome"). These endpoints
are crucial for users without JavaScript (or modern implementations of the URL
push API) and for initial loading (e.g. via hard refreshes, bookmarks, etc.).

  We currently have far too many *different* views, despite them performing
  largely the same types of tasks. It would make more sense to combine all of
  the "node" views into a single class. Similarly, we *mirror* each "partial"
  view class with a "chrome" class; a more effective strategy would be to have
  a more generic ``wrap_with_chrome`` method and no distinct "chrome" classes.
  This should also remove the incredibly nasty manipulations of Django's
  request/response life cycle we're currently performing to populate the
  chrome version. Somewhat related, having a separate endpoint for the sidebar
  and a separate endpoint for partials didn't turn out as useful as we
  expected.  It probably makes sense to combine them again.

Layers
------

We have a handful of layer generating classes, which know how to apply data
from a layer API on to regulation text. While many of these classes correspond
to a *single* data layer, this is not a hard rule. Indeed, we currently have
*two* layer classes associated with the definition data -- one handles when
terms are *defined* while the other handles when they are *used*.  As noted
above, layers are applied within the ``HTMLBuilder`` and live inside the
``generator`` package. Which layers are used depends on the ``DATA_LAYERS``
setting. Individual requests can also request a subset of these, though that
functionality is rarely used.

Layers fall into three categories:

- "inline", where the layer defines exact text offsets in the Node's text.
  Internal citations (linking to another paragraph or section within the
  current regulation) are an example. They have data like:

  .. code-block:: python

    {"111-22-c": [{"offsets": [[44, 52], ...],  # string index into the text
                   # Layer specific fields
                   "citation": ["111", "33", "e"]},
                  ...],
     ...}


- "search-and-replace", where the layer includes snippets of text (rather than
  offsets). External citations (linking to content outside of eRegs) are an
  example. They look like:

  .. code-block:: python

    {"111-22-c": [{"text": "27 CFR Part 478", # exact text match
                   "locations": [0, 2, 3],    # skips the second reference
                   # Layer specific fields
                   "citation_type": "CFR",
                   "components": {...},
                   "url": "http://example.com/..."},
                  ...],
     ...}

- "paragraph", where the layer data is scoped to the full paragraph. The
  table-of-contents layer is an example here. All fields are specific to the
  individual layer. For example:

  .. code-block:: python

    {"111-Subpart-C": [{"title": "Section 111.22 A Title",
                        "index": ["111", "22"]},
                       ...]
     ...}
    

The first two categories are needed when we want to modify some component of a
Node's text (e.g. a citation, definition, or formatting adjustment). In these
scenarios, the generator provides the original text and the layer data to a
corresponding template, which is then responsible for returning appropriate
HTML. "Search-and-Replace" is the newer model, offering both better legibility
of layer data as well as resiliency to minor errors at the cost of concision.

The "paragraph" layer types return a key and value which will be passed
through to the template for rendering a full Node. These are largely used for
"meta" data, such as the table of contents, section-wide footnotes, and data
which would appear in the sidebar.

  The main pain point here is the rather strange way that data is provided;
  the layer data structure points *into* the tree, spelling out specific
  chunks of text. An XML or similar structured document format would make much
  more sense. "Paragraph"-type layers could be attributes of the parent
  element or meta-data tags.
