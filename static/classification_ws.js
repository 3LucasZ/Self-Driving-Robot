//SETUP
const socket = io();
const livestream = document.getElementById('livestream');
const directionDisplay = document.getElementById("directionDisplay");


//LISTENERS
socket.on('connect', function(){
    console.log('connected');
    socket.emit('recordingSystem');
});
socket.on('disconnect', function(){
    console.log('disconnected');
});
socket.on('jpg_string', function(data){
    livestream.src = 'data:image/jpeg;base64,' + data;
})

//SENDERS
function startRecording() {
    console.log('starting the recording');
    socket.emit('startRecording');
}
function pauseRecording() {
    console.log('pausing the recording');
    socket.emit('pauseRecording');
}
function turnLeft(){
    direction = 0;
    directionUpdate(direction);
}
function forward(){
    direction = 1;
    directionUpdate(direction);
}
function turnRight(){
    direction = 2;
    directionUpdate(direction);
}
function noLine(){
    direction = 3;
    directionUpdate(direction);
}
function directionUpdate(direction) {
    socket.emit('direction', direction);
    directionDisplay.innerText = direction
}