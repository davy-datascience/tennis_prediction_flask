from json import JSONEncoder
from bson.json_util import loads


class Match:
    def __init__(self, row):
        self.match_id = row["match_id"]
        self.p1_name = row["p1_name"]
        self.p2_name = row["p2_name"]
        self.match_date = row["datetime"]
        self.status = row["status"]

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

        if "p1_ace" in row.index:
            self.p1_ace = row["p1_ace"]
            self.p1_df = row["p1_df"]
            self.p1_svpt = row["p1_svpt"]
            self.p1_1st_in = row["p1_1st_in"]
            self.p1_1st_won = row["p1_1st_won"]
            self.p1_2nd_won = row["p1_2nd_won"]
            self.p1_sv_gms = row["p1_sv_gms"]
            self.p1_bp_saved = row["p1_bp_saved"]
            self.p1_bp_faced = row["p1_bp_faced"]
            self.p1_2nd_pts = row["p1_2nd_pts"]
            self.p1_svpt_won = row["p1_svpt_won"]
            self.p1_1st_serve_ratio = row["p1_1st_serve_ratio"]
            self.p1_svpt_ratio = row["p1_svpt_ratio"]
            self.p1_1st_won_ratio = row["p1_1st_won_ratio"]
            self.p1_2nd_won_ratio = row["p1_2nd_won_ratio"]
            self.p1_sv_gms_won = row["p1_sv_gms_won"]
            self.p1_sv_gms_won_ratio = row["p1_sv_gms_won_ratio"]
            self.p1_bp_saved_ratio = row["p1_bp_saved_ratio"]
            self.p2_ace = row["p2_ace"]
            self.p2_df = row["p2_df"]
            self.p2_svpt = row["p2_svpt"]
            self.p2_1st_in = row["p2_1st_in"]
            self.p2_1st_won = row["p2_1st_won"]
            self.p2_2nd_won = row["p2_2nd_won"]
            self.p2_sv_gms = row["p2_sv_gms"]
            self.p2_bp_saved = row["p2_bp_saved"]
            self.p2_bp_faced = row["p2_bp_faced"]
            self.p2_2nd_pts = row["p2_2nd_pts"]
            self.p2_svpt_won = row["p2_svpt_won"]
            self.p2_1st_serve_ratio = row["p2_1st_serve_ratio"]
            self.p2_svpt_ratio = row["p2_svpt_ratio"]
            self.p2_1st_won_ratio = row["p2_1st_won_ratio"]
            self.p2_2nd_won_ratio = row["p2_2nd_won_ratio"]
            self.p2_sv_gms_won = row["p2_sv_gms_won"]
            self.p2_sv_gms_won_ratio = row["p2_sv_gms_won_ratio"]
            self.p2_bp_saved_ratio = row["p2_bp_saved_ratio"]

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