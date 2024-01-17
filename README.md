# Game Server with Petting Zoo Classic Environment Wrapper

The server code (`server_zoo.py`) serves as a wrapper for the Petting Zoo Classic Environment Go V5, implementing game logic for 7x7 and 9x9 boards.

## Features

- Accepts and processes client moves (`MOVE x,y` or `PASS`).
- Detects and handles invalid moves, enforcing a turn change after the third invalid move.
- Implements TIMEOUT enforcing a turn change if the player's move takes more than *timeout* seconds (10 seconds as default)
- Generates a graphical representation of the board.
- Declares the end of the game with the victory of one of the players (`END 1 1 0` or `END 2 0 1`).

For a more detailed explanation of the code, please refer to (`server_client_go_explained.html`).

### Example Clients

In order to test the server code, several different clients have been implemented:

   - `client_dummy.py` : This client generates random coordinates, leading to invalid moves, and includes a percentage of 'PASS' moves.

   - `client_zoo_random.py`: This client is aware of the game rules and does not generate invalid moves, but it plays randomly without following any specific algorithm.

   - `client_zoo_model.py`: This client strictly adheres to the game rules and utilizes a trained model. It may produce a 'TIMEOUT' if the model takes more than 10 seconds to generate a move.


## Requirements

- Python version >= 3.10.13
- Tested on Ubuntu 22.04 (functionality on Windows not guaranteed)

## Installation

```bash
pip install pettingzoo[classic]
pip install asyncio 
pip install aioconsole
```

## Usage

The server can run on a different machine than the clients, as long as they are on the same IP subnet. 
Update the host in both the server and clients accordingly.

##### 1. Start the server
```bash
python server_zoo.py
```

##### 2. In a different terminal, launch a client (Dummy client in this example):
```bash
python client_dummy.py
```

##### 3. In yet another terminal, start another client (your model):
```bash
python your_client_model.py
```



## Bonus: Playing Against a Stable Baselines 3 PPO Trained Model

To assess the quality of your model, you can play against a Stable Baselines 3 PPO Reinforcement Learning trained model. Follow these steps:


##### 1. Install Stable Baselines 3 and sb3-contrib
```bash
pip install stable-baselines3 
pip install sb3-contrib
```

##### 2. Start the server
```bash
python server_zoo.py
```

##### 3. In a different terminal, launch the PPO model
```bash
python client_zoo_model.py
```
##### 4. In yet another terminal, start your client model:
```bash
python your_client_model.py
```
Enjoy!
