========================================
django-static-libs
========================================

Install
=======
``pip install django-static-libs``

Setting
=======
Add app to ``ISTALLED_APPS`` in ``settings.py``::
    
    INSTALLED_APPS = (
        ...
        'static_libs',
        )

Usage
=====
  
template.html::
    
    <html>
        <head>
            <link type="text/css" href="{{ STATIC_URL }}libs/bootstrap/3.0/css/bootstrap.min.css" rel="stylesheet">
        </head>

        <body>
         ...
        </body>
    </html>
    
Libs
====

- Twitter Bootstrap 3.0
- jQuery 1.10.2
- jquery-ui 1.10.3
- jquery.form 3.40
- jquery.cookie 1.3.1

