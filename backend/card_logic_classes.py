from enum import IntEnum
import random

#cards and suites associated to their points
class Card(IntEnum):
    IX=0
    ALSO=2
    FELSO=3
    KIRALY=4
    X=10
    ASZ=11

class Suite(IntEnum):
    PIROS=1
    ZOLD=2
    TOK=3
    MAKK=4

#functions for sending/receiving cards without json
def card_to_bytes(card):
    _card=(Card[card[0]].value,Suite[card[1]].value)
    return str(int.from_bytes(_card, byteorder ='big')).encode()

def bytes_to_card(card_bytes):
    print("Bytes to convert:", card_bytes)
    _card = int(card_bytes)
    _card = tuple(_card.to_bytes(2, byteorder ='big'))
    _card = (Card(_card[0]).name,Suite(_card[1]).name)
    return _card

#represents pile of cards, be it a full one or a pile with points
class Deck():
    def __init__(selfie,empty=False):
        selfie._cards=list()

        #init for the main deck at the beginning of the game
        if not empty:
            for c in Card:
                for s in Suite:
                    selfie._cards.append((c.name,s.name))


    #shuffle cards
    def shuffle_deck(selfie): random.shuffle(selfie._cards)

    #see what's currently inside the deck
    @property
    def cards(selfie):
        return selfie._cards

    #put a card in the deck (at its end)
    def add_card(selfie,card):
        if card not in selfie._cards:
            selfie._cards.append(card)
        else: print(f"Card {card} already in deck!")

    #take cards from the top, deleting them from the deck
    def take_from_top(selfie,count=0):

        if(len(selfie._cards)>=count):
            picked_cards=selfie._cards[0:count]
            selfie._cards=selfie._cards[count:]
            return picked_cards
        else:
            print("Cannot take cards, deck smaller than requested quantity")
            return

    def extract_card(selfie,position):
        if(len(selfie._cards)>position):
            _picked_card=selfie._cards[position]
            selfie._cards.pop(position)
            return _picked_card
        else:
            print("Cannot extract card, index error")
            return

    #return sum of the cards in accordance to their points
    @property
    def total_points(selfie):
        return sum([Card[c[0]].value for c in selfie._cards])