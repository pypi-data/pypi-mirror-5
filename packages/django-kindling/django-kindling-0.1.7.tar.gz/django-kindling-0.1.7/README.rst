django-kindling
===============

To assist set-up of nice Django projects. May later be replaced by a project template.

Quickstart
----------

To get started::

    % mkvirtualenv yourproject
    (yourproject) % pip install git+https://github.com/radiosilence/django-kindling.git
    (yourproject) % kindling yourproject
    (yourproject) % workon yourproject
    (yourproject) % pip install -r yourproject/requirements.txt

Next, I would recommend you update `fabfile.py` to choose a debug port, live domain name, and enable celery (if needed).


Todos
-----

 * Create boilerplate HTML
 * Create boilerplate CSS
