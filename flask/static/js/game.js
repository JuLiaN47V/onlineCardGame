var cookieArr = document.cookie.split(";");
var myTurn = false;
let username
    // Loop through the array elements
    for(var i = 0; i < cookieArr.length; i++) {
        var cookiePair = cookieArr[i].split("=");
        if (cookiePair[0] === "username"){
            username = cookiePair[1]
        }
    }

var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function () {
    socket.emit('hello_game', username)
  });

socket.on("ownCards", function (cards) {
    let cardX = 100;
    let topV = 90;

    for(var i = 0; i < cards.length; i++) {
        let img = document.createElement("img");
        img.src = "static/img/cards/" + cards[i] + ".png";
        img.style.top = topV + "%";
        cardX = cardX + 120;
        if (cardX >= window.innerWidth - 100){
            cardX = 100;
            topV = topV + 10;
        }
        img.id = cards[i];
        img.style.left = cardX.toString() + "px";
        img.className = "image";
        img.onclick = chooseCard;
        document.body.appendChild(img)
    }
});

let first = false;
let firstCard;
let secondCard;

function chooseCard() {

    if (myTurn === true) {
        if (first === false) {
            firstCard = this.id;
        } else {
            secondCard = this.id;
            first = false;
        }






    } else {
        alert("Not your turn!")
    }
}


socket.on("yourTurn", function () {
    myTurn = true;
    setTimeout(function(){ alert("Your turn!"); }, 1500);
});