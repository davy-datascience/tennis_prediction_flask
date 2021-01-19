import configparser

from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime

from queries.match_queries import get_matches

config = configparser.ConfigParser()
config.read("config.ini")

app = Flask(__name__)
app.secret_key = config['flask']['secret_key']
app.debug = True


@app.route('/')
def index():
    # return render_template('tennis/test.html')
    return redirect(url_for('tennis'))


@app.route('/tennis')
def tennis():
    return render_template('tennis/home.html', my_date="BLIBLIBLI")


@app.route('/change_date_of_matches', methods=['GET', 'POST'])
def change_date_of_matches():
    print("change date of matches on server")

    data = request.data
    print(data)
    date_picked = data.split()

    # TODO check datetime with timezone on browser
    date_of_matches = datetime(int(date_picked[0]), int(date_picked[1]), int(date_picked[2]))

    matches = get_matches(date_of_matches)

    return matches.to_html(classes='data')
