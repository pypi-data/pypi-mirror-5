=================
Building projects
=================

Editing templates
-----------------

Tarbell projects consist of simple HTML pages that may use Jinja templating features.

If you create a file in your project directory called `chapter1.html`, you'll be able to
preview the file at http://localhost:5000/chapter1.html and publish to the same file. This
file can be straight up HTML, or it can inherit from a base template.

Files and directories that start with an underscore (`_`) or a dot (`.`) will not be 
rendered by the preview server or included in the generated static HTML.

Understanding the base template
-------------------------------

Base templates live in your projects `_base` directory, and use Jinja templating features to 
make your life easier. Develop base templates to use for projects that need to share boilerplate 
code like advertising, analytics, and common page elements. Tarbell projects are intended to
inherit from base templates.

Here's a simple `_base/_base.html`::

  <html>
    <head>
      <title>{{ title }}</title>
      {% block css %}
      <link rel="stylesheet" type="text/css" href="css/style.css" />
      {% endblock css %}
    </head>
    <body>
      {% block content %}{% endblock content %}
    </body>
  </html>

To inherit from this template extend the base template in `index.html` or other project files you
create. Now, all your `index.html` needs to contain is::

  {% block content %}
  <h1>{{ title }} </h1>
  {{ content|markdown }}
  {% endblock content %}

You might notice we're using the `|markdown` filter. Base templates also define filters. See 
building base templates for more.

If a base template defines a static file or template (e.g. `_base/style.css`), it will be available
relative to the project's base path (e.g. http://127.0.0.1:5000/style.css). If a project defines 
a file with the same name, the project's version will be used instead.

See the basic Tarbell template for a simple implementation of a base template.


Configuring projects
--------------------

Project configuration is kept in the `tarbell.py` file in your project's base directory::

  # -*- coding: utf-8 -*-

  """
  Tarbell project configuration
  """

  # Short project name
  NAME = "nellie-bly"

  # Descriptive title of project
  TITLE = "The Story of Nellie Bly"

  # Google spreadsheet key
  # SPREADSHEET_KEY = "0Ak3IIavLYTovdC1qMFo5UDEwcUhQZmdZbkk4WW1sYUE"

  # S3 bucket configuration
  S3_BUCKETS = {
      "staging": "s3://projects.beta.myorg.tld/profiles/nellie-bly/",
      "production": "s3://projects.myorg.tld/profiles/nellie-bly/",
  }

  # Repository this project is based on (used for updates)
  TEMPLATE_REPO_URL = "https://github.com/newsapps/tarbell-template"

  # Default template variables
  DEFAULT_CONTEXT = {
      'name': 'nellie-bly',
      'title': 'The Story of Nellie Bly'
  }

`TITLE` and `NAME` are required and describe the project.

If specified, `SPREADSHEET_KEY` will be used as data source if Google Spreadsheets is configured.

If specified, `S3_BUCKETS` should be a Python dict consisting of `targetname`->`targeturl` pairs.

If specified, `TEMPLATE_REPO_URL` will be used to pull in updates to the base template. 

If specified, `DEFAULT_CONTEXT` will provide context variables to the template. The default context
is dictionary of `key`->`value` pairs to provide to the template. The `value` may be any Python
object that can be represented as a Jinja template variable.

Using context variables
-----------------------

Template data comes from Google spreadsheets or tarbell.py's `DEFAULT_CONTEXT`.

This simple `DEFAULT_CONTEXT` shows many of the key template features::

  DEFAULT_CONTEXT = {
      'name': 'nellie-bly',
      'title': 'The Story of Nellie Bly',
      'font_size': '20px',
      # Nested dictionary
      'photos': {
          'intro': {
              'url': 'img/bly01.jpg',
              'caption': 'A caption',
          }
      },
      # Nested list
      'timeline': [
          {'year': '1902', 'description': 'Description...'},
          {'year': '1907', 'description': 'Description...'},
          {'year': '1909', 'description': 'Description...'},
      ],
    }
  }

To print the title in your template, use `{{ title }}`::

  <h1>{{ title }}</h1>

Address a nested dictionary::

  <img src="{{ photos.intro.url }}" alt="{{ photos.intro.caption }}" />
  <aside>{{ photos.intro.caption }}</aside>

Access a list of data::

  <ul>
    {% for year in timeline %}
    <li><strong>{{ year }}</strong>: {{ description }}</li>
    {% endfor %}
  </ul>

Where can context variables be used?
------------------------------------

Context variables can be used in HTML, CSS, and Javascript files. If the text file causes a Jinja
template error (which can happen if the file has Jinja-like markers), the file will be served as static
and the preview server will log an error.

This means that CSS and Javascript files may include variables. `style.css` might include::

  #content { font-size: {{ font_size }}; }

Similarly, a Javascript file could include::

  var data = {{ photos|tojson }}
  console.log(photos.intro.url);

Use this feature with care! Missing variables could easily break your CSS or Javascript.
