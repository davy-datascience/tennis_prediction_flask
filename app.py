import configparser

from flask import Flask, render_template, redirect, url_for, request
from flask_moment import Moment
from datetime import datetime

from managers.match_manager import get_match_results

config = configparser.ConfigParser()
config.read("config.ini")

app = Flask(__name__)
app.secret_key = config['flask']['secret_key']
app.debug = True

moment = Moment(app)


@app.route('/')
def index():
    # return render_template('tennis/test.html')
    return redirect(url_for('tennis'))


@app.route('/tennis')
def tennis():
    date_of_matches = datetime(2020, 10, 26, 23, 0)

    return render_template('tennis/home.html', match_results=get_match_results(date_of_matches))


@app.route('/change_date_of_matches', methods=['GET', 'POST'])
def change_date_of_matches():
    print("change date of matches on server")

    data = request.data
    print(data)
    date_picked = data.split()

    date_of_matches = datetime(int(date_picked[0]), int(date_picked[1]), int(date_picked[2]),
                               int(date_picked[3]), int(date_picked[4]))

    return render_template('tennis/matches.html', match_results=get_match_results(date_of_matches))
