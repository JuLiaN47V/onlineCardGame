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
    leftSelectionCard.src = "static/img/cards/none.png";
    document.body.appendChild(leftSelectionCard);

    leftMiddleSelectionCard = document.createElement("img");
    leftMiddleSelectionCard.style.left = 210 + "px";
    leftMiddleSelectionCard.style.top = 65 + "%";
    leftMiddleSelectionCard.className = "image";
    leftMiddleSelectionCard.id = "leftMiddleSelectionCard";
    leftMiddleSelectionCard.onclick = detachCard;
    leftMiddleSelectionCard.src = "static/img/cards/none.png";
    document.body.appendChild(leftMiddleSelectionCard);

    rightMiddleSelectionCard = document.createElement("img");
    rightMiddleSelectionCard.style.left = 320 + "px";
    rightMiddleSelectionCard.style.top = 65 + "%";
    rightMiddleSelectionCard.className = "image";
    rightMiddleSelectionCard.id = "rightMiddleSelectionCard";
    rightMiddleSelectionCard.onclick = detachCard;
    rightMiddleSelectionCard.src = "static/img/cards/none.png";
    document.body.appendChild(rightMiddleSelectionCard);

    rightSelectionCard = document.createElement("img");
    rightSelectionCard.style.left = 430 + "px";
    rightSelectionCard.style.top = 65 + "%";
    rightSelectionCard.className = "image";
    rightSelectionCard.id = "rightSelectionCard";
    rightSelectionCard.onclick = detachCard;
    rightSelectionCard.src = "static/img/cards/none.png";
    document.body.appendChild(rightSelectionCard);
    function pass(){
        socket.emit("pass")
    }
    let passBtn = document.createElement("button");
    passBtn.onclick = pass;
    passBtn.id = "passBtn";
    passBtn.className = "passBtn";
    passBtn.innerHTML = "pass";
    document.body.appendChild(passBtn);

var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function () {
    socket.emit('hello_game', username)
  });

socket.on("ownCards", function (cards) {
    document.cookie = "state=ingame";
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
let third = false;
let fourth = false;
let leftCard = "none";
let leftMiddleCard = "none";
let rightMiddleCard = "none";
let rightCard = "none";
let element;


function chooseCard() {

    if (myTurn === true) {
        if (first === false) {
            document.getElementById("leftSelectionCard").src = "static/img/cards/" + this.id + ".png";
            leftCard = this.id;
            this.style.visibility = "hidden";
            first = true;
        } else if (second === false) {
            document.getElementById("leftMiddleSelectionCard").src = "static/img/cards/" + this.id + ".png";
            leftMiddleCard = this.id;
            this.style.visibility = "hidden";
            second = true
        } else if (third === false) {
            document.getElementById("rightMiddleSelectionCard").src = "static/img/cards/" + this.id + ".png";
            rightMiddleCard = this.id;
            this.style.visibility = "hidden";
            third = true
        } else if (fourth === false) {
            document.getElementById("rightSelectionCard").src = "static/img/cards/" + this.id + ".png";
            rightCard = this.id;
            this.style.visibility = "hidden";
            fourth = true
        }
        if (first || second || third || fourth) {
            let subBtn = document.createElement("button");
            subBtn.onclick = submitCards;
            subBtn.id = "subBtn";
            subBtn.className = "subButton";
            subBtn.innerHTML = "Submit cards";
            document.body.appendChild(subBtn);
        }

    } else {
        alert("Not your turn!")
    }
}

function detachCard(){
    this.src = "static/img/cards/none.png";
    if (this.id === "leftSelectionCard") {
        document.getElementById(leftCard).style.visibility = 'visible';
        first = false;
    } else if (this.id === "leftMiddleSelectionCard") {
        document.getElementById(leftMiddleCard).style.visibility = 'visible';
        second = false;
    } else if (this.id === "rightMiddleSelectionCard") {
        document.getElementById(rightMiddleCard).style.visibility = 'visible';
        third = false;
    } else if (this.id === "rightSelectionCard") {
        document.getElementById(rightCard).style.visibility = 'visible';
        fourth = false;
    }
    document.body.removeChild(document.getElementById("subBtn"));
}

function submitCards(){
    socket.emit("chooseCard", leftCard, leftMiddleCard, rightMiddleCard, rightCard);
    first = false;
    second = false;
    third = false;
    fourth = false;
}


socket.on("yourTurn", function () {
    myTurn = true;
    first = false;
    second = false;
    third = false;
    fourth = false;
    setTimeout(function () {alert("Your turn!");}, 500);
});

socket.on("update_middle", function (cards) {
    document.getElementById("middleCardLeft").src = "static/img/cards/" + cards.card1 + ".png";
    document.getElementById("leftSelectionCard").src = "static/img/cards/none.png";
    first = false
    document.getElementById("middleCardMiddleLeft").src = "static/img/cards/" + cards.card2 + ".png";
    document.getElementById("leftMiddleSelectionCard").src = "static/img/cards/none.png";
    second = false;
    document.getElementById("middleCardMiddleRight").src = "static/img/cards/" + cards.card3 + ".png";
    document.getElementById("rightMiddleSelectionCard").src = "static/img/cards/none.png";
    third = false;
    document.getElementById("middleCardRight").src = "static/img/cards/" + cards.card4 + ".png";
    document.getElementById("rightSelectionCard").src = "static/img/cards/none.png";
    fourth = false;
    document.body.removeChild(document.getElementById("subBtn"));
    leftCard = "none";
    leftMiddleCard = "none";
    rightMiddleCard = "none";
    rightCard = "none";
});

socket.on("badCards", function () {
    element = document.getElementById(leftCard);
    if(typeof(element) != 'undefined' && element != null){
        first = false;
        document.getElementById(leftCard).style.visibility = "visible";
        document.getElementById("leftSelectionCard").src = "static/img/cards/none.png";
    }
    element = document.getElementById(leftMiddleCard);
    if(typeof(element) != 'undefined' && element != null){
        second = false;
        document.getElementById(leftMiddleCard).style.visibility = "visible";
        document.getElementById("leftMiddleSelectionCard").src = "static/img/cards/none.png";
    }
    element = document.getElementById(rightMiddleCard);
    if(typeof(element) != 'undefined' && element != null){
        third = false;
        document.getElementById(rightMiddleCard).style.visibility = "visible";
        document.getElementById("rightMiddleSelectionCard").src = "static/img/cards/none.png";
    }
    element = document.getElementById(rightCard);
    if(typeof(element) != 'undefined' && element != null){
        fourth = false;
        document.getElementById(rightCard).style.visibility = "visible";
        document.getElementById("rightSelectionCard").src = "static/img/cards/none.png";
    }
    leftCard = "none";
    leftMiddleCard = "none";
    rightMiddleCard = "none";
    rightCard = "none";
    alert("Not working")
});

socket.on("update_playerCards", function (values) {
    document.getElementById("player" + values.index).lastElementChild.innerHTML = "cards left: " + values.value;
});

socket.on("winner", function () {
    alert("WINNER")
});