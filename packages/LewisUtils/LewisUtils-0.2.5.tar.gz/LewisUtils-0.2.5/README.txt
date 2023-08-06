===========
Lewis Utils Modules
===========

The package provides some modules as shortcuts to do many works for python programmers.

often looks like this::

    #!/usr/bin/env python

    from lewisou.utils import xxxxx


Http Client
=========

    from lewisou.utils.httpclient import utils
    utils.setup (Host='www.google.com')
    utils.r_url('www.google.com')


Mongodb Client
=========
    from lewisou.utils.mongodb import client
    client.setup (db_name='foo')
    db = client.db.get_db()

