import threading
from _thread import start_new_thread
from flask import Flask, session, make_response
from flask import render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
import json
import time

# TODO sid'get switched
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SESSION_COOKIE_HTTPONLY'] = False
socketio = SocketIO(app, manage_session=True)

players = []  # playerlist for lobby
playersGame = []  # playerlist for game
playersReady = 0  # amount of players that are ready to play


class Game:
    players = []  # list of players
    setCards = ["none", "none", "none", "none"]  # cards on table
    cardsLeft = []  # cards that needs to be given to the players
    rounds = 0
    lastPlayer = None
    passAmount = 0
    state = None

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
    reload = False

    def __init__(self, name, sid):
        self.sid = sid
        self.name = name
        self.state = "lobby"


game = Game


@socketio.on('redirect')  # event to handle redirect from index to lobby in index.js
def redirect():
    emit('redirect', {'url': url_for('lobby')})  # send url to redirect to


@socketio.on('new_player')  # event that handles new player in lobby.js
def new_player():
    global players
    exists = False
    for player in players:
        if player.name == session["username"]:
            exists = True
            break
    if not exists:
        players.append(Player(session["username"], request.sid))  # construct new player object
        if len(players) == 1:  # if this is only player
            emit('host', room=players[0].sid)  # event to set to lobbyhost
        emit('update_player_amount', {'amountP': len(players)}, broadcast=True)  # event to update playeramount


@socketio.on('disconnect')  # event that handles every disconnection of every client
def disconnect():
    global players
    inLobby = True
    for player in players:
        if player.sid == request.sid:  # finds player with sid of event
            inLobby = False
            if players[0].sid == player.sid:  #
                players.remove(player)  # removes player
            try:
                players.remove(player)
            except ValueError:
                pass
            emit('update_player_amount', {'amountP': len(players)}, broadcast=True)
            del player  # destruct objekt
            break
    try:
        emit('host', room=players[0].sid)
    except IndexError:
        pass
    if not inLobby:
        start_new_thread(checkDiscFunc, (request.sid,))


def checkDiscFunc(sid):
    time.sleep(0.5)
    for player in game.players:
        if player.sid == sid:
            game.players.remove(player)
            del player
            break


@socketio.on('start')
def start():  # event is sent after host started the game in lobby.js
    global playersGame
    playersGame = players.copy()  # copies current playerlist cause players get remove on disconnect event (redirect in next step = new Socket connection)
    emit("redirect", {'url': url_for('gameFunc')}, broadcast=True)  # redirects


@app.route('/game')
def gameFunc():
    testlist = []
    global game
    game = Game()
    for player in game.players:
        player = player.__dict__
        testlist.append(player)

    return render_template('game.html', players=json.dumps(testlist), playerAmount=len(
        testlist))  # render template with list of players that were in the lobby to start the game


@socketio.on('hello_game')  # event is sent after connection in game.js
def hello_game(username):
    global playersReady
    reload = False
    for player in game.players:  # for each player
        if player.name == username:  # find objekt of session were the event is emitted from
            player.sid = request.sid  # set sid to new sid
            if player.state == "ingame":
                givePlayerCards(player)
                player.reload = True
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
                           playerAmount=len(players))  # render template for the lobby with live playeramount


@app.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":  # if formular is posted
        taken = False  #
        username = request.form["name"]  #
        for player in players:  # set taken to True if name is already taken
            if player.name == username:  #
                taken = True  #
                break  #
        for c in username:
            if c == " ":
                nameText = "No spaces in name!"
                return render_template('index.html', nameText=nameText)

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
    game.state = "ongoing"
    for player in players:
        del player
    players.clear()
    giveCardsEachPlayer()  # give players the cards once
    nextPlayer()


def giveCardsEachPlayer():
    global playersGame
    global game
    cardsEachPlayer = 52 / len(game.players)  # Cards Amount / Amount of Player
    x = 0
    for player in game.players:
        tempCards = []
        player.state = "ingame"
        player.cards.clear()  # Clear cards of each player (else bug that list append else other???)
        i = 0
        while i < int(cardsEachPlayer):
            if len(game.cardsLeft) > 1:
                card = game.cardsLeft[random.randrange(0, len(game.cardsLeft) - 1)]  # choose random card of left cards
                tempCards.append(card)  # append random card
                game.cardsLeft.remove(card)  # remove card from the cards that are left
            elif len(game.cardsLeft) == 1:
                card = game.cardsLeft[0]
                tempCards.append(card)  # append random card
                game.cardsLeft.remove(card)  # remove card from the cards that are left
            i += 1
        game.players[x].cards = tempCards
        game.players[x].cards.sort()
        x += 1
        emit("ownCards", player.cards, room=player.sid)


