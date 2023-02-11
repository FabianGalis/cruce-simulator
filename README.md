# cruce-simulator
A game of custom Romanian/Hungarian "Cruce" using python sockets. It allows players to make up their own rules, so it can be considered just a base on which players can still play with custom rules in accordance to how people play in their respective regions.

## How to play the actual game

The game is similar to the historical card game of "66" with a few modifications. The official base rules can be found here https://tromf.ro/tutorial.htm (in Romanian).
In practice, there are many regions where the game is played differently than this "official" documented version, so this project is not restrictive in terms of rules as it allows players maximum freedom.

However, there's a set of basic rules that stay the same regardless of region:
* All cards get divided equally to players;
* Players know at all times the following information: their hand, their points, who is leading the game, current placed trick;
* Players can't put more cards than a single one on the current trick;
* All players have to contribute to the current trick in order for it to be able to be taken by one of them;
* All card points get accumulated once trick is taken (player specific).

When playing this game's version with python sockets, everything works by pressing the right keys as instructed by the terminal. (There's a graphical interface in the works.)

## How the game works internally

The program consists of the following files:
* `card_logic_classes.py` - contains Enums for card names and suites, along with their points, and a class representing a card deck to handle the cards;
* `cruce_server.py` - a multi-threaded server that handles all players, stores every information about the game state (leaderboard, player decks, current trick etc.);
* `cruce_client.py` - one client for each player, includes a menu in the terminal to help players see what keys must they press to do the various actions.

This program is based on an exchange of a JSON between players and the main server. The flow of a regular game is as follows:
1. Server opened for connections;

2. Player connects to the server;
3. Player inputs and sends their name;
4. Server deals cards to player.
5. Exchange of JSON between player - server (until player hand is empty)

(steps 2,3,4,5 executed in parallel for all players)

6. Server declares winner;
7. Server resets.

The JSON that is passed around is structured as follows:

```javascript
{
  'action':'action_name'
  'data':[specific data, any type]
}
```

## Action list and what they do

### Client -> Server
| Action name | Associated data | What it does |
| --- | --- | --- |
| `send_name` | string name | Sends a name for the server to register the player |
| `trick_status` | - | Request current trick |
| `point_status` | - | Request the player's current points |
| `place_on_trick` | card | Try to place a card of player's choice on the current trick |
| `take_trick` | - | Try taking the current trick if eligible |
| `lead` | - | Request leaderboard |
| `quit` | - | Disconnect from the game |

### Server -> Client
| Action name | Associated data | What it does |
| --- | --- | --- |
| `connection_success` | string message | Welcome message and connection success confirmation |
| `initial_cards` | [card list] | Deal the starting cards |
| `trick_status` | dict of {player_name : card} | Send current trick, with each card from the trick belonging to a player |
| `point_status` | int value | Send a player's current points |
| `place_on_trick` | string message | Confirmation/error message for player placing a card on the current trick |
| `take_trick` | string message | Confirmation/error message for player taking the current trick |
| `lead` | tuple of (int points, {player set}) | Send the number of max points and the player(s) that own them |
| `quit` | string message | Quitting confirmation message |
