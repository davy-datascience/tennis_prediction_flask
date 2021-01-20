import configparser
import pandas as pd
import numpy as np

from datetime import timedelta
from pymongo import MongoClient


def get_match_dtypes():
    return {"p1_s1_gms": "Int16","p1_s2_gms": "Int16", "p1_s3_gms": "Int16", "p1_s4_gms": "Int16", "p1_s5_gms": "Int16",
            "p2_s1_gms": "Int16","p2_s2_gms": "Int16", "p2_s3_gms": "Int16", "p2_s4_gms": "Int16", "p2_s5_gms": "Int16"}


def get_mongo_client():
    config = configparser.ConfigParser()
    config.read("config.ini")
    mongo_client = config['mongo']['client']
    return MongoClient(mongo_client)


def get_matches(match_date):
    mongo_cli = get_mongo_client()
    database = mongo_cli["tennis"]
    collection = database["matches"]

    pipeline = [{'$match':
                     {'datetime': {'$gte': match_date, '$lt': match_date + timedelta(days=1)}}
                 },
                {'$lookup':
                     {'from': 'tournaments',
                      'localField': 'tournament_id',
                      'foreignField': 'flash_id',
                      'as': 'tour_info'
                      }
                },
                {'$unwind': '$tour_info'},
                {'$lookup':
                     {'from': 'players',
                      'localField': 'p1_id',
                      'foreignField': 'flash_id',
                      'as': 'p1_info'
                      }
                 },
                {'$unwind': '$p1_info'},
                {'$lookup':
                     {'from': 'players',
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
                        'p1_s1_gms': 1,
                        'p1_s2_gms': 1,
                        'p1_s3_gms': 1,
                        'p1_s4_gms': 1,
                        'p1_s5_gms': 1,
                        'p2_s1_gms': 1,
                        'p2_s2_gms': 1,
                        'p2_s3_gms': 1,
                        'p2_s4_gms': 1,
                        'p2_s5_gms': 1,
                        'p1_wins': 1
                    }
                }]

    matches = pd.DataFrame(list(collection.aggregate(pipeline)))

    if len(matches.index) > 0:
        matches = matches.astype(get_match_dtypes())
        # numpy nan values not interpreted by jinja
        matches = matches.replace({np.nan: None})

    return matches
