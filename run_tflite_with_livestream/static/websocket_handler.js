//SETUP
const socket = io();
const livestream = document.getElementById('livestream');


var biasDisplay = document.getElementById("biasDisplay");
var leftMotorDisplay = document.getElementById("leftMotorDisplay");
var rightMotorDisplay = document.getElementById("rightMotorDisplay");


//LISTENERS
socket.on('connect', function(){
    console.log('connected');
    socket.emit('livestreamSystem');
});


socket.on('disconnect', function(){
    console.log('disconnected');
});


socket.on('jpg_string', function(data){
    livestream.src = 'data:image/jpeg;base64,' + data;
})


socket.on('bias', function(data) {
    biasDisplay.innerHTML = data;
    leftMotorDisplay.innerHTML = 50 + data;
    rightMotorDisplay.innerHTML = 50 - data;
})


//SENDERS
function startInference() {
    console.log('starting the recording')
    socket.emit('startInference')
}


function stopInference() {
    console.log('pausing the recording')
    socket.emit('stopInference')
}