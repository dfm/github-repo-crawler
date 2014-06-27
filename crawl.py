#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
import time
import traceback
from crawler.repos import get_random_repos, process_repo

ntot = 0
nreadme = 0
nlicense = 0
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
            print("While analyzing a repo, got exception: ")
            traceback.print_exc()
            continue

    # Count the number of readmes and licenses.
    r = map(sum, zip(*r))
    nreadme += r[0]
    nlicense += r[1]
    ntot += len(repos)

    # Watch the grass grow.
    print(("Analyzed {0} repositories. Found: {1} readmes, {2} licenses. "
           "Took {0} seconds.").format(ntot, nreadme, nlicense,
                                       time.time() - strt))
