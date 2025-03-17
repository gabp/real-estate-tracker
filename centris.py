import requests
import re
from progress.bar import Bar
import logging
import contextlib
import json
try:
    from http.client import HTTPConnection # py3
except ImportError:
    from httplib import HTTPConnection # py2

def debug_requests_on():
    '''Switches on logging of the requests module.'''
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

def debug_requests_off():
    '''Switches off logging of the requests module, might be some side-effects'''
    HTTPConnection.debuglevel = 0

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.handlers = []
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.WARNING)
    requests_log.propagate = False

@contextlib.contextmanager
def debug_requests():
    '''Use with 'with'!'''
    debug_requests_on()
    yield
    debug_requests_off()


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'}
centris_url = 'https://www.centris.ca'

class CentrisPriceFetcher:

    query_file_name = ''
    path = ''
    query = ''
    nbr_of_items = 0
    s = None
    bar = None

    def __init__(self, query_file_name, path, query):
        
        self.query_file_name = query_file_name
        self.path = path
        self.query = query

        self.bar = Bar(f'Processing {self.query_file_name} ')
        self.s = requests.Session()
        self.s.headers.update(headers)

        # first req
        r = self.s.get(centris_url + self.path)

        # lock
        r = self.s.post(centris_url + '/UserContext/Lock', headers={'Content-Type':'application/json'}, data='{"uc":0}')
        uck = r.text

        self.s.headers.update({'X-CENTRIS-UC': '0', 'X-CENTRIS-UCK':uck})

        # session type
        r = self.s.post(centris_url + '/UserContext/SetSessionTypeUser', headers={'Content-Type':'application/json'})

        # unlock
        r = self.s.post(centris_url + '/UserContext/UnLock', headers={'Content-Type':'application/json'}, data='{"uc":0,"uck":' + uck + '}')
        assert r.text == 'true', r.text
        

    def update_query(self):
        self.s.post(centris_url + '/property/UpdateQuery', headers={'Content-Type':'application/json'}, data=self.query)


    def get_all(self):
        
        if self.query.strip() != '':
            self.update_query()

        # get all
        max_found = False
        results = tuple()
        start_position = 0
        while True:
            r = self.s.post(centris_url + '/Property/GetInscriptions', headers={'Content-Type':'application/json'}, data='{"startPosition":' + str(start_position) + '}')

            ids = [m.group(1) for m in re.finditer(r'class=\\"a-more-detail\\" href=\\"([a-z\~\-0-9\\/]+)', r.text)]
            prices = [m.group(1) for m in re.finditer(r'itemprop=\\"price\\" content=\\"([0-9]+)\\"', r.text)]

            if len(ids) == 0:
                print()
                break
            
            if not max_found:
                j = json.loads(r.text)
                self.bar.max = int(int(j['d']['Result']['count']))
                max_found = True

            self.bar.next(len(ids))
            results += tuple(zip(ids, prices))
            start_position += 20

        return results



class CentrisDataFetcher:

    s = None
    bar = None

    def __init__(self):
        
        self.s = requests.Session()
        self.s.headers.update(headers)


    def fetch_data_for_ids(self, ids):

        results = {}

        self.bar = Bar(f'Fetching Data ')
        self.bar.max = len(ids)

        for id in ids:
            r = self.s.get(centris_url + id)

            if r.status_code != 200:
                results[id] = None
                self.bar.next(1)
                continue

            area = [m.group(1) for m in re.finditer(r'<span>([0-9 ]+) pc</span>', r.text)]
            if len(area) == 0:
                area = -1
            else:
                area = int(area[0].replace(' ', ''))

            results[id] = { 'area': area }
            self.bar.next(1)

        print()

        return results
