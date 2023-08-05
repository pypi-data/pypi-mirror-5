Switter app description
=======================

Switter is a drop-in Django app that gets tweets for you, keeps them cached for a short while and makes it easy to display them on your site:

- **backend** part - fetches and caches tweets from Twitter 1.1 API,
- **frontend** part - is slightly modified version of a popular **jquery.tweet.js** plugin, that uses Switter backend instead of talking directly to Twitter API,
- **django-cms plugin** that makes use of Switter backend and forntend in an easy and pleasant way: when cached tweets are fresh enogh, it doesn't even make any ajax call, they're rendered right away.



Installation
============

* To install ::

    pip install django-switter

* Add ``'switter'`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        # other apps
        "switter",
        "switter.plugins",  # this one is for django-cms
    )

* Add Switter url patterns to your main urls.py ::

    urlpatterns = patterns('',
        ...
        url(r'^switter/', include('switter.urls')),
        ...
    )

* And update your database::

    python manage.py migrate switter
    python manage.py migrate switter.plugins


* Or just ``syncdb`` if you don't use South migrations::

    python manage.py syncdb



Usage
=====

* Register a Twitter app, get your Twitter OAuth credentials and put them into your settings.py ::

    SWITTER_CONSUMER_KEY = '...'
    SWITTER_CONSUMER_SECRET = '...'
    SWITTER_ACCESS_TOKEN = '...'
    SWITTER_ACCESS_TOKEN_SECRET = '...'

* Once installed it's pretty straighforward to use cms plugin - just add it yo your pages! ::

* Fine tune Switter plugin by overriding ``cms/plugins/switter/default.html`` template ::

    {# cms/plugins/switter/default.html #}
    {% load sekizai_tags %}

    <section class="switter" id="switter-{{ object.id }}">
        {% if object.header %}
            <h2>{{ object.header }}</h2>
        {% endif %}

        <ul class="tweets">{# loading... #}</ul>
    </section>

    {% addtoblock "js" %}
        <script type="text/javascript">
            $(function(){
                $('#switter-{{ object.id }} .tweets').switter({
                    // these 3 are Switter-specific:
                    url: '{% url switter_tweets query_type=object.query_type %}',
                    url_params: {{ object.get_jquery_ajax_data|safe }},
                    preloaded_tweets: {{ object.get_tweets_json|safe }},

                    // put the rest of your usual jquery.tweet.js configuration here...
                    count: {{ object.count }},
                    loading_text: "Oooh, loading tweets...",

                    // for example fancy tweet template: 
                    template: '<p>{text}</p><a class="tweet_time" href="{tweet_url}">{time}</a> <a class="tweet_user" href="{user_url}">by @{screen_name}</a>'
                });
            });
        </script>
    {% endaddtoblock %}


* Not using django-cms? Not a problem! Just use modified Switter plugin template code and include it in your templates ::

    {# my/fancy/switter/_tweets.html to be included here and there #}
    <section id="switter">
        <h2>Our tweets</h2>
        <ul class="tweets"></ul>
    </section>

    {# you probably want to paste this in the bottom of your base.html #}
    <script type="text/javascript">
        // add this javascript at the bottom of your base.html template
        $(function(){
            // get user timeline...
            var switter_url = '{% url switter_tweets query_type='user_timeline' %}'
            var switter_url_params = {
                screen_name: 'verybritishproblems',
                count: 5,
                exclude_replies: false, // optional
                include_rts: true // optional
            }

            // or any Twitter search results:
            var switter_url = '{% url switter_tweets query_type='search' %}'
            var switter_url_params = {
                q: 'from:verybritishproblems', // twitter search query
                count: 5
            }

            $('#switter .tweets').switter({
                // these 3 are Switter-specific:
                url: switter_url, 
                url_params: switter_url_params,
                preloaded_tweets: {{ my_cached_tweets_json|safe }}, // optional (will ajax for tweets if not present)

                // put the rest of your usual jquery.tweet.js configuration here...
                count: 5
            });
        });
    </script>

