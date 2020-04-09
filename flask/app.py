from flask import Flask
from flask import render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

players = []
playersSave = []


class Player:
    sid = None
    name = None
    position = None

    def __init__(self, name, sid, pos):
        self.sid = sid
        self.name = name
        self.position = pos


@socketio.on('redirect')
def redirect():
    emit('redirect', {'url': url_for('lobby')})


@socketio.on('new_player')
def new_player(name):
    global players
    me = Player(name, request.sid, len(players))
    players.append(me)
    if len(players) == 1:
        emit('host', room=players[0].sid)

    for player in players:
        print(player.name)
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


@app.route('/lobby')
def lobby():
    global players
    return render_template('lobby.html', playerAmount=len(players))


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
