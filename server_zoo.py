"""
GO Server - wrapper for Petting Zoo  Go V5 - Classic Environment 
Implementation by Francisco Silva - up202109000 - GROUP 2

"""

import asyncio
import aioconsole
from pettingzoo.classic import go_v5
import socket
import time
import select

def coordinates_to_action(x, y, N):
    x,y = y,x                                #INVERT ROWS AND COLUMNS
    return N * x + y


def action_to_coordinates(action_id, N):
    x = action_id // N
    y = action_id % N
    return x, y


def is_valid_move(env, action_mask, actual_board_size, data):

    if data.startswith('MOVE'):
        input_values = [val.strip() for val in data.replace('MOVE ', '').split(",") if val.isdigit()][:2]

        if len(input_values) == 2:
            x, y = map(int, input_values)

            if x > actual_board_size or y > actual_board_size:
                print(f"Invalid input. x and y must be less than {actual_board_size}.")
                return False, -1

            if x == actual_board_size and y != 0:
                print(f"Invalid input. To Pass, please use x == {actual_board_size} and y == 0.")
                return False, -1

            action_id = coordinates_to_action(x, y, actual_board_size)
            print("Valid move from {}: coordinates ({}, {})  ( action: {} )".format(env.agent_selection, x, y, action_id))

        else:
            print(f"Invalid input. Please enter 'MOVE x,y'.")
            return False, -1

    elif data.strip().upper() == 'PASS':
        x, y = actual_board_size, 0
        action_id = actual_board_size ** 2
        print(f"Valid PASS from {env.agent_selection}. ( action: {action_id} )")


    elif data.strip().upper() == 'TIMEOUT':
        x, y = actual_board_size, 0
        action_id = actual_board_size ** 2
        print(f"TIMEOUT from {env.agent_selection}.Passing the turn ( action: {action_id} )")


    else:
        print("Invalid input. Please enter 'MOVE x,y' or 'PASS'.")
        return False, -1

    if action_mask[action_id] == 0:
        print("Invalid move (action_mask == 0). Please enter a legal move.")
        return False, -1

    return True, action_id

def receive_data_with_timeout(agent, timeout, ag, agent_mapping):
    start_time = time.time()  # Record the start time

    try:
        agent.settimeout(None)
        data = agent.recv(1024).decode()

        elapsed_time = time.time() - start_time
        agent_label = agent_mapping.get(ag, ag)
        print(f"Received data from {agent_label} in {elapsed_time:.2e} seconds.")

        if elapsed_time > timeout:
            raise socket.timeout("TIMEOUT")
        else:
            return data

    except socket.timeout:
        elapsed_time = time.time() - start_time
        agent_label = agent_mapping.get(ag, ag)
        print(f"{agent_label} TIMEOUT after {elapsed_time:.2e} seconds. Passing the turn.")
        return "TIMEOUT"

       

   


