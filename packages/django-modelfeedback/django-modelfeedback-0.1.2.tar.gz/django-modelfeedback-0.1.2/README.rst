=======================
 Model Feedback v0.1.1
=======================

.. image:: https://travis-ci.org/yokomizor/django-modelfeedback.png?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/yokomizor/django-modelfeedback

.. image:: https://coveralls.io/repos/yokomizor/django-modelfeedback/badge.png?branch=master
   :alt: Coverage Status
   :target: https://coveralls.io/r/yokomizor/django-modelfeedback

.. image:: https://pypip.in/v/django-modelfeedback/badge.png
   :alt: Pypi Version
   :target: https://pypi.python.org/pypi/django-modelfeedback

.. image:: https://pypip.in/d/django-modelfeedback/badge.png
   :alt: Pypi Downloads
   :target: https://pypi.python.org/pypi/django-modelfeedback

Adds support for receive feedback to django models using Likert scale.

Detailed documentation is in `Model Feedback Github Page`_.


Intallation
-----------

.. code-block:: bash

      pip install django-modelfeedback


Quick start
-----------

1. Add "modelfeedback" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'modelfeedback',
      )

2. Include the modelfeedback URLconf in your project urls.py like this::

      url(r'^feedback/', include('modelfeedback.urls')),

3. Run `python manage.py syncdb` to create the feedback models.


Sample Application
------------------

.. code-block:: bash

      cd sample
      pip install -r requirements.txt
      ./manage syncdb
      ./manage runserver

Visit http://127.0.0.1:8000/ to see the sample.

Or visit the `live demo`_.


License
-------

MIT License. See LICENSE file.


.. _Model Feedback Github Page: https://github.com/yokomizor/django-modelfeedback/wiki
.. _live demo: http://modelfeedback.ro.ger.io
