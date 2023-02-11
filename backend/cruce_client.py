import socket, json
from card_logic_classes import *

connected = False

#connect to server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect(("127.0.0.1",64433))
connected = True

#get name request
received = server_socket.recv(1024)
received = json.loads(received)

print(received['data'])

#send name and register player to server
to_send = received
to_send['data']=str(input("Input your name: "))
to_send = json.dumps(to_send).encode()
server_socket.send(to_send)

#initialise empty deck in hand
hand=Deck(True)

# get cards
received = server_socket.recv(1024)
received = json.loads(received)

for card in received['data']:
    hand.add_card(card)

while connected:

    # if game didn't end yet (cards still in hand)
    if hand.cards:

        to_send={'action':'default','data':''}
        print("-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-")
        print("Current hand: ", hand.cards)
        print("0. Quit")
        print("1. See trick status")
        print("2. See point status")
        print("3. Take current trick")
        print("4. Place card on trick")
        print("5. Check who is leading")
        print("-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-=x=-")

        option=int(input())

        if option==0:
            to_send['action']='quit'
            to_send['data']=hand.cards
            connected=False
        elif option==1: to_send['action']='trick_status'
        elif option==2: to_send['action']='point_status'
        elif option==5: to_send['action']='lead'
        elif option==3: to_send['action']='take_trick'

        
        elif option==4:
            to_send['action']='place_on_trick'
            picked_position=int(input("Enter card position:"))
            card_to_place=hand.extract_card(picked_position)
            while not card_to_place:
                picked_position=int(input("Enter card position:"))
                card_to_place=hand.extract_card(picked_position)
            to_send['data']=card_to_place
        

        # sending
        to_send = json.dumps(to_send).encode()
        server_socket.send(to_send)

        # getting answer + printing in a pretty way
        received = server_socket.recv(1024)  
        received = json.loads(received)

        # EXCEPTIONS
        if received['action']=='wrong_trick_place':
            #get card back in player hand
            hand.add_card(card_to_place)
            #print warning
            print(received['data'])
        elif received['action']=='wrong_take_trick':
            print(received['data'])
        
        # SUCCESSFUL REPLIES
        elif received['action']=='trick_status':
            print("Current trick is: ", received['data'])
        elif received['action']=='point_status':
            print("Your current points are: ", received['data'])
        elif received['action']=='place_on_trick':
            print("You placed ",card_to_place)
            print("Current trick is now: ",received['data'])
        elif received['action']=='lead':
            print(f"{received['data'][1]} leading with {received['data'][0]} points.")
        else: # for take_trick, disconnected + unknown messages
            print(received['data'])

    else:
        print("Waiting for other players to finish...")
        #wait for last message to see who won
        received = server_socket.recv(1024)  
        received = json.loads(received)
        print("GAME OVER\nThe winner is: ",received['data'])
        connected=False

#disconnecting
server_socket.close()