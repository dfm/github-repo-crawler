#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
import os
import time
import json
import traceback
from crawler.repos import get_random_repos, process_repo

info_fn = "data/_STATS.json"
if os.path.exists(info_fn):
    with open(info_fn, "r") as f:
        info = json.load(f)
else:
    info = {}
    info["ntot"] = 0
    info["nreadme"] = 0
    info["nlicense"] = 0

while True:
    # Get a list of random repos.
    strt = time.time()
    try:
        repos = get_random_repos()
    except Exception as e:
        print("While getting repos, got exception: ")
        traceback.print_exc()
        continue

    # Loop over these repos and process each one.
    r = []
    for repo in repos:
        try:
            r.append(process_repo(repo))
        except Exception as e:
            print("While analyzing a repo {0}, got exception: "
                  .format(repo["full_name"]))
            traceback.print_exc()
            continue

    # Count the number of readmes and licenses.
    r = map(sum, zip(*r))
    info["ntot"] += r[0]
    info["nreadme"] += r[1]
    info["nlicense"] += r[2]

    # Watch the grass grow.
    print(("Analyzed {0} repositories. Found: {1} readmes, {2} licenses. "
           "Took {3} seconds.").format(info["ntot"], info["nreadme"],
                                       info["nlicense"], time.time() - strt))
    with open(info_fn, "w") as f:
        json.dump(info, f)
