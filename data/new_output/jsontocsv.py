import json
import pandas as pd

with open('summary.json', 'r', encoding='utf-8') as f:
    data = json.loads(f.read())


for el in data:
    print(el["transcript"], len(el["overlaps"]))

# # create dataframe
# df = pd.json_normalize(data)

# df.to_csv('csvfile.csv', encoding='utf-8', index=False)