import redis_db
import os
from prettytable import PrettyTable
import sys
import redis
import json
import centris

# get data
db = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

ids = db.smembers('condo-griffintown.json')

#results = {}
#
#for id in ids:
#    data = db.get(f'{id}:data')
#
#    if data is not None:
#        results[id] = json.loads(data)
#    else:
#        results[id] = None
#
#print(results['/fr/condo~a-vendre~montreal-le-sud-ouest/28745307'])
#
#sold_ids = db.smembers('sold')
#missing_data_ids = [ id for id in results if results[id] is not None and id not in sold_ids ]
#
#print(missing_data_ids)


#data_fetcher = centris.CentrisDataFetcher()
#
#results = data_fetcher.are_ids_sold(['/fr/condo~a-vendre~montreal-le-sud-ouest/28745307'])
#
#print(results)

path_prefix = 'C:/Users/Gab/Documents/prog/python/centris'
query_file_name = 'condo-griffintown.json'
query_file = open(path_prefix + './queries/' + query_file_name, 'r')
query_string = query_file.read()
query = json.loads(query_string)

db = redis_db.DB()

sold_ids = db.get_sold_ids()
c = centris.CentrisPriceFetcher(query_file_name, query["path"], query["query"])
centris_results = c.get_all()
#centris_results_ids = [centris_result[0] for centris_result in centris_results]

#results_in_redis = db.get_unsold_prices_by_tag(query_file_name)

#for id_in_redis in results_in_redis.keys():
#    if id_in_redis not in sold_ids and id_in_redis not in centris_results_ids:
#        print(f"{id_in_redis} is sold!")
#    else:
#        print(f"{id_in_redis} is not sold!")

centris_results_ids = [centris_result[0] for centris_result in centris_results]
results_in_redis = db.get_unsold_prices_by_tag(query_file_name)

sold_ids = [id for id in results_in_redis.keys() if id not in centris_results_ids]

for id_in_redis in sold_ids:
    print(f"{id_in_redis} is sold!")

for id_in_centris in centris_results_ids:
    if id_in_centris not in sold_ids:
        print(f"{id_in_centris} is not sold!")

# get property data
#sold_ids = db.get_sold_ids()
#data_dict = db.get_data_by_tag(query_file_name)
#missing_data_ids = [ id for id in data_dict if data_dict[id] is None and id not in sold_ids ]