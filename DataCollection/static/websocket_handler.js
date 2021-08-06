//SETUP
const socket = io();
const livestream = document.getElementById('livestream')
const biasDisplay = document.getElementById("biasDisplay");
var motorBias = 0;

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
    motorBias = 0;
    socket.emit('startRecording');
    console.log('starting the recording');
}
function pauseRecording() {
    socket.emit('pauseRecording');
    console.log('pausing the recording');
}
function motorsOn(){
    socket.emit('motorsOn');
}
function motorsOff(){
    socket.emit('motorsOff');
}
function turnLeft(){
    motorBias = Math.max(-20, motorBias - 2);
    socket.emit('motorBias', motorBias);
    biasDisplay.innerHTML = motorBias;
}
function turnRight(){
    motorBias = Math.min(20, motorBias + 2);
    socket.emit('motorBias', motorBias);
    biasDisplay.innerHTML = motorBias;
}
function forward(){
    motorBias = 0;
    socket.emit('motorBias', motorBias);
    biasDisplay.innerHTML = motorBias;
}