def givePlayerCards(player):
    emit("ownCards", player.cards, room=player.sid)


@socketio.on('chooseCard')
def chooseCard(card1, card2, card3, card4):
    global game
    actualCardsSet = []
    for card in game.setCards:
        if card != "none":
            actualCardsSet.append(card)
    index = {"B": 11, "D": "12", "K": 13, "A": 14}
    cardsAll = [card1, card2, card3, card4]
    cardsValue = []
    for card in cardsAll:
        if card != "none":
            if len(card) > 2:
                cardValue = card[0:2]
            else:
                cardValue = card[0]
            cardsValue.append(cardValue)

    n = 0
    badCard = False
    # test if submitted cards have same value
    while n < len(cardsValue):
        more = 0
        try:
            nValue = index[cardsValue[n]]
        except KeyError:
            nValue = cardsValue[n]
        while more < len(cardsValue):
            try:
                moreValue = index[cardsValue[more]]
            except KeyError:
                moreValue = cardsValue[more]

            if nValue == moreValue:
                more += 1
            else:
                badCard = True
                break
        if not badCard:
            n += 1
        else:
            badCards()
            return

    if game.rounds == 0:
        setCards(card1, card2, card3, card4)
        # check if cards are higher then given one
    else:
        if len(cardsValue) == len(actualCardsSet):
            try:
                indexedValue = index[cardsValue[0]]
            except KeyError:
                indexedValue = cardsValue[0]

            if len(game.setCards[0]) > 2:
                setCardValue = game.setCards[0][0:2]
            else:
                setCardValue = game.setCards[0][0]
            try:
                indexedSetValue = index[setCardValue]
            except KeyError:
                indexedSetValue = setCardValue
            if int(indexedValue) > int(indexedSetValue):
                setCards(card1, card2, card3, card4)
            else:
                badCards()
        else:
            badCards()


def setCards(card1, card2, card3, card4):
    global game
    cards = [card1, card2, card3, card4]
    actualCards = []
    for card in cards:
        if card != "none":
            actualCards.append(card)
    n = 0
    while n < len(cards):
        game.setCards[n] = cards[n]
        n += 1
    emit("update_middle", {"card1": card1, "card2": card2, "card3": card3, "card4": card4}, broadcast=True)
    for player in game.players:
        if player.sid == request.sid:
            game.lastPlayer = player
            game.passAmount = 0
            index = game.players.index(player)
            for card in actualCards:
                player.cards.remove(card)
            if len(player.cards) == 0:
                emit("winner", {"winner": player.name}, broadcast=True)
                reset()
                break
            else:
                emit("update_playerCards", {"index": index, "value": len(player.cards)}, broadcast=True)
                game.rounds += 1
                nextPlayer()


def reset():
    global game
    global playersGame
    global playersReady
    players.clear()  # playerlist for lobby
    playersGame = []  # playerlist for game
    playersReady = 0  # amount of players that are ready to play
    del game
    game = Game()


@socketio.on("pass")
def passFunc():
    global game
    if game.passAmount < len(game.players) - 1:
        game.passAmount += 1
        nextPlayer()
    else:
        game.rounds = 0
        card1 = "none"
        card2 = "none"
        card3 = "none"
        card4 = "none"
        emit("update_middle", {"card1": card1, "card2": card2, "card3": card3, "card4": card4}, broadcast=True)
        emit("yourTurn", room=request.sid)


def badCards():
    emit("badCards", room=request.sid)


currentPlayer = 0


def nextPlayer():
    global currentPlayer
    global playersGame

    if currentPlayer < len(playersGame):
        if currentPlayer == 0:
            lastPlayerID = len(playersGame) - 1
        else:
            lastPlayerID = currentPlayer - 1
        emit("update_currentPlayer", {"cid": currentPlayer, "lid": lastPlayerID}, broadcast=True)
        emit("yourTurn", room=playersGame[currentPlayer].sid)
    else:
        currentPlayer = 0
        emit("update_currentPlayer", {"cid": currentPlayer, "lid": len(playersGame) - 1}, broadcast=True)
        emit("yourTurn", room=playersGame[currentPlayer].sid)

    currentPlayer += 1


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
