from __future__ import print_function, division

import re
import glob
import yaml
import sqlite3
import numpy as np
from collections import Counter
from nltk import word_tokenize, sent_tokenize


def process_text(body):
    d = Counter([w for s in map(word_tokenize, sent_tokenize(body))
                 for w in s])
    norm = np.sqrt(float(sum(v*v for v in d.values())))
    d = dict((k, c / norm) for k, c in d.iteritems())
    return d


def cosine_similarity(c1, c2):
    if len(c1) > len(c2):
        c1, c2 = c2, c1
    d2 = 0.0
    for w, c in c1.iteritems():
        d2 += c * c2.get(w, 0.0)
    return d2


# Load the license text.
licenses = []
for fn in glob.iglob("../choosealicense.com/_licenses/*.txt"):
    with open(fn, "r") as f:
        txt = f.read()
        _, head, body = txt.split("---\n")
    meta = yaml.load(head)
    meta["_CONTENTS"] = process_text(body)

    if meta["title"] == "No License":
        continue

    # Parse it to get the common name.
    nm = meta["title"].strip("v.0123456789").strip()
    if nm == "Public Domain (Unlicense)":
        nm = "Public Domain"
    elif nm.startswith("CC"):
        nm = "Creative Commons"
    elif nm.startswith("GNU "):
        nm = nm[4:]
    elif "BSD" in nm:
        nm = "BSD"
    meta["common_name"] = nm

    licenses.append(meta)

# Get the unique list of common names.
license_names = list(set(l["common_name"] for l in licenses))

# Pre-compile the regular expressions.
readme_search = re.compile(r"\blicense\b", re.I | re.S)
license_search = re.compile("|".join(map(r"(\b{0}\b)".format, license_names)),
                            re.I | re.S)

# # Add the extra columns.
# with sqlite3.connect("data.db") as conn:
#     c = conn.cursor()
#     c.execute("alter table github add column license_common")
#     c.execute("alter table github add column license_name")
#     c.execute("alter table github add column readme_license")
#     c.execute("alter table github add column readme_license_name")

with sqlite3.connect("data.db") as conn:
    c = conn.cursor()
    c.execute("""select rowid, license, readme from github
        where license is not NULL or readme is not NULL""")
    rows = c.fetchall()
    total = float(len(rows))
    print("{0:.0f} total repos".format(total))

    for j, (rowid, license, readme) in enumerate(rows):
        if j % 10000 == 0:
            print(j, j / total)
        nm = None
        license_name = None
        readme_license = 0
        readme_license_name = None
        if license is not None:
            v = process_text(license.strip())
            d = [cosine_similarity(v, li["_CONTENTS"]) for li in licenses]
            i = np.argmax(d)
            license_name = "unknown" if d[i] < 0.7 else licenses[i]["title"]
            nm = "unknown" if d[i] < 0.7 else licenses[i]["common_name"]
            c.execute("update github set license_name=? where rowid=?",
                      (license_name, rowid))

        if readme is not None:
            readme_license = len(readme_search.findall(readme))
            if readme_license > 0:
                base_counts = license_search.findall(readme)
                if len(base_counts):
                    counts = np.array(map(lambda x:
                                          map(lambda y: len(y) > 0, x),
                                          base_counts))
                    ind = np.argmax(np.sum(counts, axis=0))
                    readme_license_name = license_names[ind]
                c.execute("""update github set
                    readme_license=?, readme_license_name=?
                    where rowid=?""", (readme_license, readme_license_name,
                                       rowid))
        if readme_license_name is None:
            c.execute("""update github set
                readme_license=?, readme_license_name=?
                where rowid=?""", (0, None, rowid))

        if nm is None:
            nm = readme_license_name
        if nm is not None:
            c.execute("update github set license_common=? where rowid=?",
                      (nm, rowid))
