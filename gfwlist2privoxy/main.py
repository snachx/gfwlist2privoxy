#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pkgutil
import urllib.parse
import logging
import urllib.request, urllib.error, urllib.parse
import time
import re
from argparse import ArgumentParser
import base64

__all__ = ['main']


gfwlist_url = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
                        help='local path or remote url of gfwlist, ignore to use default address', metavar='GFWLIST')
    parser.add_argument('-f', '--file', dest='output', required=True,
                        help='path to the output action file', metavar='ACTION')
    parser.add_argument('-p', '--proxy', dest='proxy', required=True,
                        help='the proxy in the action file, for example, \
                        "127.0.0.1:1080"', metavar='PROXY')
    parser.add_argument('-t', '--type', dest='type', required=True,
                        help='the proxy type in the action file, should be one of the followings, \
                        "http socks4 socks4a socks5 socks5t"', metavar='TYPE')
    parser.add_argument('--user-rule', dest='user_rule',
                        help='user rule file, which will be appended to gfwlist')
    return parser.parse_args()


def decode_gfwlist(content):
    # decode base64 if have to
    try:
        if b'.' in content:
            raise Exception()
        return base64.b64decode(content)
    except Exception as e:
        print(e)
        return content


def get_hostname(something):
    try:
        # quite enough for GFW
        if not something.startswith(b'http:'):
            something = b'http://' + something
        r = urllib.parse.urlparse(something)
        return r.hostname
    except Exception as e:
        logging.error(e)
        return None


def add_domain_to_set(s, something):
    hostname = get_hostname(something)
    if hostname is not None:
        if hostname.startswith(b'.'):
            hostname = hostname.lstrip(b'.')
        if hostname.endswith(b'/'):
            hostname = hostname.rstrip(b'/')
        if hostname:
            s.add(hostname)


def parse_gfwlist(content, user_rule=None):
    builtin_rules = pkgutil.get_data('resources', 'builtin.txt').splitlines(False)
    gfwlist = content.splitlines(False)
    if user_rule:
        gfwlist.extend(user_rule.splitlines(False))
    domains = set(builtin_rules)
    for line in gfwlist:
        line = line
        if line.find(b'.*') >= 0:
            continue
        elif line.find(b'*') >= 0:
            line = line.replace(b'*', b'/')
        if line.startswith(b'!'):
            continue
        elif line.startswith(b'['):
            continue
        elif line.startswith(b'@'):
            # ignore white list
            continue
        elif line.startswith(b'||'):
            add_domain_to_set(domains, line.lstrip(b'||'))
        elif line.startswith(b'|'):
            add_domain_to_set(domains, line.lstrip(b'|'))
        elif line.startswith(b'.'):
            add_domain_to_set(domains, line.lstrip(b'.'))
        else:
            add_domain_to_set(domains, line)
    return domains


def reduce_domains(domains):
    # reduce 'www.google.com' to 'google.com'
    # remove invalid domains
    tld_content = pkgutil.get_data('resources', 'tld.txt')
    tlds = set(tld_content.splitlines(False))
    new_domains = set()
    for domain in domains:
        domain_parts = domain.split(b'.')
        last_root_domain = None
        for i in range(0, len(domain_parts)):
            root_domain = b'.'.join(domain_parts[len(domain_parts) - i - 1:])
            if i == 0:
                if not tlds.__contains__(root_domain):
                    # root_domain is not a valid tld
                    break
            last_root_domain = root_domain
            if tlds.__contains__(root_domain):
                continue
            else:
                break
        if last_root_domain:
            new_domains.add(last_root_domain)
    return new_domains


def generate_action(domains, proxy, proxy_type):
    # render the action file
    proxy_content = pkgutil.get_data('resources', 'gfwlist.action')
    if proxy_type == b'http':
        forward_string = b'forward ' + proxy
    else:
        forward_type = b'forward' + b'-' + proxy_type
        forward_string = forward_type + b' ' + proxy + b' .'
    proxy_content = proxy_content.replace(b'__FORWARDER__', forward_string)
    domains_string = b''
    for domain in domains:
        domains_string += b'.' + domain + b'\n'
    proxy_content = proxy_content.replace(b'__DOMAINS__', domains_string)
    gen_time = time.localtime()
    format_time = time.strftime("%Y-%m-%d %X %z", gen_time).encode('utf-8')
    proxy_content = proxy_content.replace(b'__TIME__', format_time)
    return proxy_content

def is_url(input):
    # URL validator copied from django
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$'.encode('utf-8'), re.IGNORECASE)
    return regex.match(input)

def main():
    args = parse_args()
    user_rule = None
    if args.input:
        if is_url(args.input):
            print('Downloading gfwlist from %s' % args.input)
            content = urllib.request.urlopen(args.input, timeout=10).read()
        else:
            with open(args.input, 'r') as f:
                content = f.read()
    else:
        print('Downloading gfwlist from %s' % gfwlist_url)
        content = urllib.request.urlopen(gfwlist_url, timeout=10).read()
    if args.user_rule:
        with open(args.user_rule, 'r') as f:
            user_rule = f.read()
    print('Start decode gfwlist')
    content = decode_gfwlist(content)
    print('Start parse gwflist')
    domains = parse_gfwlist(content, user_rule)
    print('Size of domains:', len(domains))
    print('Reduct domains')
    domains = reduce_domains(domains)
    print('Regenerate action file')
    pac_content = generate_action(sorted(domains), args.proxy.encode('utf-8'), args.type.encode('utf-8'))
    with open(args.output, 'wb') as f:
        f.write(pac_content)


if __name__ == '__main__':
    main()
