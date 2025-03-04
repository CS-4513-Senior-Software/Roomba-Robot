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
});

document.addEventListener("keyup", function(e) {
    if(e.repeat) return;
    
    if (e.key == 'w') {
        wPressed = false;
        sendData('stop');
    }
});