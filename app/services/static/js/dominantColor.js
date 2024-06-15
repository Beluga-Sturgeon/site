function getDominantColor(imgEl) {
    imgEl.crossOrigin = "Anonymous";

    var blockSize = 5, // only visit every 5 pixels
        defaultRGB = {r:0,g:0,b:0}, // for non-supporting envs
        canvas = document.createElement('canvas'),
        context = canvas.getContext && canvas.getContext('2d'),
        data, width, height,
        i = -4,
        length,
        red = [],
        green = [],
        blue = [],
        rgb = {r:0,g:0,b:0}
        count = 0;

    if (!context) {
        return defaultRGB;
    }

    height = canvas.height = imgEl.naturalHeight || imgEl.offsetHeight || imgEl.height;
    width = canvas.width = imgEl.naturalWidth || imgEl.offsetWidth || imgEl.width;

    context.drawImage(imgEl, 0, 0);

    try {
        data = context.getImageData(0, 0, width, height);
    } catch(e) {
        /* security error, img on diff domain */
        return defaultRGB;
    }

    length = data.data.length;

    while ( (i += blockSize * 4) < length ) {
        if (data.data[i + 3] !== 0) {
        ++count;
            red.push(data.data[i]);
            green.push(data.data[i+1]);
            blue.push(data.data[i+2]);
        }
    }

    // ~~ used to floor values
    rgb.r = mode(red);
    rgb.g = mode(green);
    rgb.b = mode(blue);

    console.log(rgb)

    return rgb;
}

function mode(input) {

    // Object to store the frequency of each element
    let mode = {};

    // Variable to store the frequency of the current mode
    let maxCount = 0;

    // Array to store the modes
    let modes = [];

    // Iterate through each element of the input array
    input.forEach(function (e) {
        if (mode[e] == null) {
            mode[e] = 1;
        } else {
            mode[e]++;
        }
        if (mode[e] > maxCount) {

            // Update the current mode and its frequency
            modes = [e];
            maxCount = mode[e];
        } else if (mode[e] === maxCount) {
            modes.push(e);
        }
    });
    return modes;
}