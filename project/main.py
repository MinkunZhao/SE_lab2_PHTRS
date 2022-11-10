from flask import Blueprint, render_template
import sqlite3


def get_db_connection():
    conn = sqlite3.connect(".\\project\\pothole.sqlite")
    conn.row_factory = sqlite3.Row
    return conn


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


    