import dataExtraction
import dataPlotter
import json

data_collec = dataExtraction.collect_data(sub='funny',maxposts=10,interval_sec=30,duration_min=2,feedback=True,savefile='example.json')

with open('example.json') as j:
    data_collec = json.load(j)
    for data in data_collec:
        data = dataExtraction.offset_timestamp(data, -7)

dataPlotter.plot_collec(data_collec)
