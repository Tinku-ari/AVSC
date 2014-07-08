import pandas as pd
import numpy as np

data=pd.read_csv("hist_offers_transaggr.csv")
del data['index'] #redundant
del data['quantity']  # only 1 unique val, so useless
data.replace(to_replace=['NaN'],value=np.nan, inplace=True)
print data.shape
column_names=list(data.columns.values)
print column_names[10:14]
print set(data['productsize'].dropna())
for column_name in column_names[11:11]:
    print column_name,set(data[column_name])
    
