"""
GO  CLIENT PLAYING RANDOM - wrapper for Petting Zoo Client Go V5 - Classic Environment 
Implementation by Francisco Silva - up202109000 - GROUP 2

"""

import socket
import asyncio
from pettingzoo.classic import go_v5

def coordinates_to_action(x, y, N):
    return N * x + y


def action_to_coordinates(action_id, N):
    x = action_id // N
    y = action_id % N
    return x, y



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
    print(f"\nServer Response INIT: {response}")
    
    Game = response[-4:]
    print("Playing:", Game)

    size = next((char for char in Game if char.isdigit()), None)

    if size is not None:
        actual_board_size = int(size)
    else:
        print("Board size not defined by the server.")
        client_socket.close()
    
    if "1" in response:
        ag=1
    else:
        ag=2
    first=True


    env = go_v5.env(render_mode=None , board_size=actual_board_size, komi=5.5,screen_height=300)
    env.reset()

    print(env)

  
    print('*' * 50)
    print(f"\nBoard Size:{actual_board_size}  STARTING GAME \n")
    print('*' * 50)

    while True:
        
        #env.render()
       
        print("\nPLAYS AG", ag)

        if ag == 1 or not first:
            observation, reward, termination, truncation, info = env.last()
            obs, action_mask = observation.values()

            act = env.action_space(env.agent_selection).sample(action_mask)

            if act == actual_board_size**2:
                move = "PASS"
                print("AG{} passed.".format(ag))
            else:
                x, y = action_to_coordinates(act, actual_board_size)
                print("AG{} played at coordinates ({}, {})  ( action: {} )".format(ag, x, y, act))
                move = f"MOVE {x},{y},{0},{0}"

            client_socket.send(move.encode())
            print("Send:", move)

            # Wait for server response
            response = client_socket.recv(1024).decode()
            print(f"Server Response1: {response}")

            if "END" in response:
                process_end(response)
                break

            elif "INVALID" in response:
                continue

            elif "TIMEOUT" in response:
                pass

            else:
                if termination == False and truncation == False:
                    env.step(act)

            
        first=False

        #Wait for opponent play
        response = client_socket.recv(1024).decode()
        print(f"Server Response2: {response}")

        if "END" in response: 
            process_end(response)
            #env.close()
            break

        if ("PASS" in response) or ("TIMEOUT" in response):

            act = actual_board_size ** 2

            observation, reward, termination, truncation, info = env.last()
            obs, action_mask = observation.values()

            
            if  termination == False and truncation == False:
                env.step(act)
                opponent = 'AG2' if ag == 1 else 'AG1'
                print("{} PASSED  ( action: {} )".format(opponent,act))
            
        else:

            input_values = [val.strip() for val in response.replace('MOVE ', '').split(",") if val.isdigit()][:2]
            x, y = map(int, input_values)

            act=coordinates_to_action(x,y,actual_board_size)

            observation, reward, termination, truncation, info = env.last()
            obs, action_mask = observation.values()

            
            if  termination == False and truncation == False:
                env.step(act)
                opponent = 'AG2' if ag == 1 else 'AG1'
                print("{} played at coordinates ({}, {})  ( action: {} )".format(opponent, x, y, act))

           
    env.close()
    client_socket.close()



async def main():
    await connect_to_server()


if __name__ == "__main__":
    asyncio.run(main())
