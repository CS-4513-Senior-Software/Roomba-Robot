let wPressed = false;

function sendData(msg) {
    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })  // Send data as JSON
    })
    .then(response => response.json())
    .then(data => {})
    .catch(error => console.error("Error:", error));
}


document.addEventListener("keydown", function(e) {
    if(e.repeat) return;
    
    if (e.key == 'w') {
        wPressed = true;
        sendData('w');
    }

    if (e.key == 's') {
        sendData('s');
    }

    if (e.key == 'a') {
        sendData('a');
    }

    if (e.key == 'd') {
        sendData('d');
    }

    if (e.key == 'ArrowUp') {
        sendData('ArrowUp');
    }

    if (e.key == 'ArrowDown') {
        sendData('ArrowDown');
    }

});

document.addEventListener("keyup", function(e) {
    if(e.repeat) return;
    
    if (e.key == 'w' || e.key == 's' || e.key == 'a' || e.key == 'd') {
        wPressed = false;
        sendData('stop');
    }
});