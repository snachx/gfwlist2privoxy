GFWList2Privoxy
==============================================================

|Build Status|

Usage
--------------------------------------------------------------

Generate action file for privoxy from gfwlist, inspired by clowwindy's gfwlist2pac_ and modified from it.

::

    pip install gfwlist2privoxy

    usage: main.py [-h] [-i GFWLIST] -f ACTION -p PROXY -t TYPE [--user-rule USER_RULE]

    detail arguments:
      -h, --help                    show this help message and exit

      -i GFWLIST, --input GFWLIST   local path or remote url of gfwlist, ignore to use default address

      -f ACTION, --file ACTION      path to the output action file

      -p PROXY, --proxy PROXY       the proxy in the action file, for example, "127.0.0.1:1080"

      -t TYPE, --type TYPE          the proxy type in the action file, should be one of the followings,
                                    "http socks4 socks4a socks5 socks5t"

      --user-rule USER_RULE         user rule file, which will be appended to gfwlist

    Please set https proxy in your system if you ignore the argument GFWLIST.

Example Action File
----------------------------------------------------------
An example of generated action file is here_.

.. |Build Status| image:: https://travis-ci.org/snachx/gfwlist2privoxy.png?branch=master
   :target: https://travis-ci.org/snachx/gfwlist2privoxy
.. _gfwlist2pac: https://github.com/clowwindy/gfwlist2pac
.. _here: https://github.com/snachx/gfwlist2privoxy/blob/master/test/gfwlist.action
