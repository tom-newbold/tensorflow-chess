import json

out_json = {}
j = json.load(open('bin\\inital_dataset.json','r'))
l = len(j['data_points'])

for i in range(l):
    dp = j['data_points'][i]
    print(str(i)+'/'+str(l))
    fen = dp['fen']
    move = {
        'move':dp['following_move'],
        'eval':dp['resulting_eval']
    }
    if fen not in out_json.keys():
        out_json[fen] = [[],[]]
    out_json[fen][dp['player']].append(move)

with open('bin\\inital_dataset_compressed.json', 'w') as file:
    json.dump(out_json, file)