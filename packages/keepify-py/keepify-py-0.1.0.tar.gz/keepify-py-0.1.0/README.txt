===============
keepify-py
===============

This is the official Keepify Python library. This library allows for server-side intergration of Keepify from your python application.

Installation
============

The library can be installed using pip::
    pip install keepify-py

Usage
===============

    #!/usr/bin/env python
    from keepify import Keepify

    kp = Keepify(YOUR_TOKEN)

    # tracks an event with certain properties
    kp.track("user@email.com",'item purchase', {'item_id' : '113', 'size': 'large'})