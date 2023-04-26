var socket = io();
socket.on('connect', function () {
    socket.send('hi');
});
