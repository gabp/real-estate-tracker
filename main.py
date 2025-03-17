import json
import centris
import os
import redis_db

path_prefix = 'C:/Users/Gab/Documents/prog/python/centris'

db = redis_db.DB()
data_fetcher = centris.CentrisDataFetcher()
sold_ids = db.get_sold_ids()

query_file_names = os.listdir(path_prefix + './queries')
#query_file_names = ['condo-griffintown.json']
for query_file_name in query_file_names:

    # get config
    query_file = open(path_prefix + './queries/' + query_file_name, 'r')
    query_string = query_file.read()
    query = json.loads(query_string)

    # fetch and save price
    c = centris.CentrisPriceFetcher(query_file_name, query["path"], query["query"])
    centris_results = c.get_all()
    db.save(query_file_name, centris_results)

    # update sold ids
    centris_results_ids = [centris_result[0] for centris_result in centris_results]
    results_in_redis = db.get_unsold_prices_by_tag(query_file_name)

    sold_ids = [id for id in results_in_redis.keys() if id not in centris_results_ids]
    db.add_ids_as_sold(sold_ids)

    # get property data
    data_dict = db.get_data_by_tag(query_file_name)
    missing_data_ids = [ id for id in data_dict if data_dict[id] is None and id not in sold_ids ]

    if len(missing_data_ids) == 0:
        continue

    res = data_fetcher.fetch_data_for_ids(missing_data_ids)
    db.save_data(res)
    