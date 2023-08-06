Django-Mxit
===========

Middleware for writing Mxit apps with Django.

|django-mxit|_

.. |django-mxit| image:: https://travis-ci.org/praekelt/django-mxit.png?branch=develop
.. _django-mxit: https://travis-ci.org/praekelt/django-mxit

::

    MIDDLEWARE_CLASSES = (
        ...
        'mxit.middleware.RemoteUserMiddleware',
        ...
    )


    AUTHENTICATION_BACKENDS = (
        ...
        'django.contrib.auth.backends.RemoteUserBackend',
        ...
    )


Hit it with the correct headers and you'll be authenticated immediately:

::

    $ curl -XGET 'http://localhost:8000/' \
        -H 'X-Device-User-Agent: user-agent' \
        -H 'X-Mxit-CONTACT: contact' \
        -H 'X-Mxit-USERID-R: userid-r' \
        -H 'X-Mxit-NICK: nick' \
        -H 'X-Mxit-LOCATION: za,south africa,,,ct,cape town,,,,' \
        -H 'X-Mxit-PROFILE: en,za,01-01-2013,,,' \
        -H 'X-Mxit-USER-INPUT: &lt;b&gt;foo&lt;/b&gt;' \

    {
      "username": "userid-r",
      "mxit": {
        "MXIT_NICK": "nick",
        "MXIT_PROFILE": {
          "gender": "",
          "date_of_birth": "01-01-2013",
          "tariff_plan": "",
          "country_code": "za",
          "language_code": "en"
        },
        "DEVICE_USER_AGENT": "user-agent",
        "MXIT_CONTACT": "contact",
        "MXIT_LOCATION": {
          "city": "cape town",
          "cell_id": "",
          "network_operator_id": "",
          "subdivision_code": "",
          "client_features_bitset": "",
          "country_code": "za",
          "subdivision_name": "",
          "country_name": "south africa",
          "city_code": "ct"
        },
        "MXIT_USER_INPUT": "<b>foo</b>",
        "MXIT_USERID_R": "userid-r"
      }
    }
