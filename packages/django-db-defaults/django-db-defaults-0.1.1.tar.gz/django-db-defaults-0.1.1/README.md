# Django DB Defaults

django-db-defaults is an open source Python library that adds the DB level default constraints for Djago model fields.

## Install
There are a few different ways you can install django-db-defaults:

* pip install django-db-defaults
* pip install -e git+https://bitbucket.org/amityadav12/django-db-defaults.git#egg=db-defaults
* Download the zipfile from the [downloads](https://bitbucket.org/amityadav12/django-db-defaults) page and install it.
* Checkout the source: `git clone git://itbucket.org:amityadav12/django-db-defaults.git` and install it yourself.

## Getting Started
* Install django-db-defaults
* Add 'db_defaults' to your installed apps

There are a few different ways you can use django-db-defaults:

#### Enable it project wide
set an settings variables DB_DEFAULTS_ENABLE_ALL_MODELS = True. This will process defaults for all fields of all models.

```python
DB_DEFAULTS_ENABLE_ALL_MODELS = True
```

#### Enable it only for specific models
Add a dict named 'db_defaults' to your models class that contains mapping of field names to their default values. The loader will process defaults for all the fields those has mapping in this dict. To process all fields set DB_DEFAULTS_ENABLE_ALL_FIELDS = True in django settings.

```python
DB_DEFAULTS_ENABLE_ALL_FIELDS = True
```

```python
class AreaMigrate(models.Model):
    name = models.CharField(max_length=100, default='')
    area = models.PositiveIntegerField(default=400)
    is_usable = models.BooleanField(default=False)
    description = models.TextField(default='', blank=True)
    build_date = models.DateField(auto_now=True, auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)

    db_defaults = {'name' : '', 'area' : 400}
```

## Demo application
There is a bundled application named 'demo' with this library. You can follow the steps given below to run that locally and test the library
 
* cd demo
* pip install -r requirements.txt
* Update DB credentials in demo/settings.py file.
* python manage.py syncdb
* python manage.py migrate
* verify that db defaults for all models are correctly reflected in your database.
