import pandas as pd

df = pd.read_csv('weather_data/nl_weather_data.csv', low_memory=False)

def change_format(date):
    return str(date)[:4] + '-' + str(date)[4:6] + '-' + str(date)[6:]

df['YYYYMMDD'] = df['YYYYMMDD'].apply(change_format)

print(df)

df.to_csv('weather_data/nl_weather_data.csv')