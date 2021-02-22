import configparser
import pandas as pd
import numpy as np

from datetime import timedelta
from pymongo import MongoClient


def get_match_dtypes(matches):
    all_dtypes = {
        "p1_s1_gms": "Int16", "p1_s2_gms": "Int16", "p1_s3_gms": "Int16", "p1_s4_gms": "Int16", "p1_s5_gms": "Int16",
        "p2_s1_gms": "Int16", "p2_s2_gms": "Int16", "p2_s3_gms": "Int16", "p2_s4_gms": "Int16", "p2_s5_gms": "Int16"
    }

    dtypes = {}

    for col in matches.columns.to_list():
        if col in all_dtypes.keys():
            dtypes[col] = all_dtypes[col]

    return dtypes


def get_mongo_client():
    config = configparser.ConfigParser()
    config.read("config.ini")
    mongo_client = config['mongo']['client']
    return MongoClient(mongo_client)


def get_matches_collection():
    mongo_cli = get_mongo_client()
    database = mongo_cli["tennis"]
    return database["matches"]


def query_previous_match_date(match_date):
    collection = get_matches_collection()
    prev_match = list(collection.find({'datetime': {'$lt': match_date}}).sort('datetime', -1).limit(1))
    return prev_match[0]["datetime"] if len(prev_match) > 0 else None


def query_next_match_date(match_date):
    collection = get_matches_collection()
    next_match = list(collection.find({'datetime': {'$gte': match_date + timedelta(days=1)}}).sort('datetime').limit(1))
    return next_match[0]["datetime"] if len(next_match) > 0 else None


def mongodb_project_if_exists(field):
    return {
        '$cond': [
            {"$eq": ["", "${0}".format(field)]},
            "$$REMOVE",
            "${0}".format(field)
        ]
    }


def query_matches(match_date):
    collection = get_matches_collection()

    pipeline = [
        {'$match':
            {'datetime': {'$gte': match_date, '$lt': match_date + timedelta(days=1)}}
         },
        {'$lookup':
            {
                'from': 'tournaments',
                'localField': 'tournament_id',
                'foreignField': 'flash_id',
                'as': 'tour_info'
            }
         },
        {'$unwind': '$tour_info'},
        {'$lookup':
            {
                'from': 'players',
                'localField': 'p1_id',
                'foreignField': 'flash_id',
                'as': 'p1_info'
            }
         },
        {'$unwind': '$p1_info'},
        {'$lookup':
            {
                'from': 'players',
                'localField': 'p2_id',
                'foreignField': 'flash_id',
                'as': 'p2_info'
            }
         },
        {'$unwind': '$p2_info'},
        {'$project':
            {
                'match_id': 1,
                'status': 1,
                'datetime': 1,
                'p1_name': "$p1_info.full_name",
                'p2_name': "$p2_info.full_name",
                'tournament_name': "$tour_info.flash_name",
                'p1_s1_gms': mongodb_project_if_exists("score.p1_s1_gms"),
                'p1_s2_gms': mongodb_project_if_exists("score.p1_s2_gms"),
                'p1_s3_gms': mongodb_project_if_exists("score.p1_s3_gms"),
                'p1_s4_gms': mongodb_project_if_exists("score.p1_s4_gms"),
                'p1_s5_gms': mongodb_project_if_exists("score.p1_s5_gms"),
                'p2_s1_gms': mongodb_project_if_exists("score.p2_s1_gms"),
                'p2_s2_gms': mongodb_project_if_exists("score.p2_s2_gms"),
                'p2_s3_gms': mongodb_project_if_exists("score.p2_s3_gms"),
                'p2_s4_gms': mongodb_project_if_exists("score.p2_s4_gms"),
                'p2_s5_gms': mongodb_project_if_exists("score.p2_s5_gms"),
                'p1_proba': mongodb_project_if_exists("prediction.p1_proba"),
                'p2_proba': mongodb_project_if_exists("prediction.p2_proba"),
                'p1_wins': mongodb_project_if_exists("p1_wins")
            }
         },
        {'$sort':
            {'datetime': 1}
         }
    ]

    matches = pd.DataFrame(list(collection.aggregate(pipeline)))

    if len(matches.index) > 0:
        matches = matches.astype(get_match_dtypes(matches))
        # numpy nan values not interpreted by jinja
        matches = matches.replace({np.nan: None})

    return matches


def normalize_matches(match_list):
    matches = pd.json_normalize(match_list)

    '''for embedded in ["p1", "p2", "tournament", "score", "stats", "features", "prediction"]:
        matches.columns = matches.columns.str.replace(rf'^{embedded}\.', '') '''

    matches.columns = matches.columns.str.replace(r'^p1\.', '')
    matches.columns = matches.columns.str.replace(r'^p2\.', '')
    matches.columns = matches.columns.str.replace(r'^tournament\.', '')
    matches.columns = matches.columns.str.replace(r'^score\.', '')
    matches.columns = matches.columns.str.replace(r'^stats\.', '')
    matches.columns = matches.columns.str.replace(r'^features\.', '')
    matches.columns = matches.columns.str.replace(r'^prediction\.', '')

    return matches


