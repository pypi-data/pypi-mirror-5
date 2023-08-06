Attendly python library
=======================

Python interface to the Attendly API

**Note: This is a very early alpha release of the api.. things may change**

Basic usage
````````````

.. code:: python

    import attendly

    # Login (normally you would just store the apikey and only login once)
    user = attendly.User.login('bobby7','password')

    attendly.apikey(user['apikey'])

    # Get a list of events
    events = attendly.Event.list()
    for e in events:
        print e['event']['name']

    # Get an event
    event = attendly.Event.get(events[0]['event']['id'])
    print event['url']

Install via pip
`````````````````

.. code:: bash

    $ pip install Attendly


Links
`````

* `website <http://attendly.com/>`_
* `documentation <http://attendly.me/apidocs/>`_
* `source <https://github.com/Attendly/attendly-python>`_