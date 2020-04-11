from flask import Flask, session, make_response
from flask import render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room, emit

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
        self.cardsLeft = ["6E", "6B", "6H", "6S"]


class Player:
    sid = None
    name = None
    state = None
    cards = None

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
    me = Player(session["username"], request.sid)
    players.append(me)
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
    return render_template('game.html', players=playersSave)


@socketio.on('hello_game')
def hello_game(username):
    print("hello")
    global playersGame
    global playersSave
    global playersReady
    playersGame = playersSave.copy()
    for player in playersGame:
        if player.name == username:
            player.sid = request.sid
            player.state = "game_ready"
            playersReady += 1
    if playersReady == len(playersGame):
        startGame()


@app.route('/lobby')
def lobby():
    global players
    return render_template('lobby.html', playerAmount=len(players))


@app.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":
        taken = 0
        username = request.form["name"]
        for player in players:
            if player.name == username:
                taken = 1
                break
        if taken == 0:
            session["username"] = username
            nameText = "Current name: " + username
            socketio.emit('joinLobbyBTN')
            resp = make_response(render_template('index.html', nameText=nameText))
            resp.set_cookie('username', username)
            return resp
        else:
            nameText = "Name is already taken"
            return render_template('index.html', nameText=nameText)
    elif "username" in session:
        nameText = "Current name: " + session["username"]
        socketio.emit('joinLobbyBTN')
        return render_template('index.html', nameText=nameText)
    else:
        nameText = "Please set a name"
        return render_template('index.html', nameText=nameText)


def startGame():
    global players
    cardsEachPlayer = 52/len(playersGame)
    print(cardsEachPlayer)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
