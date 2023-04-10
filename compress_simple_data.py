import json

out_json = {}
j = json.load(open('bin\\full_dataset\\out.json','r'))
l = len(j['data_points'])

for i in range(l):
    dp = j['data_points'][i]
    print(str(i)+'/'+str(l), end='\r')
    fen = dp['fen']
    move = {
        'move':dp['following_move'],
        'eval':dp['resulting_eval'],
        'game_time':dp['game_time']
    }
    if fen not in out_json.keys():
        out_json[fen] = [[],[]]
    out_json[fen][dp['player']].append(move)

# removes any states with no alternate cases
for fen in list(out_json):
    dp = out_json[fen]
    if len(dp[0]) + len(dp[1]) == 1:
        out_json.pop(fen)


with open('bin\\full_dataset\\out_compressed.json', 'w') as file:
    json.dump(out_json, file)