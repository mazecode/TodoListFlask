# Flask-blog

This is a tutorial for building a Flask blog application. If you get into trouble (like I did) try the mailing list or google it. For all the problems that I had, I have noted below the fixes I used.

I built this app with the Flask micro-framework to be used as part of a series of applications that I will be 
performing benchmarking tests on.
See my Ruby on Rails version of this application here: https://github.com/archerydwd/ror_blog
The Chicago Boss version is here: https://github.com/archerydwd/cb_blog

I am going to be performing tests on this app using some load testing tools such as Gatling & Tsung. The guide for running the tests can be found here: https://github.com/archerydwd/gatling-tests

Once I have tested this application and the other verisons of it, I will publish the results, which can then be used as a benchmark for others when choosing a framework.

You can build this app using a framework of your choosing and then follow the testing mechanisms that I have described here: https://github.com/archerydwd/gatling-tests
Then compare your results against my benchmarks to get an indication of performance levels for your chosen framework.

=
###Install Python

At time of writing this the Python version was: 3.4.3 and the Flask version was: 0.10.1
Also note that sqlite comes as part of the python library, so we don't need to install sqlite seperatly.

**On OSX** 

Follow the link: https://www.python.org/ftp/python/3.4.3/python-3.4.3-macosx10.6.pkg
Open this and follow the instructions.

**On Linux**

```
wget http://www.python.org/ftp/python/3.4.3/Python-3.4.3.tgz
tar -xzf Python-3.4.3.tgz  
cd Python-3.4.3

./configure  
make  
sudo make install
```

=
###Install pip on linux

We will use pip to install flask.

```
sudo apt-get install python-pip
```

=
###Install Flask

```
sudo pip install Flask
```

=
###Building the blog app

>touch __init__.py

>vim __init__.py