async def start_server(host='localhost', port=12345):
    server_socket = None
    error_occurred = False

    try: 

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(2)

        print("Waiting for two agents to connect...")
        agent1, addr1 = server_socket.accept()
        
        print("Agent 1 connected from", addr1)

        #********************* DEFINE GAME TYPE AND BOARD SIZE **************

        Game = "G9x9"  # "G7x7" 

        #********************************************************************

        size = next((char for char in Game if char.isdigit()), None)

        if size is not None:
            actual_board_size = int(size)
        else:
            print("Board size not defined.")


        bs = b'AG1 ' + Game.encode()
        agent1.sendall(bs)

        agent2, addr2 = server_socket.accept()
        print("Agent 2 connected from", addr2)
        bs = b'AG2 ' + Game.encode()
        agent2.sendall(bs)

        agents = [agent1, agent2]
        current_agent = 0


        env = go_v5.env(render_mode="human", board_size=actual_board_size, komi=5.5)
        env.reset()

        print(env)

        scores = {agent: 0 for agent in env.possible_agents}
        total_rewards = {agent: 0 for agent in env.possible_agents}
        round_rewards = []


        agent_mapping = {env.possible_agents[0]: 'AG1', env.possible_agents[1]: 'AG2'}

        agent_mapping2 = {0: 'AG1', 1: 'AG2'}

        print('*' * 50)
        print(f"\nBoard Size:{actual_board_size}  STARTING GAME \n")
        print('*' * 50)
        jog = 0

        num_agents = len(env.possible_agents)
        consecutive_illegal_inputs = [0] * num_agents

        #************************* set TIMEOUT *************
        timeout=10


        while True:
            try:

                data=None
                data = receive_data_with_timeout(agents[current_agent], timeout, current_agent, agent_mapping2)
            #agent_label = agent_mapping2.get(current_agent, current_agent)
                #print(f"{agent_label} DATA: -> {data}")
                if data is None:
                    break

                env.render()
                print("\nPLAYS: ", env.agent_selection)

                observation, reward, termination, truncation, info = env.last()
                obs, action_mask = observation.values()

                #If Game Finished
                if termination or truncation:

                    if env.rewards[env.possible_agents[0]] != env.rewards[env.possible_agents[1]]:
                        winner = max(env.rewards, key=env.rewards.get)
                        scores[winner] += env.rewards[winner]
                        winner_label = agent_mapping.get(winner, winner)
                        print('*' * 50)
                        print(f"\n END OF THE GAME - Victory : {winner_label}\n")
                        print('*' * 50)

                        opponent = env.possible_agents[1] if winner == env.possible_agents[0] else env.possible_agents[0]

                        if winner == env.possible_agents[0]:
                            result_string = f'END 1 {scores[winner]} {scores[opponent]}'
                        elif winner == env.possible_agents[1]:
                            result_string = f'END 2 {scores[winner]} {scores[opponent]}'

                    else:
                        result_string = 'END 0 0 0'  # Tie

                    for a in env.possible_agents:
                        total_rewards[a] += env.rewards[a]
                    round_rewards.append(env.rewards)
                

                    # Send the result string to both agents
                    agents[current_agent].sendall(result_string.encode())
                    agents[1 - current_agent].sendall(result_string.encode())

                    user_input = await aioconsole.ainput("\n Press <Enter> to  Finish")
                    break

                else:
                    print(f"{agent_mapping[env.possible_agents[current_agent]]} -> {data}")

                    jog = jog + 1

                    if jog == 2 ** 63 :
                        agents[current_agent].sendall(b'END 0 0 0')
                        agents[1 - current_agent].sendall(b'END 0 0 0')
                        break

                    valid, action_id = is_valid_move(env, action_mask, actual_board_size, data)

                    if valid:
                        act = action_id
                        env.step(act)

                        consecutive_illegal_inputs[current_agent] = 0

                        agents[current_agent].sendall(b'VALID')
                        agents[1 - current_agent].sendall(data.encode())
                    
                        current_agent = 1 - current_agent

                    #invalid movement
                    else:

                        #if it is the third consecutive  pass the turn
                        if consecutive_illegal_inputs[current_agent] >= 3:
                            
                            print("Three consecutive illegal inputs. Passing the turn.")
                            act = actual_board_size ** 2
                            env.step(act)
                            #x,y = action_to_coordinates(act,actual_board_size)
                            move=f"PASS"

                            agents[current_agent].sendall(move.encode())
                            agents[1 - current_agent].sendall(move.encode())

                            consecutive_illegal_inputs[current_agent] = 0
                            current_agent = 1 - current_agent

                        #if is not the third consecutive send invalid an repeat
                        else:
                            agents[current_agent].sendall(b'INVALID')

                            consecutive_illegal_inputs[current_agent] += 1
            except Exception as e:
                error_occurred = True
                print("Error during the game loop:", e)
                break               

    except Exception as e:
        error_occurred = True
        print("Error during the game:", e)

    finally:
            # Close the server socket in case of an error
        if server_socket:
            server_socket.close()
        
        # Only execute the remaining code if no error occurred
        if not error_occurred:
            winner = max(scores, key=scores.get)
            opponent = 'white_0' if winner.startswith('black') else 'black_0'

            # Mapping the winner and opponent names to 'AG1' and 'AG2'
            winner_label = agent_mapping.get(winner, winner)
            opponent_label = agent_mapping.get(opponent, opponent)

            # Print the result
            print(f"\nThe winner is {winner_label} with score: {scores[winner]} vs. {opponent_label} with score: {scores[opponent]}.")
            print("\nRewards by round: ", round_rewards)
            env.close()
            time.sleep(1)
            agent1.close()
            agent2.close()
            

async def main():
    await start_server()


if __name__ == "__main__":
    asyncio.run(main())
