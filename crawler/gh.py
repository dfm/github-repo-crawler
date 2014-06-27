#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = ["get_auth", "gh_request"]

import os
import requests

auth_id = None
auth_secret = None
base_url = "https://api.github.com"


def get_auth():
    global auth_id, auth_secret
    if auth_id is None:
        auth_id = os.environ["GH_CRAWLER_ID"]
    if auth_secret is None:
        auth_secret = os.environ["GH_CRAWLER_SECRET"]
    return {"client_id": auth_id, "client_secret": auth_secret}


def gh_request(endpoint, method="GET", **kwargs):
    kwargs = dict(get_auth(), **kwargs)
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "dfm/github-repo-crawler",
    }
    r = getattr(requests, method.lower())(base_url + endpoint,
                                          params=kwargs,
                                          headers=headers)

    if r.status_code != requests.codes.ok:
        r.raise_for_status()

    return r
