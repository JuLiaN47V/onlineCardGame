if (document.getElementById("current_name").innerHTML === "Please set a name" || document.getElementById("current_name").innerHTML === "Name is already taken" || document.getElementById("current_name").innerHTML === "No spaces in name!") {

} else {
  var br = document.createElement("br");
  document.body.appendChild(br)
  var btn = document.createElement("BUTTON");
  btn.innerHTML = "Join Gamelobby";
  btn.onclick = index;
  document.body.appendChild(btn);
}


var socketGame = io.connect('http://' + document.domain + ':' + location.port);
function index() {
  socketGame.emit('redirect')
}
  socketGame.on('redirect', function (data) {
    window.location = data.url;
});
