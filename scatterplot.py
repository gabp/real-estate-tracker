import redis_db
import os
from prettytable import PrettyTable
import sys
import centris
import matplotlib.pyplot as plt


def update_annot(ind):

    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    text = labels[ind["ind"][0]]
    
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.4)


def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()


def click(event):
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        print(centris.centris_url + labels[ind["ind"][0]])


# get data
db = redis_db.DB()

data = {}
prices = {}
queries_displayed = []
query_file_names = os.listdir('./queries')
for query_file_name in query_file_names:
    if len(sys.argv) == 1 or sys.argv[1] in query_file_name:
        data.update(db.get_data_by_tag(query_file_name))
        prices.update(db.get_unsold_prices_by_tag(query_file_name, last_number_of_days=0))


# filter missing data
xs = []
ys = []
labels = []
for id in data:
    d = data[id]

    if d is None or id not in prices:
        continue
    
    area = d['area']

    if area is None or area <= 0:
        continue

    # get last price
    price = prices[id][-1]

    if price < 900000:
        xs.append(area)
        ys.append(price)
        labels.append(id)


# display
fig,ax = plt.subplots()
sc = plt.scatter(xs, ys)

annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

fig.canvas.mpl_connect("motion_notify_event", hover)
fig.canvas.mpl_connect("button_press_event", click)

plt.show()