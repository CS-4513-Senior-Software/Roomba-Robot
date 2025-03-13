let axis_values = [0, 0, 0, 0];
let prev_write_request = [];

let LR_idx = 0;
let FB_idx = 1;
let PAN_idx = 2;
let TILT_idx = 3;

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

    // // ensure axis_value TILT and PAN elements do not go outside the range [1, 179]
    // for (let i = 2; i < axis_values.length; i++) {
    //     if (axis_values[i] > 179) {
    //         axis_values[i] = 179;
    //     }

    //     if (axis_values[i] < 1) {
    //         axis_values[i] = 1;
    //     }
    // }

    console.log(axis_values);


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

update(); // start update loop