#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import pkgutil
from urllib import parse, request
import logging
import time
from argparse import ArgumentParser

__all__ = ['main']


gfwlist_url = 'https://gitlab.com/gfwlist/gfwlist/raw/master/gfwlist.txt'


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
                        help='path to gfwlist, ignore to download from Internet', metavar='GFWLIST')
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
        return base64.b64decode(content)
    except Exception:
        return content


def get_hostname(something):
    try:
        # quite enough for GFW
        if not something.startswith('http:'):
            something = 'http://' + something
        r = parse.urlparse(something)
        return r.hostname
    except Exception as e:
        logging.error(e)
        return None


def add_domain_to_set(s, something):
    hostname = get_hostname(something)
    if hostname is not None:
        if hostname.startswith('.'):
            hostname = hostname.lstrip('.')
        if hostname.endswith('/'):
            hostname = hostname.rstrip('/')
        if hostname:
            s.add(hostname)


def parse_gfwlist(content, user_rule=None):
    builtin_rules = pkgutil.get_data('resources', 'builtin.txt').decode('utf-8').splitlines(False)
    gfwlist = content.splitlines(False)
    if user_rule:
        gfwlist.extend(user_rule.splitlines(False))
    domains = set(builtin_rules)
    for line in gfwlist:
        sline = line.decode('utf-8')
        if sline.find('.*') >= 0:
            continue
        elif sline.find('*') >= 0:
            sline = sline.replace('*', '/')
        if sline.startswith('!'):
            continue
        elif sline.startswith('['):
            continue
        elif sline.startswith('@'):
            # ignore white list
            continue
        elif sline.startswith('||'):
            add_domain_to_set(domains, sline.lstrip('||'))
        elif sline.startswith('|'):
            add_domain_to_set(domains, sline.lstrip('|'))
        elif sline.startswith('.'):
            add_domain_to_set(domains, sline.lstrip('.'))
        else:
            add_domain_to_set(domains, sline)
    return domains


def reduce_domains(domains):
    # reduce 'www.google.com' to 'google.com'
    # remove invalid domains
    tld_content = pkgutil.get_data('resources', 'tld.txt').decode('utf-8')
    tlds = set(tld_content.splitlines(False))
    new_domains = set()
    for domain in domains:
        domain_parts = domain.split('.')
        last_root_domain = None
        for i in range(0, len(domain_parts)):
            root_domain = '.'.join(domain_parts[len(domain_parts) - i - 1:])
            if i == 0:
                if not tlds.__contains__(root_domain):
                    # root_domain is not a valid tld
                    break
            last_root_domain = root_domain
            if tlds.__contains__(root_domain):
                continue
            else:
                break
        if last_root_domain is not None:
            new_domains.add(last_root_domain)
    return new_domains


def generate_action(domains, proxy, proxy_type):
    # render the action file
    proxy_content = pkgutil.get_data('resources', 'gfwlist.action').decode('utf-8')
    if proxy_type == 'http':
        forward_string = 'forward ' + proxy
    else:
        forward_type = 'forward' + '-' + proxy_type
        forward_string = forward_type + ' ' + proxy + ' .'
    proxy_content = proxy_content.replace('__FORWARDER__', forward_string)
    domains_string = ''
    for domain in domains:
        domains_string += '.' + domain + '\n'
    proxy_content = proxy_content.replace('__DOMAINS__', domains_string)
    gen_time = time.localtime()
    format_time = time.strftime("%Y-%m-%d %X %z", gen_time)
    proxy_content = proxy_content.replace('__TIME__', format_time)
    return proxy_content


def main():
    args = parse_args()
    user_rule = None
    if args.input:
        with open(args.input, 'rb') as f:
            content = f.read()
    else:
        print('Downloading gfwlist from %s' % gfwlist_url)
        content = request.urlopen(gfwlist_url, timeout=10).read()
    if args.user_rule:
        with open(args.user_rule, 'rb') as f:
            user_rule = f.read()

    content = decode_gfwlist(content)
    domains = parse_gfwlist(content, user_rule)
    domains = reduce_domains(domains)
    pac_content = generate_action(domains, args.proxy, args.type)
    with open(args.output, 'wt') as f:
        f.write(pac_content)


if __name__ == '__main__':
    main()
