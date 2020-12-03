# %%
import sys

import constants
from communications import CommunicationsHandler
from gui import TablutGUI
from iterative_deepening import iterative_deepening_best_move
from utils import initialize_jit

if __name__ == '__main__' and True:  # TODO: REMOVE FALSE!
    if len(sys.argv) > 1:
        # Help
        if sys.argv[1] == "-h":
            print("\n\n Usage: "
                  "\n <White / Black> <timeout[s]> <ip>  :  Connect to game server and play as White/Black player"
                  "\n --interactive <human-white / human-black> <ai-white / ai-black> [timeout]: Play a match against ai"
                  "\n --aivsai [timeout]: for a match between ai \n")
            sys.exit(0)

        # Interactive
        if sys.argv[1] == "--interactive":
            if sys.argv[2] not in ("human-white", "human-black") or sys.argv[3] not in ("ai-white", "ai-black"):
                print("Parameter error")
                sys.exit(-1)
            if len(sys.argv) > 4:
                constants.DEFAULT_TIMEOUT = int(sys.argv[4])
            human_color = 'w' if sys.argv[2] == "human-white" else 'b'
            ai_color = 'w' if sys.argv[3] == 'ai-white' else 'b'
            TablutGUI().loop_interactive(human_color, ai_color)
            sys.exit(0)

        # AI vs AI
        if sys.argv[1] == "--aivsai":
            if len(sys.argv) > 2:
                constants.DEFAULT_TIMEOUT = int(sys.argv[2])
            TablutGUI().loop_ai()
            sys.exit(0)

    # Server connection
    if len(sys.argv) != 4:
        print("Wrong no. of arguments: {} provided but 3 needed".format(len(sys.argv) - 1))
        sys.exit(-1)

    print("Initializing...")
    initialize_jit()
    print("Initialization done!")

    arg_color = str(sys.argv[1])
    arg_timeout = int(sys.argv[2])
    arg_ip = str(sys.argv[3])

    if arg_color not in ("White", "Black"):
        print("Role \"{}\" not recognized".format(arg_color))
    player_color = 'w' if arg_color == "White" else 'b'
    player_name = "Hyper"

    print("Starting communication with ip {} with name {} and role {}".format(arg_ip, player_name, arg_color))
    communications_handler = CommunicationsHandler(name=player_name, ip=arg_ip, color=player_color, timeout=arg_timeout)
    print("Comms established")
    communications_handler.send_name()

    while 1:
        state, turn = communications_handler.listen_state()
        if turn == player_color:
            move = iterative_deepening_best_move(*state, player_color, arg_timeout)
            communications_handler.send_move(*move)
