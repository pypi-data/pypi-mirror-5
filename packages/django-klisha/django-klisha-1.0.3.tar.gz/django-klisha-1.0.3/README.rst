
===============================
klisha - Django-based photoblog
===============================

klisha is a standards-compliant and responsive photoblog web application, 
written in Python and uses the Django web framework.

.. figure:: https://raw.github.com/zenzire/django-klisha/master/docs/images/responsive.png
   :alt: Responsive design


Installation
============

Create a virtualenv
-------------------

::

    ~$ virtualenv ~/django-klisha
    ~$ cd ~/django-klisha
    ~$ source ./bin/activate

Clone the code
--------------

::

    ~$ git clone https://github.com/zenzire/django-klisha.git

Install required pip packages
-----------------------------

::
    
    (django-klisha):~$ cd django-klisha/klisha
    (django-klisha):~/django-klisha$ pip install -r requirements.txt

Launch the server
-----------------

::

    (django-klisha):~/django-klisha$ python manage.py runserver 0.0.0.0:8080



klisha-powered sites
====================

* http://www.mierzejewski.net - Captured Moments


Release notes
=============

Version development (unreleased):
---------------------------------


Version 1.0.2 (2013-Aug-14):
----------------------------

* Admin: Added vertical display of the tags' filter interface
* Updated Django from 1.5.1 to 1.5.2
* Updating Description, Screenshots and Installation paragraphs in README.rst file

Version 1.0.1 (2013-Aug-05):
----------------------------
  
* Added links to the next and the previous picture on picture detail page
* Added KLISHA_WEBSITE_DESCRIPTION optional parameter to settings
* Added Installation and Release notes paragraphs in README.rst file
 
Version 1.0.0 (2013-Jul-25):
----------------------------

* Initial version


