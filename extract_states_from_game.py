GAME_PATH = 'stockfish-test\\sample_game.pgn'

import coupled_stockfish_engine as cse
sf = cse.CoupledStockfish(GAME_PATH, 'The111thTom')

states, b = sf.run()
p = sf.player
out_json = {'data_points':[]}
for s in states:
    _state = {
        'player': p,
        'fen': s['fen'],
        'following_move': s['move'],
        'resulting_eval': s['eval']
    }
    out_json['data_points'].append(_state)

import json
with open('bin\\out.json', 'w') as file:
    json.dump(out_json, file)