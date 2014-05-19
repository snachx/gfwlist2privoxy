GFWList2Privoxy
===========

|Build Status|

Generate action file for privoxy from gfwlist, inspired by clowwindy's gfwlist_ and modified from it.

::

    pip install gfwlist2privoxy

    usage: main.py [-h] [-i GFWLIST] -f ACTION -p PROXY -t PROXY_TYPE [--user-rule USER_RULE]

    detail arguments:
      -h, --help                    show this help message and exit

      -i GFWLIST, --input GFWLIST   path to the gfwlist, ignore to download from Internet

      -f ACTION, --file ACTION      path to the output action file

      -p PROXY, --proxy PROXY       the proxy in the action file, for example, "127.0.0.1:1080"

      -t TYPE, --type TYPE          the proxy type in the action file, should be one of the followings,
                                    "http socks4 socks4a socks5 socks5t"

      --user-rule USER_RULE         user rule file, which will be appended to gfwlist

    Please set https proxy in your system if you ignore the argument GFWLIST.

.. |Build Status| image:: https://travis-ci.org/snachx/gfwlist2privoxy.png?branch=master
   :target: https://travis-ci.org/snachx/gfwlist2privoxy
.. _gfwlist: https://github.com/clowwindy/gfwlist2pac