def q_find_match_by_id(match_id):
    collection = get_matches_collection()

    pipeline = [
        {'$match':
             {'match_id': match_id}
         },
        {'$lookup':
            {
                'from': 'tournaments',
                'localField': 'tournament_id',
                'foreignField': 'flash_id',
                'as': 'tour_info'
            }
         },
        {'$unwind': '$tour_info'},
        {'$lookup':
            {
                'from': 'players',
                'localField': 'p1_id',
                'foreignField': 'flash_id',
                'as': 'p1_info'
            }
         },
        {'$unwind': '$p1_info'},
        {'$lookup':
            {
                'from': 'players',
                'localField': 'p2_id',
                'foreignField': 'flash_id',
                'as': 'p2_info'
            }
         },
        {'$unwind': '$p2_info'},
        {'$unwind': '$stats'},
        {'$project':
            {
                'match_id': 1,
                'status': 1,
                'datetime': 1,
                'p1_name': "$p1_info.full_name",
                'p2_name': "$p2_info.full_name",
                'tournament_name': "$tour_info.flash_name",
                # Score
                'p1_s1_gms': mongodb_project_if_exists("score.p1_s1_gms"),
                'p1_s2_gms': mongodb_project_if_exists("score.p1_s2_gms"),
                'p1_s3_gms': mongodb_project_if_exists("score.p1_s3_gms"),
                'p1_s4_gms': mongodb_project_if_exists("score.p1_s4_gms"),
                'p1_s5_gms': mongodb_project_if_exists("score.p1_s5_gms"),
                'p2_s1_gms': mongodb_project_if_exists("score.p2_s1_gms"),
                'p2_s2_gms': mongodb_project_if_exists("score.p2_s2_gms"),
                'p2_s3_gms': mongodb_project_if_exists("score.p2_s3_gms"),
                'p2_s4_gms': mongodb_project_if_exists("score.p2_s4_gms"),
                'p2_s5_gms': mongodb_project_if_exists("score.p2_s5_gms"),
                # Stats
                'p1_ace': "$stats.p1_ace",
                'p1_df': "$stats.p1_df",
                'p1_svpt': '$stats.p1_svpt',
                'p1_1st_in': '$stats.p1_1st_in',
                'p1_1st_won': '$stats.p1_1st_won',
                'p1_2nd_won': '$stats.p1_2nd_won',
                'p1_sv_gms': '$stats.p1_sv_gms',
                'p1_bp_saved': '$stats.p1_bp_saved',
                'p1_bp_faced': '$stats.p1_bp_faced',
                'p1_2nd_pts': '$stats.p1_2nd_pts',
                'p1_svpt_won': '$stats.p1_svpt_won',
                'p1_1st_serve_ratio': '$stats.p1_1st_serve_ratio',
                'p1_svpt_ratio': '$stats.p1_svpt_ratio',
                'p1_1st_won_ratio': '$stats.p1_1st_won_ratio',
                'p1_2nd_won_ratio': '$stats.p1_2nd_won_ratio',
                'p1_sv_gms_won': '$stats.p1_sv_gms_won',
                'p1_sv_gms_won_ratio': '$stats.p1_sv_gms_won_ratio',
                'p1_bp_saved_ratio': '$stats.p1_bp_saved_ratio',
                'p2_ace': "$stats.p2_ace",
                'p2_df': "$stats.p2_df",
                'p2_svpt': '$stats.p2_svpt',
                'p2_1st_in': '$stats.p2_1st_in',
                'p2_1st_won': '$stats.p2_1st_won',
                'p2_2nd_won': '$stats.p2_2nd_won',
                'p2_sv_gms': '$stats.p2_sv_gms',
                'p2_bp_saved': '$stats.p2_bp_saved',
                'p2_bp_faced': '$stats.p2_bp_faced',
                'p2_2nd_pts': '$stats.p2_2nd_pts',
                'p2_svpt_won': '$stats.p2_svpt_won',
                'p2_1st_serve_ratio': '$stats.p2_1st_serve_ratio',
                'p2_svpt_ratio': '$stats.p2_svpt_ratio',
                'p2_1st_won_ratio': '$stats.p2_1st_won_ratio',
                'p2_2nd_won_ratio': '$stats.p2_2nd_won_ratio',
                'p2_sv_gms_won': '$stats.p2_sv_gms_won',
                'p2_sv_gms_won_ratio': '$stats.p2_sv_gms_won_ratio',
                'p2_bp_saved_ratio': '$stats.p2_bp_saved_ratio',
                
                'p1_proba': mongodb_project_if_exists("prediction.p1_proba"),
                'p2_proba': mongodb_project_if_exists("prediction.p2_proba"),
                'p1_wins': mongodb_project_if_exists("p1_wins")
            }
        }
    ]

    matches = pd.DataFrame(list(collection.aggregate(pipeline)))

    return matches.iloc[0]
