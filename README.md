## Emulating human chess intelligence
### using Tensorflow and Stockfish

The intention behind this project is to find a way to extract useful *"state-decision"* data from my own chess game archive,
and to develop a machine learning model using this to emulate my ability.

Older games should be exponentially less impactful, under the assumption of a *"learning curve"*.

#### Links
- Tensorflow: <https://www.tensorflow.org/>
- Stockfish: <https://pypi.org/project/stockfish/>
- Python-Chess: <https://python-chess.readthedocs.io/en/latest/>

APIs:
- [chess.com](https://www.chess.com/news/view/published-data-api)
- [lichess.org](https://lichess.org/api)

#### Requires

`coupled_stockfish_engine.STOCKFISH_PATH` should point to a stockfish executable