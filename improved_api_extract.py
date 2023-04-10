import requests, time, json, os
import coupled_stockfish_engine as cse

def expand_fen(fen_string: str, blank_char: str = ' ') -> str:
    out_string = ''
    fen_string = fen_string.split('-')
    rows = fen_string[0].split('/')
    if fen_string[1] not in ['w','b']: raise ValueError('incorrectly reading player from fen string')
    player = 0 if fen_string[1] == 'w' else 0
    for y in range(8):
        for x in range(8):
            piece = rows[y][x]
            try:
                val = int(piece)
                if val!=0:
                    rows[y] = rows[y][:x] + val*blank_char + rows[y][x+1:]
                for i in range(val):
                    out_string += val*blank_char
                x += val
            except ValueError:
                out_string += piece
    return (out_string, player)
#print(expand_fen("r1bq2nr/2pk1Bpp/p4p2/np2p3/1P3P2/PQP1P2P/6P1/R1B1K1NR w KQ - 3 14"))

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
   
r_temp = list(r)
while len(r_temp) != 0:
    request = requests.get('https://api.chess.com/pub/player/the111thtom/games/{year}/{month:02d}'.format(year=y,month=m))
    r_temp = request.json()['games']
    m -= 1
    if m==0:
        y -= 1
        m = 12
    r = r_temp + r

'''
MAX_GAMES = 50 # truncate list at number of games
if len(r) > MAX_GAMES:
    r = r[-MAX_GAMES:]
'''

    
out_json = {'data_points':[]}
reference_time = r[0]['end_time']
time_range = r[-1]['end_time'] - reference_time

for i in range(len(r), 0, -1): # iterate over games from api
    j = r[i-1]
    with open('bin\\temp.pgn', 'w') as f:
        f.write(j['pgn'])
        f.close()

    sf = cse.CoupledStockfish('bin\\temp.pgn', 'The111thTom', out=False)
    try:
        states, b = sf.run()
        for s in states: # add all states to output json
            fen, p = expand_fen(s['fen'])
            _state = {
                'player': p,
                'fen': fen,
                'following_move': s['move'],
                'resulting_eval': s['eval'],
                'game_time': (j['end_time'] - reference_time) / time_range,
            }
            out_json['data_points'].append(_state)
        #print(str(i+1)+' of '+str(len(r)), end='\r')
        print(str(i)+' of '+str(len(r)))
    except ValueError:
        print('skipped game '+str(i))

print(str(len(out_json['data_points']))+' game states extracted from '+str(len(r))+' games')
# save output json and dispose of temp file
with open('bin\\full_dataset\\out.json', 'w') as file:
    json.dump(out_json, file)
os.remove('bin\\temp.pgn')