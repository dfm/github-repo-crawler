#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = ["get_auth", "gh_request"]

import os
import time
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
    payload = dict(get_auth(), **kwargs)
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "dfm/github-repo-crawler",
    }
    r = getattr(requests, method.lower())(base_url + endpoint,
                                          params=payload,
                                          headers=headers)

    if r.status_code != requests.codes.ok:
        if r.status_code == 403:
            # This probably means that the rate limit was reached.
            # Wait for rate limit to reset and then re-submit the request.
            remain = int(r.headers["X-RateLimit-Remaining"])
            if remain < 1:
                reset = int(r.headers["X-RateLimit-Reset"]) - time.time()
                print("Waiting {0} seconds for rate limit to reset..."
                      .format(reset))
                time.sleep(max(1.0, reset))
                return gh_request(endpoint, method=method, **kwargs)

        r.raise_for_status()

    return r
