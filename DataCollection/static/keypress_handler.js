var leftBtn = document.getElementById('leftBtn');
var rightBtn = document.getElementById('rightBtn');
var pauseBtn = document.getElementById('pauseBtn');
var forwardBtn = document.getElementById('forwardBtn');


document.onkeydown = function (event) {
    switch (event.keyCode) {
        case 37:
            console.log("Left key is pressed.");
            leftBtn.click();
            break;
        case 38:
            console.log("Up key is pressed.");
            forwardBtn.click();
            break;
        case 39:
            console.log("Right key is pressed.");
            rightBtn.click();
            break;
        case 32:
            console.log("Space bar pressed")
            pauseBtn.click();
            break;
    }
};