=====
=====
Snikt
=====

Snikt is a web application front end for provisioning new hardware.

`pip install django-snikt` is the preferred way to install this application.

Quick start (with Django Project already set up and Snikt installed)
-----------

1. Add "mac_info" to your INSTALLED_APPS in the settings.py file like this::

      INSTALLED_APPS = (
          ...
          'mach_info',
      )

2. Include the polls URLconf in your project urls.py like this::

      url(r'^home/', include('mach_info.urls',namespace="mach_info")),

3. Run `python manage.py syncdb` to create the mach_info models.

4. Start the development server with `python manage.py runserver`  and visit http://127.0.0.1:8000/admin/
   to monitor the database and possibly make changes.

5. Visit http://127.0.0.1:8000/home/ to use the application.
