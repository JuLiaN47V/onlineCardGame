var socketGame = io.connect('http://' + document.domain + ':' + location.port);
function index() {
  socketGame.emit('redirect')
}
  socketGame.on('redirect', function (data) {
    window.location = data.url;
});