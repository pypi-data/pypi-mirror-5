django-bootstrap-staticfiles
============================

This package provides a Django_ app whose ``static`` folder contains the
compiled assets of Bootstrap_.

Each Bootstrap version will be tagged accordingly.

Setup
-----

1. Install the app::

    pip install django-bootstrap-staticfiles

2. Inlude it in your Django project::

    # settings.py:

    INSTALLED_APPS = (
        ...
        'django_bootstrap_staticfiles',
        ...
    )

3. Make sure ``django.contrib.staticfiles.finders.AppDirectoriesFinder`` is in
   your list of ``STATICFILES_FINDERS``.

Usage
-----

If you're not using an asset manager, you can just include them as usual in
your site templates.::

    {% load staticfiles %}
    ...
    <script type="text/javascript" src="{% static 'js/bootstrap.min.js' %}"></script>
    ...

Copyright and license
---------------------

Copyright 2013 55 Minutes

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

.. _Django: https://www.djangoproject.com
.. _Bootstrap: http://getbootstrap.com
