#DJANGO-RELINKING

Django-relinking application adds function and template filter for relinking custom text.


Installation
------------------------
1. Run from command line "pip install django-relinking"
2. Add "django_relinking" to INSTALLED_APPS in your settings package
3. Run migrations: ``` python manage.py migrate django_relinking ```

Options
------------------------
_If you want you can redefine next options:_
+ __RELINKING_LINK_TEMPLATE__ - template for link tag.
*Default*: ```RELINKING_LINK_TEMPLATE = '<a target="{target}" href="{url}">{text}</a>'```
+ __RELINKING_ENABLE_CACHE__ - enable or disable caching.
*Default*: ```RELINKING_ENABLE_CACHE = False```
+ __RELINKING_CACHE_PREFIX__ - prefix for keys in cache.
*Default*: ```RELINKING_CACHE_PREFIX = "{links_table}.{hash}"```
+ __RELINKING_INDEX_PATTERN__ - temporary pattern for replacting keys to link indexes.
*Default*: ```RELINKING_INDEX_PATTERN =  "<%=link {}=%>"```

Usage
------------------------
*Before usage you must register models or other objects which have ```get_absolute_url``` method:*
```python
from django_relinking.content_types import register

"""
content_type - class of model or view which has method 'get_absolute_url`

verbose_name - human title of content type.
--- verbose_name can be a function. Default is None.
--- If verbose_name is None and content_type has attribute 'verbose_name',
------ then verbose_name = content_type.verbose_name
--- If verbose_name is None and content_type has method 'verbose_name',
------ then verbose_name = content_type.verbose_name()
--- If verbose_name is None and content_type hasn't attribute 'verbose_name'
------ then verbose_name = content_type.__name__

objects - queryset or list of this content_type objects.
--- For example: ``` Model.objects.all() ```.
--- Every objects must have attribute pk and `get_absolute_url` method
--- If objects is None - this content type is a single
--- and it must have `get_absolute_url` method
"""
register(content_type, verbose_name, objects)
```

*Also you can:*
```python
from django_relinking.content_types import register_all, unregister, unregister_all
#
# Register many content types for one time
register_all(content_type1, content_type2, ..., content_typeN)
#
# Unregister registered content type
unregister(content_type)
#
# Unregister all registered content types
unregister_all()
#
# Unregister some registered content types
unregister_all(content_type1, content_type2, ..., content_typeN)
```
____________________________________________________
When you register appropriate content types you can:
____________________________________________________
**In template:**
```html
{% load relinking %}
<!-- Plain text -->
{% filter relink %}
    plain text
{% endfilter %}
<!-- variable -->
{{ model.attr|relink }}
```
**In code:**
```python
from django_relinking import relink_text
relinked = relink_text(some_text_with_keywords)
```
