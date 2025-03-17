import redis
import json
from datetime import date, timedelta, datetime

class DB():
    db = None

    def __init__(self):

        self.db = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
    
    def save(self, query_file_name, results):

        today = str(date.today())

        for result in results:
            id = result[0]
            price = result[1]

            # save result
            self.db.hset(id, today, price)

            # tag result
            self.db.sadd(query_file_name, id)
            self.db.sadd('all', id)
    

    def get_unsold_prices_by_tag(self, tag, last_number_of_days=7):
        
        # get unsold ids for tag
        sold_ids = self.db.smembers('sold')
        ids = [ id for id in self.db.smembers(tag) if id not in sold_ids ]

        results = {}

        for id in ids:
            prices = self.db.hgetall(id)
            if len(prices) == 0:
                return {}
            
            keys = list(prices.keys())
            keys_in_range = keys[-last_number_of_days - 1:]
            prices_in_range = [int(prices[key]) for key in keys_in_range]

            if len(prices_in_range) == 0:
                print(id)
                print(prices)

            results[id] = prices_in_range

        return results


    def save_data(self, results):

        for id in results:
            if results[id] == None:
                self.db.sadd('sold', id)
                continue

            self.db.set(id + ':data', json.dumps(results[id]))


    def get_data_by_tag(self, tag='all'):
        ids = self.db.smembers(tag)

        results = {}

        for id in ids:
            data = self.db.get(f'{id}:data')

            if data is not None:
                results[id] = json.loads(data)
            else:
                results[id] = None

        return results


    def get_sold_ids(self):
        ids = self.db.smembers('sold')

        return ids


    def add_ids_as_sold(self, ids):
        if len(ids) == 0:
            return

        self.db.sadd('sold', *ids)