```
import sqlite3
from flask import Flask, render_template, url_for, request, redirect, flash

app = Flask(__name__)

SQL = """
create table if not exists articles (
  	article_id INTEGER PRIMARY KEY AUTOINCREMENT,
	  article_title varchar(24),
		article_text varchar(200)
		)
"""

COMMENT = """
create table if not exists comments (
	comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
	art_id INTEGER,
	commenter varchar(50),
	body varchar(250),
	FOREIGN KEY(art_id) REFERENCES articles(article_id)
	)
"""

def setupdb():
	with sqlite3.connect('blogdata.db', check_same_thread=False) as connection:
		cursor = connection.cursor()
		cursor.execute(SQL)
		cursor.execute(COMMENT)

setupdb()

@app.route('/', methods=['GET', 'POST'])
def display_articles():
	with sqlite3.connect('blogdata.db', check_same_thread=False) as connection:
		cursor = connection.cursor()
		SELECT = """SELECT * from articles"""
		articles_data = cursor.execute(SELECT)
	return(render_template("index.html", the_title="Flask Blog", articles=articles_data, delete_link=url_for("delete_article"), update_link=url_for("update_article"), show_link=url_for("show_article"), create_link=url_for("create_article")))

@app.route('/articles/create', methods=['GET', 'POST'])
def create_article():
	return(render_template("create.html", the_title="Flask Blog - create", index_link=url_for("display_articles"), save_article_link=url_for("save_article")))
					
@app.route('/savearticle', methods=['POST'])
def save_article():
	all_ok = True
	if len(request.form['article_title']) < 5:
		all_ok = False
		flash("Sorry the article title must be 5 or more characters. Try again")
	if len(request.form['article_title']) == 0:
		all_ok = False
		flash("Sorry the article title cannot be empty. Try again")
	if len(request.form['article_text']) == 0:
		all_ok = False
		flash("Sorry the article text cannot be empty. Try again")
	if all_ok:
		with sqlite3.connect('blogdata.db', check_same_thread=False) as connection:
			cursor = connection.cursor()
			INSERT = """
			INSERT INTO articles (article_title, article_text) 
			VALUES (?, ?)
			"""
			cursor.execute(INSERT, (request.form['article_title'], request.form['article_text']))
		return(redirect(url_for("display_articles")))
	else:
		return(redirect(url_for("create_article")))

@app.route('/articles/show', methods=['POST'])
def show_article():
	with sqlite3.connect('blogdata.db', check_same_thread=False) as connection:
		cursor = connection.cursor()
		SHOW = """SELECT * FROM articles WHERE article_id == (?)"""
		SHOWCOMMENTS = """SELECT * FROM comments WHERE art_id == (?)"""
		article_data = list(cursor.execute(SHOW, (request.form['article_id'],)))
		articles_comments = list(cursor.execute(SHOWCOMMENTS, (request.form['article_id'],)))
	return(render_template("show.html", the_title="Flask Blog - show", article=article_data, comments=articles_comments, index_link=url_for("display_articles"), delete_link=url_for("delete_article"), update_link=url_for("update_article"), delete_comment_link=url_for("delete_comment"), create_comment_link=url_for("create_comment")))

@app.route('/articles/delete', methods=['POST'])
def delete_article():
	with sqlite3.connect('blogdata.db', check_same_thread=False) as connection:
		cursor = connection.cursor()
		DELETE = """DELETE FROM articles WHERE article_id == (?)"""
		DELETECOMMENTS = """DELETE FROM comments WHERE art_id == (?)"""
		cursor.execute(DELETE, (request.form['article_id'],))
		cursor.execute(DELETECOMMENTS, (request.form['article_id'],))
	return(redirect(url_for("display_articles")))

@app.route('/articles/update', methods=['GET', 'POST'])
def update_article():
	with sqlite3.connect('blogdata.db', check_same_thread=False) as connection:
		cursor = connection.cursor()
		ARTICLE = """SELECT * FROM articles WHERE article_id == (?)"""
		article_data = cursor.execute(ARTICLE, (request.form['article_id'],))
	return(render_template("update.html", the_title="Flask Blog - update", article=article_data, index_link=url_for("display_articles"), changes_link=url_for("save_changes")))

@app.route('/articles/update_save', methods=['POST'])
def save_changes():
	with sqlite3.connect('blogdata.db', check_same_thread=False) as connection:
		cursor = connection.cursor()
		UPDATE = """UPDATE articles SET article_title = ?, article_text = ? WHERE article_id == ?"""
		cursor.execute(UPDATE, (request.form['article_title'], request.form['article_text'], request.form['article_id']))
	return(redirect(url_for("display_articles")))

@app.route('/comments/create', methods=['POST'])
def create_comment():
	all_ok = True
	if len(request.form['commenter']) == 0:
		all_ok = False
		flash("Sorry your name cannot be empty. Try again")
	if len(request.form['body']) == 0:
		all_ok = False
		flash("Sorry your comment cannot be empty. Try again")
	if all_ok: 
		with sqlite3.connect('blogdata.db', check_same_thread=False) as connection:
			cursor = connection.cursor()
			INSERT = """
				INSERT INTO comments (art_id, commenter, body) 
				VALUES (?, ?, ?)
				"""
			cursor.execute(INSERT, (request.form['article_id'], request.form['commenter'], request.form['body']))
			ARTICLE = """SELECT * FROM articles WHERE article_id == (?)"""
			SELECT = """SELECT * from comments WHERE art_id == (?)"""
			article_data = list(cursor.execute(ARTICLE, (request.form['article_id'],)))
			comments_data = list(cursor.execute(SELECT, (request.form['article_id'],)))
		return(render_template("show.html", the_title="Flask Blog - show", article=article_data, comments=comments_data, index_link=url_for("display_articles"), delete_link=url_for("delete_article"), update_link=url_for("update_article"),  delete_comment_link=url_for("delete_comment"), create_comment_link=url_for("create_comment")))
	else:
		return(redirect(url_for("show.html")))

@app.route('/comments/delete', methods=['POST'])
def delete_comment():
	with sqlite3.connect('blogdata.db', check_same_thread=False) as connection:
		cursor = connection.cursor()
		DELETE = """DELETE FROM comments WHERE comment_id == (?)"""	
		ARTICLE = """SELECT * FROM articles WHERE article_id == (?)"""
		SELECT = """SELECT * from comments WHERE art_id == (?)"""
		cursor.execute(DELETE, (request.form['comment_id'],))
		article_data = list(cursor.execute(ARTICLE, (request.form['article_id'],)))
		comments_data = list(cursor.execute(SELECT, (request.form['article_id'],)))
	return(render_template("show.html", the_title="Flask Blog - show", article=article_data, comments=comments_data, index_link=url_for("display_articles"), delete_link=url_for("delete_article"), update_link=url_for("update_article"),    delete_comment_link=url_for("delete_comment"), create_comment_link=url_for("create_comment")))

app.config['SECRET_KEY'] = 'thisismysecretkeywhichyouwillneverguesshahahahahahahahaha'
if __name__ == "__main__":
	app.run(debug=True)
```

In the above we are first importing all the required libraries. We are then setting up the database tables. Then we get into the flask app and set up routes and methods for the CRUD actions. At the bottom we then set up a secret key and use if __name__ == "__main__" to tell if the app is being run locally or if it's on a platform that runs it automatically. If run locally we need to do app.run inside the if statement.

=
###Templates

We now need to provide templates for our blog app to work. Flask uses Jinja2 templating, so we are going to build a hierarchical template structure. Starting with making a base html page:

>mkdir templates

**base.html**

>touch templates/base.html

