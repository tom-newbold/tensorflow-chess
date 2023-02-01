import requests, time, json

y = time.gmtime().tm_year
m = time.gmtime().tm_mon
# fetch most recent game
r = []
while len(r) == 0:
    request = requests.get('https://api.chess.com/pub/player/the111thtom/games/{year}/{month:02d}'.format(year=y,month=m))
    r = request.json()['games']
    m -= 1
    if m==0:
        y -= 1
        m = 12
j = r[-1]
print(json.dumps(j, indent=4))


#import coupled_stockfish_engine as cse
#sf = cse.CoupledStockfish('stockfish-test\\sample_game.pgn', 'The111thTom')