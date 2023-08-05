py-lkd.to
=========

py-lkd.to is a minimal Python wrapper for [lkd.to API](http://lkd.to/api).

Dependencies
------------

requests

    pip install requests
    
Usage
------

    from lkd import lkd

    karan = lkd('karan')
    print karan.about()['realname']