>vim templates/base.html

```
<html>
	<head>
		<title>{{ the_title }}</title>
	</head>
	<body>
		{% block the_body %}
		
		{% endblock %}
	</body>
</html>
```

Very simple. You can think of the parts inside the double brackets as variables that we pass in from the __init__.py file. Think of the {% parts as for control flow statements, such as if statements and replacement of sections. 

**create.html**

>touch templates/create.html

>vim templates/create.html

```
{% extends "base.html" %}

{% block the_body %}
	<h1>New article</h1>
	
	{% with messages = get_flashed_messages() %}
		{% if messages %}
			<ul>
				{% for message in messages %}
					<li>{{ message }}
				{% endfor %}
			</ul>
		{% endif %}
	{% endwith %}
	
	<form action="{{ save_article_link }}" method="POST">
		<p>
			Title:<br>
			<input type="text" name="article_title">
		</p>
		<p>
			Text:<br>
			<textarea name="article_text"></textarea>
		</p>
		<p>
			<input type="submit" value="Create Article">
		</p>
	</form>
	<form action="{{ index_link }}" method="POST">
		<button type="submit">Back</button>
	</form>
{% endblock %}
```

**index.html**

>touch templates/index.html

>vim templates/index.html

```
{% extends "base.html" %}

{% block the_body %}
	<h1>Listing articles</h1>
	<a href="{{ create_link }}">New article</a>
	<table>
		<tr>
			<th>Title</th>
			<th>Text</th>
			<th colspan="3"></th>
			{% for id, art_title, art_text in articles %}
				<tr>
					<td>{{ art_title }}</td>
					<td>{{ art_text }}</td>
					<td><form action="{{ show_link }}" method="POST"><input type="hidden" name="article_id" value="{{ id }}"><input type="submit" value="Show"></form></td>
					<td><form action="{{ update_link }}" method="POST"><input type="hidden" name="article_id" value="{{ id }}"><input type="submit" value="Edit"></form></td>
					<td><form action="{{ delete_link }}" method="POST"><input type="hidden" name="article_id" value="{{ id }}"><input type="submit" value="Destroy"></form></td>
				</tr>
			{% endfor %}
	</table>
{% endblock %}
```

**show.html**

>touch templates/show.html

>vim templates/show.html

```
{% extends "base.html" %}

{% block the_body %}
	{% for id, art_title, art_text in article %}
		<p>
			<strong>Title:</strong>
			{{ art_title }}
		</p>
		<p>
			<strong>Text:</strong>
			{{ art_text }}
		</p>
	{% endfor %}

		<h2>Comments</h2>
			{% for comm_id, art_id, commenter, body in comments %}
					<p>
						<strong>Commenter:</strong>
						{{ commenter }}
					</p>
					<p>
						<strong>Comment:</strong>
						{{ body }}
					</p>
					<form action="{{ delete_comment_link }}" method="POST"><input type="hidden" name="article_id" value="{{ art_id }}"><input type="hidden" name="comment_id" value="{{ comm_id }}"><input type="submit" value="Delete Comment"></form>
			{% endfor %}

	{% for id, art_title, art_text in article %}
		<h2>Add a comment:</h2>
		<form method="post" action="{{ create_comment_link }}">
			<input type="hidden" name="article_id" value="{{ id }}" />
			<p>
				Commenter:<br>
				<input type="text" name="commenter" />
			</p>
			<p>
				Body:<br>
				<textarea name="body"></textarea>
			</p>
			<p>
				<input type="submit" value="Create Comment" />
			</p>
		</form>

		<table>
			<tr>
				<td><form action="{{ index_link }}" method="POST"><button type="submit">Back</button></form></td>
				<td><form action="{{ update_link }}" method="POST"><input type="hidden" name="article_id" value="{{ id }}"><input type="submit" value="Edit"></form></td>
			</tr>
		</table>
	{% endfor %}
{% endblock %}
```

**update.html**

>touch templates/update.html

>vim templates/update.html

```
{% extends "base.html" %}

{% block the_body %}
	{% for id, art_title, art_text in article %}
	<form action="{{ changes_link }}" method="post">
		<p>
			Title:<br>
			<input name="article_title" value="{{ art_title }}"/>
		</p>
		<p>
			Text:<br>
			<textarea name="article_text">{{ art_text }}</textarea>
		</p>
		<p>
			<input type="hidden" name="article_id" value="{{ id }}" />
			<input type="submit" value="Update Article"/>
		</p>
	</form>
	{% endfor %}
	<form action="{{ index_link }}" method="POST"><button type="submit">Back</button></form>
{% endblock %}
```

=
###Getting production ready

remove debug = True from the app.run() line at the end of the __init__.py file.

=
###The End

Thanks for reading.

Darren.
