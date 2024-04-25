from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db_file = 'db/mkdb.db'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+db_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '78qw#t0gp02378wq10f1234y6f0qw7og3w87etr1238op4r7t032'
db = SQLAlchemy(app)
# db.create_all()

from mkdashboard import routes, models
