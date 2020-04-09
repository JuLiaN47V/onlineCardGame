function createCircleOfDivs(list, radius, offsetX, offsetY, className) {
   var x, y;
   for (var n = 0; n < list.length; n++) {
     x = radius * Math.cos(n / num * 2 * Math.PI);
     y = radius * Math.sin(n / num * 2 * Math.PI);
     var div = document.createElement("textarea");
     div.className = className;
     div.style.left = (x + offsetX) + "px";
     div.style.top = (y + offsetY) + "px";
     document.body.appendChild(div);
   }
}