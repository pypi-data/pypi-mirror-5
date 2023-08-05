==============
Flask-Upstatic
==============

Opinionated library for working with CDNs in Flask.


-------------
Configuration
-------------

================================= ===============================================
``UPSTATIC_DEBUG_USE_LOCAL``      Whether to use local version when in debug mode
``UPSTATIC_S3_ACCESS_KEY_ID``     S3 Access Key ID
``UPSTATIC_S3_SECRET_ACCESS_KEY`` S3 Secret Access Key
``UPSTATIC_S3_BUCKET_NAME``       S3 Bucket Name
``UPSTATIC_S3_KEY_PREFIX``        S3 Key Prefix
``UPSTATIC_S3_CDN_HOST``          S3 CDN Host
================================= ===============================================

-----
Usage
-----

Initialize extension::

  upstatic = Upstatic(app)
  # or
  upstatic = Upstatic()
  upstatic.init_app(app)

Add a static root::

  upstatic.add_root('home', '/abs/path/static')
  upstatic.add_root('home', 'rel/path/static')

Override ``url_for``::

  app.add_template_global(upstatic.url_for)

Set a ``root`` param in ``url_for`` to get static file from named root::

  <img src="{{ url_for('static', filename='/images/image.png', root='home') }}">

You can also add static roots from packages::

  upstatic.add_root('home', 'static', package_name='home')

Add a ``root_url`` to override url building for multiple apps scenarios::

  upstatic.add_root('admin', 'static', package_name='admin',
                    root_url='http://localhost:5000/admin/static')

Compile and upload the static files::

  upstatic.upload_all('home', 'admin', protocol='http')
