import pandas as pd
import json

#this script normalize the SUB column in order to delete nested lists
table = pd.read_json('exp_elenco2024.json', orient='records')

def normalize(x):
    if x is not None:
        x = x[0]
    return x

table["SUB"] = table.apply(lambda row: normalize(row["SUB"]), axis=1)

#print(table[ table["Codice"] == "VEN24-AT.09.01.a"]["SUB"])

table.to_json('exp_elenco2024.json', orient='records', indent=4, default_handler=str)



