var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('disconnect', function () {
    socket = io.connect('http://' + document.domain + ':' + location.port);
  });

socket.on('update_player_amount', function (playerAmount) {
    document.getElementById("playerAmountArea").innerText = playerAmount.amountP;
  });
socket.on('connect', function () {
    socket.emit('new_player')
  });
socket.on('host', function () {
    element = document.getElementById("start");
    if(typeof(element) != 'undefined' && element != null){

    } else {
        var btn = document.createElement("BUTTON");
        btn.innerHTML = "Start Game";
        btn.id = "start";
        btn.onclick = start;
        document.body.appendChild(btn);
    }

  });

function start() {
    socket.emit("start");
}

  socket.on('redirect', function (data) {
    window.location = data.url;
});

