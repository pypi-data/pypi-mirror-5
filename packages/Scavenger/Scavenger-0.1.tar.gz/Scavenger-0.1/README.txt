=========
Scavenger
=========

Scavenger is a light search engine for use in django projects utilizing 
redis indexing and mongodb datastore. Usage Example::

    #!/usr/bin/env python

    from mongoengine import *
    from <app.models> import <models>

    p = Person(first_name='joe', last_name='smith')
    Scavenger.index(p)

    search_models = ['first_name', 'last_name']
    s = Scavenger(search_models)

    query = 'jared'
    matches = s.search(query)


Notes
-----

* Scavenger.index method calls save() method of mongodb object.

* Scavenger instance hooks to redis on default localhost:6379 using db=0.

* Scavenger.index_root defaults to current app/directory name