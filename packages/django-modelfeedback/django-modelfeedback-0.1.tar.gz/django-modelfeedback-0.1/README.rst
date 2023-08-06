=======================
 Model Feedback v0.0.1
=======================

.. image:: https://travis-ci.org/yokomizor/django-modelfeedback.png?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/yokomizor/django-modelfeedback

.. image:: https://coveralls.io/repos/yokomizor/django-modelfeedback/badge.png?branch=master
   :alt: Coverage Status
   :target: https://coveralls.io/r/yokomizor/django-modelfeedback

Adds support for receive feedback to django models using Likert scale.

Detailed documentation is in `Model Feedback Github Page`_.


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


.. _Model Feedback Github Page: https://github.com/yokomizor/django-modelfeedback/wiki
