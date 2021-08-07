//SETUP
const socket = io();
const livestream = document.getElementById('livestream');
const biasDisplay = document.getElementById("biasDisplay");
const leftMotorDisplay = document.getElementById("leftMotorDisplay");
const rightMotorDisplay = document.getElementById("rightMotorDisplay");
var motorBias = 0;
const MOTOR_DEFAULT = 20;


//LISTENERS
socket.on('connect', function(){
    console.log('connected');
    socket.emit('livestreamSystem');
    update_labels();
});
socket.on('disconnect', function(){
    console.log('disconnected');
});
socket.on('jpg_string', function(data){
    livestream.src = 'data:image/jpeg;base64,' + data;
})
socket.on('bias', function(data) {
    motorBias = data;
    update_labels();
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


//FUNCTIONS
function update_labels() {
    biasDisplay.innerHTML = motorBias;
    leftMotorDisplay.innerHTML = MOTOR_DEFAULT + motorBias;
    rightMotorDisplay.innerHTML = MOTOR_DEFAULT - motorBias;
}