import redis_db
import os
from prettytable import PrettyTable
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def display_results(results, head=20, price_limit=600000):
    table = PrettyTable()
    table.field_names = ["Current Price ($)", "Old Price ($)", "Change ($)", "Change (%)", "Raw Change ($)", "Raw Change (%)", "Price Fluctuation", "Link"]

    for id in results:
        prices = results[id]

        previous_price = prices[0]
        current_price = prices[-1]
        arrows = ''
        price_fluctuation = f'{str(prices[0])}$'

        last_price = prices[0]
        for i in range(1, len(prices)):
            price = prices[i]

            if price > last_price:
                arrows += '\u2191'
                price_fluctuation = f'{price_fluctuation} \u2192 {str(price)}$'
            elif price < last_price:
                arrows += '\u2193'
                price_fluctuation = f'{price_fluctuation} \u2192 {str(price)}$'
            
            last_price = price
        
        if len(arrows) == 0:
            price_fluctuation = ''


        if current_price > price_limit:
            continue

        change = ''
        raw_change_percent = 100*(previous_price/current_price - 1)
        change_percent = f'{raw_change_percent:.2f}'

        if previous_price > current_price:
            change = f'{bcolors.OKGREEN}{previous_price - current_price} \u2193{bcolors.ENDC}'
            change_percent = f'{bcolors.OKGREEN}{change_percent} \u2193{bcolors.ENDC}'
        elif previous_price < current_price:
            change = f'{bcolors.FAIL}{current_price - previous_price} \u2191{bcolors.ENDC}'
            change_percent = f'{bcolors.FAIL}{change_percent} \u2191{bcolors.ENDC}'
        else:
            change = f'0'
            change_percent = '0'

        table.add_row([current_price, previous_price, change, change_percent, previous_price - current_price, raw_change_percent, price_fluctuation, f'https://www.centris.ca{id}'])


    # display
    table.align = 'r'
    table.sortby = 'Raw Change (%)'
    table.reversesort = True
    table.start = 0
    table.end = head
    table.fields = ["Current Price ($)", "Change ($)", "Change (%)", "Price Fluctuation", "Link"]

    print(table)

    # print average of results
    avg_price = sum([r[0] for r in table._rows]) / len(table._rows)
    avg_old_price = sum([r[1] for r in table._rows]) / len(table._rows)
    print_avg_table(avg_price, avg_old_price)


def print_avg_table(avg_price, avg_old_price):

    # init table
    avg_table = PrettyTable()
    
    # compte change values
    avg_change = avg_old_price - avg_price
    avg_change_percent = f'{abs(100*(avg_old_price/avg_price - 1)):.2f}'

    # color stuff
    if avg_change > 0:
        avg_change = f'{bcolors.OKGREEN}{avg_change:.0f} \u2193{bcolors.ENDC}'
        avg_change_percent = f'{bcolors.OKGREEN}{avg_change_percent} \u2193{bcolors.ENDC}'
    elif avg_change < 0:
        avg_change = f'{bcolors.FAIL}{abs(avg_change):.0f} \u2191{bcolors.ENDC}'
        avg_change_percent = f'{bcolors.FAIL}{avg_change_percent} \u2191{bcolors.ENDC}'
    else:
        avg_change = '0'
        avg_change_percent = '0'

    # only 1 row
    avg_table.add_row([f'{avg_price:.0f}', avg_change, avg_change_percent])

    # display
    avg_table.field_names = ["Average Price ($)", "Change ($)", "Change (%)"]
    avg_table.align = 'r'
    print(avg_table)




# get data
db = redis_db.DB()

last_number_of_days = 100
results = {}
queries_displayed = []
query_file_names = os.listdir('./queries')
for query_file_name in query_file_names:
    if len(sys.argv) == 1 or sys.argv[1] in query_file_name:
        results.update(db.get_unsold_prices_by_tag(query_file_name, last_number_of_days=last_number_of_days))
        queries_displayed.append(query_file_name)

# print
display_results(results, head=20, price_limit=800000)
print(f'Results of {queries_displayed} in the last {last_number_of_days} days.')
print()
