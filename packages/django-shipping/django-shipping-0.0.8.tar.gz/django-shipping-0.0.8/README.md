django-shipping
===============

Django Shipping is a django application that provides integration with Correios (federal brazilian carrier) and UPS (international carrier).


## Installation

Anyway, let's install this bitch! The first thing you'll want to do is run:

``` bash
$ pip install django-shipping
```

Put ``shippging`` in your ``INSTALLED_APPS``:

``` python
# settings.py

INSTALLED_APPS = (
    # ...
    'shipping',
)

```

Put ``shipping.urls`` in your ``urls.py``:

``` python
# urls.py

from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # ...

    url(r'^shipping/', include('shipping.urls')),
    url(r'^admin/', include(admin.site.urls)),
))

```


You need to run shipping migrations. We use [south](http://south.readthedocs.org/en/latest/index.html) for this, go to your ``project`` dir and make:

``` bash
$ python manage.py migrate shipping
```

## Using

Now, start your django application and go to admin:

``` bash
$ python manage.py runserver
```

In django's admin you wi'll see the shipping models: ``Zone``, ``Country``, ``State``, ``Bin``, ``UPSCarrier`` and ``CorreiosCarrier``. You need to create one instance for each carrier that you'll use
for shipping.
