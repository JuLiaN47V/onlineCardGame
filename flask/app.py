import threading
from flask import Flask, session, make_response
from flask import render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SESSION_COOKIE_HTTPONLY'] = False
socketio = SocketIO(app, manage_session=True)

players = []  # playerlist for lobby
playersGame = []  # playerlist for game
playersReady = 0  # amount of players that are ready to play


class Game:
    players = None  # list of players
    setCards = None  # cards on table
    cardsLeft = None  # cards that needs to be given to the players

    def __init__(self):
        self.players = playersGame  # list of players
        self.cardsLeft = [  # cards that needs to be given to the players at start
            "2T", "2P", "2H", "2K",
            "3T", "3P", "3H", "3K",
            "4T", "4P", "4H", "4K",
            "5T", "5P", "5H", "5K",
            "6T", "6P", "6H", "6K",
            "7T", "7P", "7H", "7K",
            "8T", "8P", "8H", "8K",
            "9T", "9P", "9H", "9K",
            "10T", "10P", "10H", "10K",
            "BT", "BP", "BH", "BK",
            "DT", "DP", "DH", "DK",
            "KT", "KP", "KH", "KK",
            "AT", "AP", "AH", "AK"
        ]


class Player:
    sid = None  # socket sid
    name = None  # username
    state = None  # state
    cards = []  # cards on hand

    def __init__(self, name, sid):
        self.sid = sid
        self.name = name
        self.state = "lobby"


@socketio.on('redirect')  # event to handle redirect from index to lobby in index.js
def redirect():
    emit('redirect', {'url': url_for('lobby')})  # send url to redirect to


@socketio.on('new_player')  # event that handles new player in lobby.js
def new_player():
    global players
    players.append(Player(session["username"], request.sid))  # construct new player object
    if len(players) == 1:  # if this is only player
        emit('host', room=players[0].sid)  # event to set to lobbyhost
    emit('update_player_amount', {'amountP': len(players)}, broadcast=True)  # event to update playeramount


@socketio.on('disconnect')  # event that handles every disconnection of every client
def disconnect():
    global players
    for player in players:
        if player.sid == request.sid:  # finds player with sid of event
            if players[0].sid == player.sid:  #
                players.remove(player)  # removes player
                try:
                    emit('host', room=players[0].sid)  # tries to set host to first player
                except IndexError:
                    pass
            else:
                players.remove(player)
            del player  # destruct objekt
            break
    emit('update_player_amount', {'amountP': len(players)}, broadcast=True)


@socketio.on('start')
def start():  # event is sent after host started the game in lobby.js
    global playersGame
    playersGame = players.copy()  # copies current playerlist cause players get remove on disconnect event (redirect in next step = new Socket connection)
    emit("redirect", {'url': url_for('game')}, broadcast=True)  # redirects


@app.route('/game')
def game():
    testlist = []
    for player in playersGame:
        player = player.__dict__
        testlist.append(player)

    print(testlist)
    return render_template('game.html', players=json.dumps(testlist), playerAmount=len(testlist))  # render template with list of players that were in the lobby to start the game


@socketio.on('hello_game')  # event is sent after connection in game.js
def hello_game(username):
    global playersGame
    global playersReady
    reload = False
    for player in playersGame:  # for each player
        if player.name == username:  # find objekt of session were the event is emitted from
            player.sid = request.sid  # set sid to new sid
            if player.state == "ingame":
                givePlayerCards(player)
                reload = True
            else:
                player.state = "game_ready"  # set state to ready
                playersReady += 1  # count up the amount of players that are ready
    if not reload:
        if playersReady == len(playersGame):  # if all players are ready
            startGame()


@app.route('/lobby')
def lobby():
    global players
    return render_template('lobby.html',
                           playerAmount=len(players))  # render tamplate for the lobby with live playeramount


@app.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":  # if formular is posted
        taken = False  #
        username = request.form["name"]  #
        for player in players:  # set taken to True if name is already taken
            if player.name == username:  #
                taken = True  #
                break  #
        if not taken:  # if name is not taken:
            session["username"] = username  # set Session cookie for username
            nameText = "Current name: " + username  # set display text
            socketio.emit('joinLobbyBTN')  # Event to create button to join gamelobby
            resp = make_response(render_template('index.html', nameText=nameText))  # create response with template
            resp.set_cookie('username', username)  # set cookie in response
            return resp
        else:  # if name is taken:
            nameText = "Name is already taken"  # set display text
            return render_template('index.html', nameText=nameText)
    elif "username" in session:  # if the site is entered and cookie with username is set
        nameText = "Current name: " + session["username"]  # set display text do username
        socketio.emit('joinLobbyBTN')  # event to create button to join gamelobby
        return render_template('index.html', nameText=nameText)
    else:
        nameText = "Please set a name"  # if site is entered without cookie
        return render_template('index.html', nameText=nameText)


def startGame():  # The entire game
    giveCardsEachPlayer()  # give players the cards once
    for player in playersGame:
        socketio.emit("yourTurn", room=player.sid)


def giveCardsEachPlayer():
    global playersGame
    cardsEachPlayer = 52 / len(playersGame)  # Cards Amount / Amount of Player
    game = Game()
    for player in playersGame:
        player.state = "ingame"
        player.cards.clear()  # Clear cards of each player (else bug that list append else other???)
        i = 0
        while i < int(cardsEachPlayer):
            if len(game.cardsLeft) > 1:
                card = game.cardsLeft[random.randrange(0, len(game.cardsLeft) - 1)]  # choose random card of left cards
            else:
                card = game.cardsLeft[0]
            player.cards.append(card)  # give player card
            game.cardsLeft.remove(card)  # remove card from the cards that are left
            i += 1
        emit("ownCards", player.cards, room=player.sid)


def givePlayerCards(player):
    emit("ownCards", player.cards, room=player.sid)


@socketio.on('chooseCard')
def chooseCard(cardID):
    print(cardID)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
