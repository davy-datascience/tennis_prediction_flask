import configparser

from flask import Flask, render_template, redirect, url_for, request
from flask_moment import Moment
from datetime import datetime

from tennis.managers.match_manager import get_match_results

config = configparser.ConfigParser()
config.read("config.ini")

app = Flask(__name__)
app.secret_key = config['flask']['secret_key']
app.debug = True

moment = Moment(app)


@app.route('/')
def index():
    return redirect(url_for('tennis'))


@app.route('/tennis')
def tennis():
    match_results = None

    # Get today date from url
    date_str = request.args.get('date')

    if date_str:
        date_picked = str(date_str).split("-")

        date_of_matches = datetime(int(date_picked[0]), int(date_picked[1]), int(date_picked[2]),
                                   int(date_picked[3]), int(date_picked[4]))

        match_results = get_match_results(date_of_matches)

    return render_template('tennis/home.html', match_results=match_results)


@app.route('/change_date_of_matches', methods=['GET', 'POST'])
def change_date_of_matches():
    data = request.data.decode("utf-8")
    date_picked = data.split("-")

    date_of_matches = datetime(int(date_picked[0]), int(date_picked[1]), int(date_picked[2]),
                               int(date_picked[3]), int(date_picked[4]))

    return render_template('tennis/matches.html', match_results=get_match_results(date_of_matches))
