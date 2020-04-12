from flask import Flask, session, make_response
from flask import render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SESSION_COOKIE_HTTPONLY'] = False
socketio = SocketIO(app, manage_session=True)

players = []
playersGame = []
playersSave = []
playersReady = 0


class Game:
    players = None
    setCards = None
    cardsLeft = None

    def __init__(self):
        self.players = playersSave
        self.cardsLeft = [
                          "2E", "2B", "2H", "2S",
                          "3E", "3B", "3H", "3S",
                          "4E", "4B", "4H", "4S",
                          "5E", "5B", "5H", "5S",
                          "6E", "6B", "6H", "6S",
                          "7E", "7B", "7H", "7S",
                          "8E", "8B", "8H", "8S",
                          "9E", "9B", "9H", "9S",
                          "10E", "10B", "10H", "10S",
                          "UE", "UB", "UH", "US",
                          "OE", "OB", "OH", "OS",
                          "KE", "KB", "KH", "KS",
                          "AE", "AB", "AH", "AS"
                          ]


class Player:
    sid = None
    name = None
    state = None
    cards = []

    def __init__(self, name, sid):
        self.sid = sid
        self.name = name
        self.state = "lobby"

    def getState(self):
        return self.state


@socketio.on('redirect')
def redirect():
    emit('redirect', {'url': url_for('lobby')})


@socketio.on('new_player')
def new_player():
    global players
    players.append(Player(session["username"], request.sid))
    if len(players) == 1:
        emit('host', room=players[0].sid)
    emit('update_player_amount', {'amountP': len(players)}, broadcast=True)


@socketio.on('disconnect')
def disconnect():
    global players
    for player in players:
        if player.sid == request.sid:
            if players[0].sid == player.sid:
                players.remove(player)
                try:
                    emit('host', room=players[0].sid)
                except IndexError:
                    pass
            else:
                players.remove(player)
            del player
            break
    emit('update_player_amount', {'amountP': len(players)}, broadcast=True)


@socketio.on('start')
def start():
    global playersSave
    playersSave = players.copy()
    emit("redirect", {'url': url_for('game')}, broadcast=True)


@app.route('/game')
def game():
    return render_template('game.html', players=playersSave)    #render template with list of players that were in the lobby to start the game


@socketio.on('hello_game')      #event is sent after connection in game.js
def hello_game(username):
    global playersGame
    global playersSave
    global playersReady
    playersGame = playersSave.copy()
    for player in playersGame:
        print("player")
        if player.name == username:
            player.sid = request.sid
            player.state = "game_ready"
            playersReady += 1
    print(playersReady)
    if playersReady == len(playersGame):
        startGame()


@app.route('/lobby')
def lobby():
    global players
    return render_template('lobby.html', playerAmount=len(players))     # render tamplate for the lobby with live playeramount


@app.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":                    # if formular is posted
        taken = False                               #
        username = request.form["name"]             #
        for player in players:                      #set taken to True if name is already taken
            if player.name == username:             #
                taken = True                        #
                break                               #
        if not taken:                                 # if name is not taken:
            session["username"] = username            # set Session cookie for username
            nameText = "Current name: " + username    # set display text
            socketio.emit('joinLobbyBTN')             # Event to create button to join gamelobby
            resp = make_response(render_template('index.html', nameText=nameText))  #create response with template
            resp.set_cookie('username', username)   # set cookie in response
            return resp
        else:                                          #if name is taken:
            nameText = "Name is already taken"         # set display text
            return render_template('index.html', nameText=nameText)
    elif "username" in session:                        # if the site is entered and cookie with username is set
        nameText = "Current name: " + session["username"]   # set display text do username
        socketio.emit('joinLobbyBTN')                       # event to create button to join gamelobby
        return render_template('index.html', nameText=nameText)
    else:
        nameText = "Please set a name"                  # if site is entered for the first time
        return render_template('index.html', nameText=nameText)


def startGame():             # The entire game
    giveCardsEachPlayer()


def giveCardsEachPlayer():
    global playersGame
    cardsEachPlayer = 52 / len(playersGame)     # Cards Amount / Amount of Player
    game = Game()
    for player in playersGame:
        player.cards.clear()                    # Clear cards of each player (else bug that list append else other???)
        i = 0
        while i < int(cardsEachPlayer):
            if len(game.cardsLeft) > 1:
                card = game.cardsLeft[random.randrange(0, len(game.cardsLeft) - 1)]     #choose random card of left cards
            else:
                card = game.cardsLeft[0]
            player.cards.append(card)       # give player card
            game.cardsLeft.remove(card)     # remove card from the cards that are left
            i += 1


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
