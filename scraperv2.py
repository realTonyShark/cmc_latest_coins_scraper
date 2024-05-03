from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
cmc_api_key = os.getenv("CMC_API_KEY")

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS cryptocurrencies (
        id SERIAL PRIMARY KEY,
        name TEXT,
        price NUMERIC,
        date TIMESTAMP
    );
""")

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
  'start':'1',
  'limit':'50',
  'convert':'USD',
  'sort':'date_added',
  'sort_dir':'desc' 

}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': cmc_api_key,
}

session = Session()
session.headers.update(headers)

try:
  response = session.get(url, params=parameters)
  data = json.loads(response.text)
  print("success")
  print(data)

  for cryptocurrency in data['data']:
    name = cryptocurrency['name']
    price = cryptocurrency['quote']['USD']['price']
    date = cryptocurrency['date_added']
    print(f"{name} ${price} {date}")

    cur.execute("INSERT INTO cryptocurrencies (name, price, date) VALUES (%s, %s, %s);", (name, price, date))
    print(f"Inserted: {name}, {price}, {date}")

    conn.commit()
    print("Data insertion successful")

except (ConnectionError, Timeout, TooManyRedirects) as e:
    print("error:", e)

cur.close()
conn.close()