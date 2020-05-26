import pandas as pd

df = pd.read_csv('output.csv', encoding='cp949')
df = df.drop_duplicates(keep='first')
df.to_csv('output_clean.csv', encoding='cp949')