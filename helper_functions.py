# (A) LOAD SQLITE MODULE
import sqlite3
DBFILE = "database.db"
from werkzeug.exceptions import abort

# (B) HELPER - RUN SQL QUERY


def query(sql, data):
    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    conn.close()

# (C) HELPER - FETCH ALL


def select(sql, data=[]):
    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    cursor.execute(sql, data)
    results = cursor.fetchall()
    conn.close()
    return results

# (D) GET TAGS FOR CONTENT
# cid : content id


def get(cid):
    res = []
    for row in select("SELECT `tag_name` FROM `tags` WHERE `post_id`=?", [cid]):
        res.append(row[0])
    return res

# (E) DELETE TAGS
# cid : content id


def delete_tags(cid):
    query("DELETE FROM `tags` WHERE `post_id`=?", [cid])
    return True

# (F) SAVE TAGS
# cid : content id
# tags : array of tags


def save(cid, tags):
    # (F1) DELETE OLD TAGS
    delete_tags(cid)

    # (F2) INSERT NEW TAGS
    sql = "INSERT INTO `tags` (`post_id`, `tag_name`) VALUES "
    data = []
    for tag in tags:
        sql = sql + "(?,?),"
        data.extend([cid, tag])
    sql = sql[:-1] + ";"
    query(sql, data)
    return True


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post
