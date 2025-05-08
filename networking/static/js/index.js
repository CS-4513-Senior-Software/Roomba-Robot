let axis_values = [0, 0, 0, 0];
let prev_write_request = [];

let LR_idx = 0;
let FB_idx = 1;
let PAN_idx = 2;
let TILT_idx = 3;

// let activeInput = "none"; // Tracks the active input method i.e., gamepad, joystick, or keyboard

function sendWriteRequest(msg) {
    fetch('/writeRequest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: {
            LR: msg[LR_idx],
            FB: msg[FB_idx],
            TILT: msg[TILT_idx],
            PAN: msg[PAN_idx]
        } })  // Send data as JSON
    })
    .then(response => response.json())
    .then(data => {})
    .catch(error => console.error("Error:", error));
}

// runs every 20 ms
function update() {
    // ensure axis_value LR and FB elements do not go outside the range [-1, 1]
    for (let i = 0; i < axis_values.length; i++) {
        if (axis_values[i] > 1) {
            axis_values[i] = 1;
        }

        if (axis_values[i] < -1) {
            axis_values[i] = -1;
        }
    }

    if (!equals(prev_write_request, axis_values) || axis_values[PAN_idx] != 0 || axis_values[TILT_idx] != 0) {
        console.log("write");
        sendWriteRequest(axis_values);
        prev_write_request = []
        for (let i = 0; i < axis_values.length; i++) { // copy axis_values into prev_write_request
            prev_write_request[i] = axis_values[i];
        }
    }

    setTimeout(update, 20); // loop again
}

// joystick controls

// Initialize joysticks
let joystickLeft = nipplejs.create({
    zone: document.getElementById('joystick-left'),
    mode: 'static',
    position: { left: '25%', bottom: '15%' },
    color: 'blue'
});

let joystickRight = nipplejs.create({
    zone: document.getElementById('joystick-right'),
    mode: 'static',
    position: { right: '25%', bottom: '15%' },
    color: 'red'
});

function handleJoystick(joystick, side) {
    joystick.on('move', function (evt, data) {
        let angle = data.angle.degree;
        let force = data.force;

        if (force < 0.3) return;

        if (side === 'left') {
            if (angle >= 45 && angle < 135) { axis_values[FB_idx] += 1; }
            else if (angle >= 135 && angle < 225) { axis_values[LR_idx] += 1; }
            else if (angle >= 225 && angle < 315) { axis_values[FB_idx] += -1; }
            else { axis_values[LR_idx] += -1 };
        } else if (side === 'right') {
            if (angle >= 45 && angle < 135) { axis_values[PAN_idx] += 1 }
            else if (angle >= 135 && angle < 225) { axis_values[PAN_idx] += -1 }
            else if (angle >= 225 && angle < 315) { axis_values[TILT_idx] += -1 }
            else { axis_values[TILT_idx] += 1 }
        }
    });

    joystickLeft.on('end', function () {
        activeInput = "joystick";
        axis_values = [0, 0, 0, 0];  // Stop movement
    });

    joystickRight.on('end', function () {
        axis_values = [0, 0, 0, 0];  // Stop movement
    });
}

handleJoystick(joystickLeft, "left");
handleJoystick(joystickRight, "right");

// keyboard controls
document.addEventListener("keydown", function(e) {
    if (e.repeat) return;
    
    switch (e.key) {
        case 'w':
            axis_values[FB_idx] += 1;
            break;
        case 'a':
            axis_values[LR_idx] += 1;
            break;
        case 's':
            axis_values[FB_idx] += -1;
            break;
        case 'd':
            axis_values[LR_idx] += -1;
            break;
        case 'ArrowUp':
            axis_values[TILT_idx] += 1;
            break;
        case 'ArrowDown':
            axis_values[TILT_idx] += -1;
            break;
        case 'ArrowLeft':
            axis_values[PAN_idx] += -1;
            break;
        case 'ArrowRight':
            axis_values[PAN_idx] += 1;
            break;
    }
});

document.addEventListener("keyup", function(e) {
    if (e.repeat) return;
    
    switch (e.key) {
        case 'w':
            axis_values[FB_idx] += -1;
            break;
        case 'a':
            axis_values[LR_idx] += -1;
            break;
        case 's':
            axis_values[FB_idx] += 1;
            break;
        case 'd':
            axis_values[LR_idx] += 1;
            break;
        case 'ArrowUp':
            axis_values[TILT_idx] += -1;
            break;
        case 'ArrowDown':
            axis_values[TILT_idx] += 1;
            break;
        case 'ArrowLeft':
            axis_values[PAN_idx] += 1;
            break;
        case 'ArrowRight':
            axis_values[PAN_idx] += -1;
            break;
}
});

function equals(arr1, arr2) {
    if (arr1.length != arr2.length) return false;

    for (let i = 0; i < arr1.length; i++) {
        if (arr1[i] != arr2[i]) return false;
    }

    return true;
}

// Clamping function to ensure values are within a specified range
function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

function round(num, places) {
    let multiplier = 10**places
    return Math.round((num + Number.EPSILON) * multiplier) / multiplier;
}

// Polling for gamepad input
function pollGamepad() {
    const gamepads = navigator.getGamepads();
    if (gamepads[0]) { // Use the first connected gamepad
        const gamepad = gamepads[0];

        // Map gamepad axes to robot controls with clamping and dead zone
        axis_values[LR_idx] = Math.abs(gamepad.axes[0]) > 0.1 ? round(clamp(gamepad.axes[0], -1, 1), 2) * -1 : 0;  // Left/Right (LR)
        axis_values[FB_idx] = Math.abs(gamepad.axes[1]) > 0.1 ? round(clamp(-gamepad.axes[1], -1, 1), 2) : 0; // Forward/Backward (FB) (invert Y-axis)
        axis_values[PAN_idx] = Math.abs(gamepad.axes[2]) > 0.1 ? round(clamp(gamepad.axes[2], -1, 1), 2) : 0; // Pan
        axis_values[TILT_idx] = Math.abs(gamepad.axes[5]) > 0.1 ? round(clamp(-gamepad.axes[5], -1, 1), 2) : 0; // Tilt (invert Y-axis)
    }

    requestAnimationFrame(pollGamepad); // Continue polling
}

function startOptiTrack() {
    fetch('/startOptiTrack', {method: 'POST'})
    .then(response => {response.json(); console.log(response)})
    .then(data => {})
    .catch(error => console.error("Error:", error));
}

window.addEventListener("gamepadconnected", (event) => {
    console.log("Gamepad connected:", event.gamepad);
});

window.addEventListener("gamepaddisconnected", (event) => {
    console.log("Gamepad disconnected:", event.gamepad);
    axis_values = [0, 0, 0, 0]; // Reset axis values
});


pollGamepad(); // Start polling for gamepad input

update(); // start update loop