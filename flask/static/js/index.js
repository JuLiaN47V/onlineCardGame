lobbyIsSelected = false;
if (document.getElementById("current_name").innerHTML === "Please set a name" || document.getElementById("current_name").innerHTML === "Name is already taken" || document.getElementById("current_name").innerHTML === "No spaces in name!" && lobbyIsSelected === true) {

} else {
  var br = document.createElement("br");
  document.body.appendChild(br)
  var btn = document.createElement("BUTTON");
  btn.innerHTML = "Join Gamelobby";
  btn.onclick = index;
  document.body.appendChild(btn);
  let createLobbyBtn = document.createElement("BUTTON");
  createLobbyBtn.innerHTML = "create Lobby";
  createLobbyBtn.onclick = createLobby;
  document.body.appendChild(createLobbyBtn);
}


var socketGame = io.connect('http://' + document.domain + ':' + location.port);
function index() {
  socketGame.emit('redirect')
}
  socketGame.on('redirect', function (data) {
    window.location = data.url;
});

socketGame.on("addLobby", function (lobby) {
  let lobbyDiv = document.createElement("div");
  lobbyDiv.onclick=joinLobby;
  lobbyDiv.id = "lobby" + lobby.lobbyID;
  document.body.appendChild(lobbyDiv);
  let lobbyName = document.createElement("p");
  lobbyName.innerHTML = lobby.lobbyName;
  lobbyDiv.appendChild(lobbyName);
});

function createLobby(){
  socketGame.emit("createLobby");
}

function joinLobby() {
  socketGame.emit("joinLobby", this.id.split("y")[1]);
  window.location = "lobby"
}

socketGame.on("setLobby", function (lobby) {
  document.cookie = "lobby=" + lobby.lobby;
});