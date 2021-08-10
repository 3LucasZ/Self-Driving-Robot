//SETUP
const socket = io();
const livestream = document.getElementById('livestream');
const biasDisplay = document.getElementById("biasDisplay");
const leftMotorDisplay = document.getElementById('leftMotorDisplay');
const rightMotorDisplay = document.getElementById('rightMotorDisplay'); 
const MOTOR_DEFAULT = 20;
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
    console.log('starting the recording');
    socket.emit('startRecording');
    motorBias = 0;
    update_labels();
}
function pauseRecording() {
    console.log('pausing the recording');
    socket.emit('pauseRecording');
    motorBias = 0;
    update_labels();
}
function motorsOn(){
    console.log('turning on the motors')
    socket.emit('motorsOn');
}
function motorsOff(){
    console.log('turning off the motors')
    socket.emit('motorsOff');
}
//the smaller the motor bias, left turn
//the larger the motor bias, right turn
function turnLeft(){
    console.log("Bias - 2");
    motorBias = Math.max(-20, motorBias - 2);
    socket.emit('motorBias', motorBias);
    update_labels();
}
function turnRight(){
    console.log("Bias + 2");
    motorBias = Math.min(20, motorBias + 2);
    socket.emit('motorBias', motorBias);
    update_labels();
}
function forward(){
    console.log("Bias going back to 0");
    motorBias = 0;
    socket.emit('motorBias', motorBias);
    update_labels();
}
function update_labels() {
    biasDisplay.innerHTML = motorBias;
    leftMotorDisplay.innerHTML = MOTOR_DEFAULT + motorBias;
    rightMotorDisplay.innerHTML = MOTOR_DEFAULT - motorBias;
}