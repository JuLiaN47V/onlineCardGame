var cookieArr = document.cookie.split(";");
var myTurn = false;
let username;
    // Loop through the array elements
    for(var i = 0; i < cookieArr.length; i++) {
        var cookiePair = cookieArr[i].split("=");
        if (cookiePair[0] === "username"){
            username = cookiePair[1]
        }
    }

    leftSelectionCard = document.createElement("img");
    leftSelectionCard.style.left = 100 + "px";
    leftSelectionCard.style.top = 65 + "%";
    leftSelectionCard.className = "image";
    leftSelectionCard.id = "leftSelectionCard";
    leftSelectionCard.onclick = detachCard;
    document.body.appendChild(leftSelectionCard);

    rightSelectionCard = document.createElement("img");
    rightSelectionCard.style.left = 220 + "px";
    rightSelectionCard.style.top = 65 + "%";
    rightSelectionCard.className = "image";
    rightSelectionCard.id = "rightSelectionCard";
    rightSelectionCard.onclick = detachCard;
    document.body.appendChild(rightSelectionCard);


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
let second = false;
let leftCard;
let rightCard;


function chooseCard() {

    if (myTurn === true) {
        if (first === false) {
            document.getElementById("leftSelectionCard").src = "static/img/cards/" + this.id + ".png";
            leftCard = this.id;
            this.style.visibility = "hidden";
            first = true;
        } else if (second === false) {
            document.getElementById("rightSelectionCard").src = "static/img/cards/" + this.id + ".png";
            rightCard = this.id;
            this.style.visibility = "hidden";
            second = true
        }
    } else {
        alert("Not your turn!")
    }
}

function detachCard(){
    this.src = null;
    if (this.id === "leftSelectionCard") {
        document.getElementById(leftCard).style.visibility = 'visible';
        first = false;
    } else {
        document.getElementById(rightCard).style.visibility = 'visible';
        second = false;
    }
}


socket.on("yourTurn", function () {
    myTurn = true;
    setTimeout(function(){ alert("Your turn!"); }, 1500);
});