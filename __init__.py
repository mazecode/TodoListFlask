import datetime
import logging
import os

from flask import Flask, render_template, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

# ================================================================================================

SECRET_KEY = os.urandom(32)
SERVER = 'localhost'
PORT = 3306
DATABASE = 'todo_app'
USERNAME = 'root'
PASSWORD = ''
DATABASE_CONNECTION = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}?charset=utf8mb4'

# ================================================================================================
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# ================================================================================================
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "TODO List API Rest"
    }
)

app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

# ================================================================================================

handler = logging.FileHandler("./static/todo.log")  # Create the file logger
app.logger.addHandler(handler)  # Add it to the built-in logger
app.logger.setLevel(logging.DEBUG)  # Set the log level to debug

logging.basicConfig(level=logging.DEBUG)


# ================================================================================================

class Todo(db.Model):
    __tablename__ = "todo"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    description = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, nullable=True)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.created_at = datetime.datetime.now()

    def __repr__(self):
        return '' % self.id


db.create_all()


class TodoSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Todo
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    title = fields.String(required=True)
    description = fields.String(required=True)
    created_at = fields.DateTime(required=False, default=datetime.datetime.now())


# ================================================================================================

@app.route('/', methods=["GET"])
def home():
    return render_template('home.html')


@app.route('/about', methods=["GET"])
def about():
    return render_template('about.html')


@app.route('/api/todo', methods=["GET"])
def index():
    get_products = Todo.query.all()
    product_schema = TodoSchema(many=True)
    products = product_schema.dump(get_products)

    return make_response(jsonify({"todo": products})), 200


@app.route('/api/todo/<int:id_todo>', methods=["GET"])
def show(id_todo: int):
    get_todo = Todo.query.get(id_todo)
    todo_schema = TodoSchema()
    todo = todo_schema.dump(get_todo)

    return make_response(jsonify({"todo": todo}), 200)


@app.route('/api/todo', methods=["POST"])
def create():
    data = request.get_json()
    todo_schema = TodoSchema()
    todo = todo_schema.load(data)
    result = todo_schema.dump(todo.create())

    return make_response(jsonify({"todo": result}), 204)


@app.route('/api/todo/<int:id_todo>', methods=["PUT"])
def update(id_todo: int):
    if request.method == 'PUT':
        data = request.get_json()
        get_todo = Todo.query.get(id_todo)

        if data.get('title'):
            get_todo.title = data['title']

        if data.get('description'):
            get_todo.description = data['description']

        db.session.add(get_todo)
        db.session.commit()

        todo_schema = TodoSchema(only=['id', 'title', 'description'])
        todo = todo_schema.dump(get_todo)

        return make_response(jsonify({"todo": todo})), 204


@app.route('/api/error', methods=["GET"])
def error():
    return jsonify(error="Something happend wrong!"), 500


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=80, debug=True)
    app.run(host="127.0.0.1", debug=True)
