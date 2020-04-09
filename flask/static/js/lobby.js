player = {"name":""};
player.name = prompt("Please enter your name");

var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('update_player_amount', function (playerAmount) {
    document.getElementById("playerAmountArea").innerText = playerAmount.amountP;
  });
socket.on('connect', function () {
    socket.emit('new_player', player.name)
  });
socket.on('host', function () {
    var btn = document.createElement("BUTTON");
    btn.innerHTML = "Start";
    btn.id = "start";
    btn.onclick = start;
    document.body.appendChild(btn);
  });

function start() {
    socket.emit("start");
}

  socket.on('redirect', function (data) {
    window.location = data.url;
});