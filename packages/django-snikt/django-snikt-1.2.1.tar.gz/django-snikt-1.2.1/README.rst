=====
=====
Snikt
=====

Snikt is a web application front end for provisioning new hardware.

Quick start
-----------

1. Add "mac_info" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'mach_info',
      )

2. Include the polls URLconf in your project urls.py like this::

      url(r'^home/', include('mach_info.urls',namespace="mach_info")),

3. Run `python manage.py syncdb` to create the mach_info models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to monitor the database and possibly make changes.

5. Visit http://127.0.0.1:8000/home/ to use the application.
