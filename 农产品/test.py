import pandas as pd

data = {'A':[1,2,3],'B':[3,4,5]}
df = pd.DataFrame(data)
city = 'taiyuan'
df.to_csv(f"{city}/test.csv")