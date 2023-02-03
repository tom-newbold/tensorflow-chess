import requests, time, json, os
import coupled_stockfish_engine as cse

y = time.gmtime().tm_year
m = time.gmtime().tm_mon
# fetch most recent game archive
r = []
while len(r) == 0:
    request = requests.get('https://api.chess.com/pub/player/the111thtom/games/{year}/{month:02d}'.format(year=y,month=m))
    r = request.json()['games']
    m -= 1
    if m==0:
        y -= 1
        m = 12


MAX_GAMES = 300 # truncate list at number of games
if len(r) > MAX_GAMES:
    r = r[-MAX_GAMES:]

out_json = {'data_points':[]}
reference_time = r[0]['end_time']
time_range = r[-1]['end_time'] - reference_time

for i in range(len(r)): # iterate over games from api
    j = r[i]
    with open('bin\\temp.pgn', 'w') as f:
        f.write(j['pgn'])
        f.close()

    sf = cse.CoupledStockfish('bin\\temp.pgn', 'The111thTom', out=False)
    states, b = sf.run()
    p = sf.player
    for s in states: # add all states to output json
        _state = {
            'player': p,
            'fen': s['fen'],
            'following_move': s['move'],
            'resulting_eval': s['eval'],
            'game_time': (j['end_time'] - reference_time) / time_range,
        }
        out_json['data_points'].append(_state)
    print(str(i)+' of '+str(len(r)))


print(str(len(out_json['data_points']))+' game states extracted from '+str(len(r))+' games')
# save output json and dispose of temp file
with open('bin\\out.json', 'w') as file:
    json.dump(out_json, file)
os.remove('bin\\temp.pgn')