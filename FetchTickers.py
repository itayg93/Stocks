def fetch_nasdaq_tickers(self):
    resp = requests.get('https://en.wikipedia.org/wiki/NASDAQ-100')
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find(
        'table', {'class': 'wikitable sortable', 'id': 'constituents'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[1].text
        tickers.append(ticker.split())
    with open("nasdaq100tickers.pickle", "wb") as f:
        pickle.dump(tickers, f)
