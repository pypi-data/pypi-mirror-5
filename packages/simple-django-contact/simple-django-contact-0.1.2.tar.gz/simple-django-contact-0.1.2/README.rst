====
Simple Django Contact
====

Simple Django Contact form is just that. Something very very simple  
to display and send emails as a contact form.  

This is very early on and while it works, it's nothing to write home about. Let me know features you'd like to see and we'll get them in there.


Quick start
-----------

1. Add "contact" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'simple-django-contact',
      )

2. Include the contact URLconf in your project urls.py like this::

      url(r'', include('simple-django-contact.urls')),

3. Currently no need to sync your DB (phew!)

4. Prosper?