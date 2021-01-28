import pytz

from pytz import timezone
from datetime import datetime

from tennis.classes.MatchResult import Match, MatchResult
from tennis.queries.match_queries import query_matches, query_next_match_date, query_previous_match_date


def get_match_results(date_of_matches):
    matches = query_matches(date_of_matches)

    matches_per_tour = []

    if len(matches.index) != 0:
        tournaments = matches["tournament_name"].drop_duplicates().tolist()

        for tour in tournaments:
            matches_in_tour = matches[matches["tournament_name"] == tour]
            list_of_matches = [(Match(row))
                               for index, row in matches_in_tour.iterrows()]

            match_result = MatchResult(tour, list_of_matches)

            matches_per_tour.append(match_result)

    return matches_per_tour


def get_next_match_date(date_of_matches, local_timezone):
    match_date_utc = query_next_match_date(date_of_matches)
    if match_date_utc:
        match_date_utc = pytz.utc.localize(match_date_utc)
        match_date = match_date_utc.astimezone(timezone(local_timezone))
        return match_date.date()
    else:
        return None


def get_previous_match_date(date_of_matches, local_timezone):
    match_date_utc = query_previous_match_date(date_of_matches)
    if match_date_utc:
        match_date_utc = pytz.utc.localize(match_date_utc)
        match_date = match_date_utc.astimezone(timezone(local_timezone))
        return match_date.date()
    else:
        return None
