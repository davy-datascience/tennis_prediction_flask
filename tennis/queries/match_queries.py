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


def get_match_collection():
    mongo_cli = get_mongo_client()
    database = mongo_cli["tennis"]
    return database["matches"]


def query_previous_match_date(match_date):
    collection = get_match_collection()
    prev_match = list(collection.find({'datetime': {'$lt': match_date}}).sort('datetime', -1).limit(1))
    return prev_match[0]["datetime"] if len(prev_match) > 0 else None


def query_next_match_date(match_date):
    collection = get_match_collection()
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
    collection = get_match_collection()

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
                'status': 1,
                'datetime': 1,
                'p1_name': "$p1_info.full_name",
                'p2_name': "$p2_info.full_name",
                'tournament_name': "$tour_info.flash_name",
                'p1_s1_gms': mongodb_project_if_exists("p1_s1_gms"),
                'p1_s2_gms': mongodb_project_if_exists("p1_s2_gms"),
                'p1_s3_gms': mongodb_project_if_exists("p1_s3_gms"),
                'p1_s4_gms': mongodb_project_if_exists("p1_s4_gms"),
                'p1_s5_gms': mongodb_project_if_exists("p1_s5_gms"),
                'p2_s1_gms': mongodb_project_if_exists("p2_s1_gms"),
                'p2_s2_gms': mongodb_project_if_exists("p2_s2_gms"),
                'p2_s3_gms': mongodb_project_if_exists("p2_s3_gms"),
                'p2_s4_gms': mongodb_project_if_exists("p1_s4_gms"),
                'p2_s5_gms': mongodb_project_if_exists("p1_s5_gms"),
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
