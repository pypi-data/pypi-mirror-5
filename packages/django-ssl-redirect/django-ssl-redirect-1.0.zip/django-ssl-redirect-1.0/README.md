Django SSL Redirect
===================

Django SSL Redirect is a middleware that ensures secured URLs and only secured URLs are accessed securely over HTTPS.

Installation
------------

Run `pip install django-ssl-redirect`

Securing Views
--------------

To secure a view simply add `'SSL': True` the views kwargs

```python
urlpatterns = patterns('my_app.views',
    url(r'^secure/path/$', 'secure_view', {'SSL':True}),
)
```

Settings
--------
Use secure redirects.

`USE_SSL (default True)`

Name of the view kwarg.

`SSL (default 'SSL')`

Port number of the SSL connection. If not None it is appended after the host.

`SSLPORT (default None)`

A list of secure paths.

`HTTPS_PATHS (default [])`