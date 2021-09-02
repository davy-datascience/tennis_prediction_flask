import configparser

from flask import Flask, render_template, redirect, url_for, request, session
from flask_moment import Moment
from datetime import datetime

from pytz import timezone

from tennis.managers.match_manager import get_match_results, get_next_match_date, get_previous_match_date, get_match

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
    next_match_date = None
    previous_match_date = None
    local_timezone = None

    if session.get("timezone") is None:
        local_timezone = request.args.get('timezone')
        session["timezone"] = local_timezone
    else:
        local_timezone = session["timezone"]

    # Get today date from url
    custom_date = request.args.get('date')

    date_of_matches = None

    if local_timezone:
        datetime_of_matches = None
        if custom_date:
            datetime_of_matches = datetime.strptime(custom_date, '%Y-%m-%d')
        else:
            datetime_of_matches = datetime.now(tz=timezone(local_timezone))
            datetime_of_matches = datetime(datetime_of_matches.year, datetime_of_matches.month, datetime_of_matches.day, 0, 0)
        datetime_of_matches = datetime_of_matches.astimezone(timezone(local_timezone))
        date_of_matches = datetime_of_matches.date()

        match_results = get_match_results(datetime_of_matches)

        if len(match_results) == 0:
            next_match_date = get_next_match_date(datetime_of_matches, local_timezone)
            previous_match_date = get_previous_match_date(datetime_of_matches, local_timezone)

    return render_template('tennis/home.html', match_results=match_results, next_date=next_match_date,
                           prev_date=previous_match_date, date_of_matches=date_of_matches)


@app.route('/change_date_of_matches', methods=['GET', 'POST'])
def change_date_of_matches():
    data = request.data.decode("utf-8")
    date_picked = data.split("-")

    date_of_matches = datetime(int(date_picked[0]), int(date_picked[1]), int(date_picked[2]),
                               int(date_picked[3]), int(date_picked[4]))

    next_match_date = None
    previous_match_date = None

    match_results = get_match_results(date_of_matches)

    if len(match_results) == 0:
        next_match_date = get_next_match_date(date_of_matches, session["timezone"])
        previous_match_date = get_previous_match_date(date_of_matches, session["timezone"])

    return render_template('tennis/matches.html', match_results=match_results, next_date=next_match_date,
                           prev_date=previous_match_date)


@app.route('/tennis/match/<match_id>/')
def match_detail(match_id):
    match = get_match(match_id)
    return render_template('tennis/match_detail.html', match=match)