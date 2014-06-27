#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
from crawler.repos import get_random_repos, process_repo

ntot = 0
nreadme = 0
nlicense = 0
while True:
    # Get a list of random repos.
    try:
        repos = get_random_repos()
    except Exception as e:
        print("While getting repos, got exception: ")
        print(e)
        continue

    # Loop over these repos and process each one.
    r = []
    for repo in repos:
        try:
            r.append(process_repo(repo))
        except Exception as e:
            print("While analyzing a repo, got exception: ")
            print(e)
            continue

    # Count the number of readmes and licenses.
    r = map(sum, zip(*r))
    nreadme += r[0]
    nlicense += r[1]
    ntot += len(repos)

    # Watch the grass grow.
    print("Analyzed {0} repositories. Found: {1} readmes, {2} licenses"
          .format(ntot, nreadme, nlicense))
