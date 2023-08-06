Django Resizer
==============

Django Resizer allows images to be dynamically resized and/or cropped through a URL. This is very useful when you have a third-party "hot-linking" your images and they won't have access to template tag to dynamically resize images like [easy-thumbnails](https://github.com/SmileyChris/easy-thumbnails) or [sorl-thumbnail](https://github.com/sorl/sorl-thumbnail) provides.

Installation
------------

Run `pip install django-resizer`

Add `resizer` to your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = (
    ...
    'resizer',
)
```

To your sites `url.py` add:

```python
urlpatterns = patterns('',
    ...
    url(r'^resizer/(?P<path>.*)/$', 'resizer.views.resize', name='image_resize'),
)
```

Usage
-----

The resizing and cropping capabilities rely on the easy-thumbnails app.

To resize an image with a height and width of no more than 50px and with the image ratio perserved:

`/resizer/images/picture.jpg?size=50,50`

The path after `/resizer` should be the path to the image from your settings `MEDIA_ROOT`. The query string should be `size=[width],[height]`.

To resize an image to have a height and width of extactly 50px:

`/resizer/images/picture.jpg?size=50,50&crop=smart`