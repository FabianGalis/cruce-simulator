import socket, threading, time, json
from card_logic_classes import *

class Server():

    def __init__(self,TCP_IP,TCP_PORT):

        self.PLAYERS = list()

        self.TCP_IP=TCP_IP
        self.TCP_PORT=TCP_PORT

        #starting deck
        self.main_deck=Deck()
        self.main_deck.shuffle_deck()

        #player decks
        self.player_decks={}

        #current trick
        self.current_trick={}

        #current leaders [points,{players}]
        self.leaderboard = [0,{'no one'}]


    def startServer(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((self.TCP_IP,self.TCP_PORT))
            s.listen(10)

            while len(self.PLAYERS)<5: # player limit
                player_socket, addr = s.accept()
                print (f'Connected with {addr[0]} : {addr[1]}')
                # register player
                self.PLAYERS.append(player_socket)
                print ("Player count is now ",len(self.PLAYERS))
                threading.Thread(target=self.playerHandler, args=(player_socket,)).start()

            s.close()
        except socket.error as msg:
            print (f'THREAD ERROR - code : {msg[0]}, message : {msg[1]}')
            return


   #client handler :one of these loops is running for each thread/player   
    def playerHandler(self, player_socket):
        #send welcome msg to new client and request name
        to_send = {"action": "connection_success","data": "Waiting for players to join...\nWhen all players are ready, choose your name to receive cards."}
        to_send = json.dumps(to_send).encode()
        player_socket.send(to_send)

        received = player_socket.recv(1024)
        received = json.loads(received)

        #assign name to current player thread
        player_name = received['data']

        #distribute 4 cards per player
        to_send = {"action": "initial_cards","data": self.main_deck.take_from_top(24//len(self.PLAYERS))}
        to_send = json.dumps(to_send).encode()
        player_socket.send(to_send)

        #initialize empty player deck
        self.player_decks[player_name] = Deck(True)
        connected=True

        #GAME LOGIC
        while connected:
            received = player_socket.recv(1024)
            received = json.loads(received)

            print("GOT ",received)
            #initialise default response
            to_send = received

            # request current trick status
            if received['action']=='trick_status':
                to_send['data']=self.current_trick

            # request current points
            elif received['action']=='point_status':
                to_send['data']=self.player_decks[player_name].total_points
            

            # place card on trick + trick status
            elif received['action']=='place_on_trick':

                #if trick is empty, take leading suite to be the suite of first card
                if not self.current_trick:
                    self.current_trick['lead_suite']=received['data'][1]

                #check to see if player already placed a card on trick
                if player_name in self.current_trick:
                    to_send['action']='wrong_trick_place'
                    to_send['data']='You already placed a card!'
                else:
                    # place sent card and send current trick to player
                    self.current_trick[player_name] = received['data']
                    to_send['data']=self.current_trick
            
            # take trick
            elif received['action']=='take_trick':
                if len(self.PLAYERS)+1 == len(self.current_trick): # plus additional checks
                    #delete leading suite
                    self.current_trick.pop('lead_suite')
                    #take cards from trick and put them in the player deck
                    for player in self.current_trick:
                        self.player_decks[player_name].add_card(self.current_trick[player])

                    to_send['data']='Trick taken!'
                    self.current_trick.clear()

                    #update leaderboard
                    if self.player_decks[player_name].total_points==self.leaderboard[0]:
                        self.leaderboard[1].add(player_name)

                    elif self.player_decks[player_name].total_points>self.leaderboard[0]:
                        self.leaderboard[0]=self.player_decks[player_name].total_points
                        self.leaderboard[1]={player_name}
                        to_send['data']+=f"\nYou've taken the lead with {self.player_decks[player_name].total_points} points!"

                else:
                    to_send['action']='wrong_take_trick'
                    to_send['data']='Not eligible to take trick!'

            #disconnect
            elif received['action']=='quit':
                #put cards in hand back in the main deck
                for card in received['data']:
                    self.main_deck.add_card(card)

                #put cards from deck in the main deck
                for card in self.player_decks[player_name].cards:
                    self.main_deck.add_card(card)

                #delete player deck
                self.player_decks.pop(player_name)

                to_send['action']='disconnected'
                to_send['data']=f'You have successfully disconnected as {player_name}.\nCards collected successfully.'

                #exit loop
                connected=False

            #check leading player
            elif received['action']=='lead':
                to_send['data']=[self.leaderboard[0],list(self.leaderboard[1])]


            else: to_send={'action':'unrecognized','data':'ERROR - UNRECOGNIZED ACTION, try again'}

            # send response
            to_send = json.dumps(to_send).encode()
            player_socket.send(to_send)

         # connection is closed
        print(player_name," DISCONNECTED")
        self.PLAYERS.remove(player_socket)





if __name__=="__main__":
    s = Server("127.0.0.1",64433) #create server
    threading.Thread(target=s.startServer).start()

    while 1:
        #print(s.CLIENTS)
        print("\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("Player count: ",len(s.PLAYERS))
        print("Cards in main deck: ", s.main_deck.cards)
        print("Player decks: ")
        for player in s.player_decks:
            print(s.player_decks[player].cards)
        print("Current trick: ",s.current_trick)
        print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\n")
        time.sleep(10) # print data every 10 s