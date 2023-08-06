Overview
----------

This is simple-lightweight-zen Django CMS without magic.


Install
-------------

1. Install django-zen
```shell
pip install django-zen
```

2. Add to INSTALLED_APPS
```python
INSTALLED_APPS = (
    ...
    'django_zen',
    'mptt',
    'feincms',
    'redactor',
    ...
)
```

3. Add TinyMCE config
```python
REDACTOR_OPTIONS = {'lang': 'en'}
REDACTOR_UPLOAD = 'uploads/'
```

4. Add Django Zen urls
```python
url(r'', include('django_zen.urls')),
```

Menus
---------

1. Go to Django admin, add menu items. Add Menu ID for root-level menu, e.g. 'main'

2. In templates render menu
```html
{% load menu_tags %}

<ul>
{% menu main %}
    <li class="{% active request menu_item.url %}">
        <a href="{{ menu_item.url }}">{{ menu_item.name }}</a>
        {% if not menu_item.is_leaf_node %}
        <ul>
            <div>
                {{ children }}
            </div>
        </ul>
        {% endif %}
    </li>
{% endmenu %}
</ul>
```

Pages
----------

1. In templates directory create 'pages' direcotry for templates.

2. In Django admin add pages (You may add page to menu or create menu item for page).

3. Go to page url.