from json import JSONEncoder
from bson.json_util import loads


class Match:
    def __init__(self, p1_name, p2_name, match_date):
        self.p1_name = p1_name
        self.p2_name = p2_name
        self.match_date = match_date


class MatchResult:
    def __init__(self, tournament_name, matches):
        self.tournament_name = tournament_name
        self.matches = matches


class SimpleEncoder(JSONEncoder):
    def default(self, obj):
        return obj.__dict__


def get_match_result_json(match_result):
    return loads(SimpleEncoder().encode(match_result))