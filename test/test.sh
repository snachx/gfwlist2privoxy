#!/bin/bash

pushd .. && \
PYTHONPATH=. python gfwlist2privoxy/main.py  -i test/gfwlist.txt -f test/gfwlist.action -p 127.0.0.1:1080 -t socks5 --user-rule test/user_rule.txt && \
popd && cat gfwlist.action && [ -n "`grep -e .googleapis.com gfwlist.action`" ]  && [ -n "`grep -e .twitter.com gfwlist.action`" ] && \
[ -n "`grep -e .userdefined.com gfwlist.action`" ] && echo 'Test passed'
