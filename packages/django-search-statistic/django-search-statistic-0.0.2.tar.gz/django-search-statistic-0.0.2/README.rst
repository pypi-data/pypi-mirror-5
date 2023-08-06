DJANGO-SEARCH-STATISTIC
=======================

Installation
------------
1. pip install django-search-statistic
2. Add search_statistic to settings.INSTALLED_APPS
3. Add 'search_statistic.middleware.CollectStatisticMiddleware' to settings.MIDDLEWARE_CLASSES
4. python manage.py migrate search_statistic

Usage
------
If you want specify content_type and object_pk (default only path is stored) you must add to your views: 
from search_statistic.utils.visits import visit_object


def some_view(request):

   obj = SomeModel.objects.get(pk=pk)

   visit_object(request, obj)


Settings
--------
All settings stored in settings.SEARCH_STATISTIC.
Default value is:

{

    'REDIS_CACHE_SIZE': 1,

    'REDIS_PREFIX': 'django-search-statistic',

    'REDIS_SETTINGS': {

        'db': 1

    },

    'REMOVE_ON_STATUS': [400, 403, 404, 405],

    'default_query_confirm': False,

}

Options REDIS_* are using only where redis are installed.
If REDIS_CACHE_SIZE <= 0 - search queries will storing in redis infinitely.
If REDIS_CACHE_SIZE == 1 - redis isn't using
If REDIS_CACHE_SIZE >= 2 - search queries and visits are storing in cache, but after REDIS_CACHE_SIZE objects in cache they will be saved in DB

If response status code in REMOVE_ON_STATUS all visits with path == current request.path are deleteing.