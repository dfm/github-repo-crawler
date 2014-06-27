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
import requests

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
    # Skip forks.
    if repo.get("fork", True):
        return False, False, False

    # Get the repository name.
    name = repo["full_name"]

    # Skip if this repo had already been downloaded.
    bp = os.path.join(BASE_DIR, name)
    if not clobber and os.path.exists(bp):
        logging.info("{0} has already been downloaded. Skipping".format(name))
        return False, False, False

    logging.info("Processing {0}...".format(name))

    # Get the repository info.
    try:
        info = gh_request("/repos/{0}".format(name)).json()
    except requests.exceptions.HTTPError:
        logging.info("Can't get info for {0}".format(name))
        return False, False, False

    # Save the information.
    try:
        os.makedirs(bp)
    except os.error:
        pass
    with open(os.path.join(bp, "info.json"), "w") as f:
        json.dump(info, f)

    # Get the README.
    readme = None
    try:
        r = gh_request("/repos/{0}/readme".format(name)).json()
    except requests.exceptions.HTTPError:
        logging.info("No README found for {0}".format(name))
    else:
        content = r.get("content", None)
        if content is not None:
            readme = base64.b64decode(content)
            with open(os.path.join(bp, "README"), "w") as f:
                f.write(readme)
        else:
            logging.info("No README found for {0}".format(name))

    # List the top-level directory.
    r = gh_request("/repos/{0}/contents/".format(name)).json()

    # Try to find a license.
    files = []
    lic_files = []
    for f in r:
        # Skip directories.
        if f["type"] != "file":
            continue

        # Score the licenseness of each file based on its filename.
        fn = f["name"]
        files.append(fn)
        score = license_filename_score(fn)
        if score > 0:
            lic_files.append((fn, score))

    # Save the directory listing.
    with open(os.path.join(bp, "files"), "w") as f:
        f.write(("\n".join(files)).encode("utf-8"))

    # Stop if no license file was found.
    if not len(lic_files):
        logging.info("No license found for {0}".format(name))
        return True, readme is not None, False

    # Download and save the best license file.
    fn = sorted(lic_files, key=lambda o: o[1], reverse=True)[0][0]
    r = gh_request("/repos/{0}/contents/{1}".format(name, fn)).json()
    content = r.get("content", None)
    if content is not None:
        license = base64.b64decode(content)
        with open(os.path.join(bp, "LICENSE"), "w") as f:
            f.write(license)
        return True, readme is not None, True
    else:
        logging.info("Couldn't parse the license for {0}".format(name))

    return True, readme is not None, False
