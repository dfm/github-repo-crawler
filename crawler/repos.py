#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = ["get_random_repos", "process_repo"]

import os
import json
import base64
import random
import logging

from .gh import gh_request

# MAGIC: an estimate of the number of public GitHub repositories.
TOTAL_N_EST = 21300000

BASE_DIR = "./data"
try:
    os.makedirs(BASE_DIR)
except os.error:
    pass


def get_random_repos():
    i = random.randint(0, TOTAL_N_EST)
    r = []
    while not len(r):
        r = gh_request("/repositories", since=i).json()
    return r


def license_filename_score(fn):
    lfn = fn.lower()
    if "license" not in lfn and "copying" not in lfn:
        return 0
    if fn.startswith("LICENSE") or fn.startswith("COPYING"):
        return 3
    if fn.startswith("license") or fn.startswith("copying"):
        return 2
    return 1


def process_repo(repo, clobber=False):
    name = repo["full_name"]

    # Skip if this repo had already been downloaded.
    bp = os.path.join(BASE_DIR, name)
    if not clobber and os.path.exists(bp):
        logging.warn("{0} has already been downloaded. Skipping".format(name))
        return
    elif not clobber:
        os.makedirs(bp)

    # Save the info.
    with open(os.path.join(bp, "info.json"), "w") as f:
        json.dump(repo, f)

    # Get the README.
    r = gh_request("/repos/{0}/readme".format(name)).json()
    content = r.get("content", None)
    if content is not None:
        readme = base64.b64decode(content)
        with open(os.path.join(bp, "README"), "w") as f:
            f.write(readme)
    else:
        logging.warn("No README found for {0}".format(name))

    # List the top-level directory.
    r = gh_request("/repos/{0}/contents/".format(name)).json()

    # Try to find a license.
    files = []
    for f in r:
        # Skip directories.
        if f["type"] != "file":
            continue

        # Score the licenseness of each file based on its filename.
        fn = f["name"]
        score = license_filename_score(fn)
        if score > 0:
            files.append((fn, score))

    # Stop if no license file was found.
    if not len(files):
        logging.warning("No license found for {0}".format(name))
        return

    # Download and save the best license file.
    fn = sorted(files, key=lambda o: o[1], reverse=True)[0][0]
    r = gh_request("/repos/{0}/contents/{1}".format(name, fn)).json()
    content = r.get("content", None)
    if content is not None:
        license = base64.b64decode(content)
        with open(os.path.join(bp, "LICENSE"), "w") as f:
            f.write(license)
    else:
        logging.warn("Couldn't parse the license for {0}".format(name))
