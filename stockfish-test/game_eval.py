with open('sample_game.pgn','r') as f:
    out = f.readlines()
    f.close()

out = [out[i].strip() for i in range(len(out))]
#print(out)

player = 0 if '"The11thTom"' in out[4] else 1
moves = ''
for k in range(13,len(out)):
    moves = moves + ' ' + out[k]
print(moves)