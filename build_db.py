import os
import json
import glob
import sqlite3

with sqlite3.connect("data.db") as conn:
    c = conn.cursor()
    c.execute("drop table if exists github")
    c.execute("""
        create table github (
            owner text,
            name text,
            description text,
            language text,
            forks integer,
            watchers integer,
            stars integer,
            issues integer,
            readme text,
            license text
        )
    """)

for i, directory in enumerate(glob.iglob(os.path.join("data", "*", "*"))):
    if i % 100 == 0:
        print(i)

    fn = os.path.join(directory, "info.json")
    if not os.path.exists(fn):
        continue
    with open(fn, "r") as f:
        data = json.load(f)
        args = [data["owner"]["login"]] + [data[k] for k in (
            "name", "description", "language", "forks_count", "watchers",
            "stargazers_count", "open_issues",
        )]

    fn = os.path.join(directory, "README")
    readme = None
    if os.path.exists(fn):
        with open(fn, "r") as f:
            data = f.read()
            try:
                readme = data.decode("utf-8")
            except UnicodeError:
                try:
                    readme = data.decode("ISO-8859-1")
                except:
                    readme = None
            except:
                readme = None

    fn = os.path.join(directory, "LICENSE")
    license = None
    if os.path.exists(fn):
        with open(fn, "r") as f:
            data = f.read()
            try:
                license = data.decode("utf-8")
            except UnicodeError:
                try:
                    license = data.decode("ISO-8859-1")
                except:
                    license = None
            except:
                licence = None

    with sqlite3.connect("data.db") as conn:
        c = conn.cursor()
        c.execute("""
            insert into github (
                owner, name, description, language, forks, watchers, stars,
                issues, readme, license
            ) values (?,?,?,?,?,?,?,?,?,?)
        """, args + [readme, license])
