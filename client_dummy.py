"""
GO DUMMY CLIENT 
Implementation by Francisco Silva - up202109000 - GROUP 2

"""

import socket
import asyncio
import random
import time


def process_end(response):
    result_values = [val.strip() for val in response.replace('END ', '').split() if val.isdigit()]

    if len(result_values) == 3:
        winner_index, winner_score, opponent_score = map(int, result_values)
        winner_label = 'AG1' if winner_index == 1 else 'AG2'
        print('*' * 50)
        print(f" END OF THE GAME : {winner_label} WINS ")
        #print(f"{winner_label} WINS with a score of {winner_score} against {opponent_score}.")
        print('*' * 50)


async def connect_to_server(host='localhost', port=12345):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    response = client_socket.recv(1024).decode()
    print(f"Server Response INIT: {response}")

    Game = response[-4:]
    print("Playing:", Game)

    size = next((char for char in Game if char.isdigit()), None)

    if size is not None:
        actual_board_size = int(size)
    else:
        print("Board size not defined by the server.")
        client_socket.close()

    if "1" in response:
        ag = 1
    else:
        ag = 2
    first = True

    print('*' * 50)
    print(f"\nBoard Size:{actual_board_size}  STARTING GAME \n")
    print('*' * 50)

    while True:

        print("\nPLAYS AG", ag)

        if ag == 1 or not first:
            if random.randint(1, 100) <= 5:  # 5% chance to send a PASS move
                move = "PASS"
                print("AG{} passed.".format(ag))
            else:
                x = random.randint(0, 8)
                y = random.randint(0, 8)
                print("AG{} played at coordinates ({}, {}) ".format(ag, x, y))
                move = f"MOVE {x},{y},{0},{0}"

            time.sleep(1)
            client_socket.send(move.encode())
            print("Send:", move)

            # Wait for server response
            response = client_socket.recv(1024).decode()
            print(f"Server Response1: {response}")

            if "END" in response:
                process_end(response)
                break

            if "INVALID" in response:
                continue

        first = False

        response = client_socket.recv(1024).decode()
        print(f"Server Response2: {response}")
        if "END" in response:
            process_end(response)
            break

        if "PASS" not in response:
            input_values = [val.strip() for val in response.replace('MOVE ', '').split(",") if val.isdigit()][:2]
            x, y = map(int, input_values)
            opponent = 'AG2' if ag == 1 else 'AG1'
            print("{} played at coordinates ({}, {}))".format(opponent, x, y))

    client_socket.close()


async def main():
    await connect_to_server()


if __name__ == "__main__":
    asyncio.run(main())

