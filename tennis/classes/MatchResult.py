from json import JSONEncoder
from bson.json_util import loads


class Match:
    def __init__(self, row):
        self.p1_name = row["p1_name"]
        self.p2_name = row["p2_name"]
        self.match_date = row["datetime"]

        #
        if "p1_s1_gms" in row.index:
            self.p1_s1_gms = row["p1_s1_gms"]
            self.p1_s2_gms = row["p1_s2_gms"]
            self.p1_s3_gms = row["p1_s3_gms"]
            self.p1_s4_gms = row["p1_s4_gms"]
            self.p1_s5_gms = row["p1_s5_gms"]
            self.p2_s1_gms = row["p2_s1_gms"]
            self.p2_s2_gms = row["p2_s2_gms"]
            self.p2_s3_gms = row["p2_s3_gms"]
            self.p2_s4_gms = row["p2_s4_gms"]
            self.p2_s5_gms = row["p2_s5_gms"]

        if "p1_wins" in row.index:
            self.p1_wins = row["p1_wins"]

        if "p1_proba" in row.index:
            self.p1_proba = row["p1_proba"]
            self.p2_proba = row["p2_proba"]




class MatchResult:
    def __init__(self, tournament_name, matches):
        self.tournament_name = tournament_name
        self.matches = matches


class SimpleEncoder(JSONEncoder):
    def default(self, obj):
        return obj.__dict__


def get_match_result_json(match_result):
    return loads(SimpleEncoder().encode(match_result))