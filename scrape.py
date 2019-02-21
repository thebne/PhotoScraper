import sys
import sqlite3
import hashlib
import requests


DATABASE_PATH = "hashes.sqlite3"
MAX_REPEATS_BEFORE_STOP = 100

def main(url):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute(""" CREATE TABLE IF NOT EXISTS hashes (
                  md5 TEXT PRIMARY KEY,
                  image BLOB
                  ); """)

    conn.commit()

    repeats = 0
    while repeats < MAX_REPEATS_BEFORE_STOP:
        img = requests.get(url, stream=True)
        binary = img.raw.read()
        md5 = hashlib.md5(binary).hexdigest()

        # check if image is in DB
        c.execute("SELECT COUNT(*) AS count FROM hashes WHERE md5=?", (md5,))
        res = c.fetchone()
        if res[0] > 0:
            repeats += 1
            print("Image repeated, skipping (", repeats, ")")
            continue
        repeats = 0

        c.execute("INSERT INTO hashes (md5, image) VALUES (?, ?)",
                  (md5, binary))
        conn.commit()
        print("Fetched image")


if __name__ == '__main__':
    main(sys.argv[1])