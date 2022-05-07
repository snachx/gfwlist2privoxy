#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import logging
import pkgutil
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from argparse import ArgumentParser

__all__ = ["main"]

gfwlist_url = "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        dest="input",
        help="local path or remote url of gfwlist, ignore to use default address",
        metavar="GFWLIST",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="output",
        default="gfwlist.action",
        help="path to the output action file",
        metavar="ACTION",
    )
    parser.add_argument(
        "-p",
        "--proxy",
        dest="proxy",
        required=True,
        help='the proxy in the action file, for example, \
                        "127.0.0.1:1080"',
        metavar="PROXY",
    )
    parser.add_argument(
        "-t",
        "--type",
        dest="type",
        required=True,
        help='the proxy type in the action file, should be one of the followings, \
                        "http socks4 socks4a socks5 socks5t"',
        metavar="TYPE",
    )
    parser.add_argument(
        "--user-rule",
        dest="user_rule",
        help="user rule file, which will be appended to gfwlist",
    )
    parser.add_argument(
        "-w",
        "--white-file",
        dest="output_white",
        default="white.action",
        help="path to the output white list file",
        metavar="ACTION",
    )
    return parser.parse_args()


def decode_gfwlist(content):
    # decode base64 if have to
    try:
        if "." in content:
            raise Exception()
        return base64.b64decode(content).decode('utf-8')
    except Exception as e:
        print(e)
        return content


def get_hostname(something):
    try:
        # quite enough for GFW
        if not something.startswith("http:"):
            something = "http://" + something
        r = urllib.parse.urlparse(something)
        return r.hostname
    except Exception as e:
        logging.error(e)
        return None


def add_domain_to_set(s, something):
    hostname = get_hostname(something)
    if hostname is not None:
        if hostname.startswith("."):
            hostname = hostname.lstrip(".")
        if hostname.endswith("/"):
            hostname = hostname.rstrip("/")
        if hostname:
            s.add(hostname)


def parse_gfwlist(content, user_rule=None):
    builtin_rules = pkgutil.get_data(
        "gfwlist2privoxy.resources", "builtin.txt"
    ).decode("utf-8").splitlines(False)
    gfwlist = content.splitlines(False)
    domains = set(builtin_rules)
    domains_white = set()
    if user_rule:
        usrlist = user_rule.splitlines(False)
        gfwlist.extend(usrlist)
        for line in usrlist:
            if line.startswith("@@"):
                add_domain_to_set(domains_white, line.lstrip("@@"))
    for line in gfwlist:
        line = line
        if line.find(".*") >= 0:
            continue
        elif line.find("*") >= 0:
            line = line.replace("*", "/")
        if line.startswith("!"):
            continue
        elif line.startswith("["):
            continue
        elif line.startswith("@"):
            # ignore white list
            continue
        elif line.startswith("||"):
            add_domain_to_set(domains, line.lstrip("||"))
        elif line.startswith("|"):
            add_domain_to_set(domains, line.lstrip("|"))
        elif line.startswith("."):
            add_domain_to_set(domains, line.lstrip("."))
        else:
            add_domain_to_set(domains, line)
    return domains, domains_white


def reduce_domains(domains, domains_white):
    # reduce 'www.google.com' to 'google.com'
    # remove invalid domains
    tld_content = pkgutil.get_data("gfwlist2privoxy.resources", "tld.txt").decode("utf-8")
    tlds = set(tld_content.splitlines(False))
    new_domains = set()
    new_domains_white = set()
    for domain in domains:
        domain_parts = domain.split(".")
        last_root_domain = None
        for i in range(0, len(domain_parts)):
            root_domain = ".".join(domain_parts[len(domain_parts) - i - 1 :])
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

    if domains_white:
        for domain in domains_white:
            domain_parts = domain.split(".")
            last_root_domain = None
            for i in range(0, len(domain_parts)):
                root_domain = ".".join(domain_parts[len(domain_parts) - i - 1 :])
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
                new_domains_white.add(domain)
    return new_domains, new_domains_white


def generate_action(domains, domains_white, proxy, proxy_type):
    # render the action file
    proxy_content = pkgutil.get_data("gfwlist2privoxy.resources", "gfwlist.action").decode("utf-8")
    if proxy_type == "http":
        forward_string = "forward " + proxy
    else:
        forward_type = "forward" + "-" + proxy_type
        forward_string = forward_type + " " + proxy + " ."
    proxy_content = proxy_content.replace("__FORWARDER__", forward_string)
    domains_string = ""
    for domain in domains:
        domains_string += "." + domain + "\n"
    proxy_content = proxy_content.replace("__DOMAINS__", domains_string)
    gen_time = time.localtime()
    format_time = time.strftime("%Y-%m-%d %X %z", gen_time)
    proxy_content = proxy_content.replace("__TIME__", format_time)

    if domains_white:
        white_content = pkgutil.get_data("gfwlist2privoxy.resources", "white.action").decode("utf-8")
        domains_white_string = ""
        for domain in domains_white:
            domains_white_string += "." + domain + "\n"
        white_content = white_content.replace("__DOMAINS__", domains_white_string)
        white_content = white_content.replace("__TIME__", format_time)
    else:
        white_content = None
    return proxy_content, white_content


def is_url(input):
    # URL validator copied from django
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # ...or ipv4
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"  # ...or ipv6
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return regex.match(input)


def main():
    args = parse_args()
    user_rule = None
    if args.input:
        if is_url(args.input):
            print("Downloading gfwlist from %s" % args.input)
            content = urllib.request.urlopen(args.input, timeout=10).read().decode('utf-8')
        else:
            with open(args.input, "r") as f:
                content = f.read()
    else:
        print("Downloading gfwlist from %s" % gfwlist_url)
        content = urllib.request.urlopen(gfwlist_url, timeout=10).read().decode('utf-8')
    if args.user_rule:
        with open(args.user_rule, "r") as f:
            user_rule = f.read()
    print("Start decode gfwlist")
    content = decode_gfwlist(content)
    print("Start parse gwflist")
    domains, domains_white = parse_gfwlist(content, user_rule)
    print("Size of domains:", len(domains))
    print("Reduce domains")
    domains, domains_white = reduce_domains(domains, domains_white)
    print("Regenerate action file")
    pac_content, white_content = generate_action(
        domains, domains_white, args.proxy, args.type
    )
    with open(args.output, "w") as f:
        f.write(pac_content)
    if white_content:
        with open(args.output_white, "w") as f:
            f.write(white_content)


if __name__ == "__main__":
    main()
