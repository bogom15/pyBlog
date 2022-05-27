from flask import Flask, render_template, request, url_for, flash, redirect
from helper_functions import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    tags = get(post_id)
    return render_template('post.html', post=post, tags=tags)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tags = request.form['tags']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            if tags:
                tags = tags.replace(" ", "")
                tags = tags.split(',')
                post_id = conn.execute(
                    'SELECT * FROM posts WHERE id=(SELECT max(id) FROM posts);').fetchall()[0][0]
                save(post_id, tags)
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)
    tags = get(id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tags = request.form['tags']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            tags = tags.replace(" ", "")
            tags = tags.split(',')
            save(id, tags)
            return redirect(url_for('index'))

    return render_template('edit.html', post=post, tags=tags)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    delete_tags(id)
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


@app.route('/filter', methods=('POST',))
def filter():
    tag = request.form['tag']
    conn = get_db_connection()
    posts = conn.execute(f"""SELECT p.id, p.title, p.content,p.created
                            FROM
                            tags as t
                            JOIN posts p 
                            ON t.post_id=p.id
                            where t.tag_name = "{tag}";""").fetchall()
    conn.close()
    return render_template('filter.html',posts=posts)