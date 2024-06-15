function swapStyleSheet(dominantColor, index, server) {
    console.log(server)
    const xhttp = new XMLHttpRequest();
    if (index == 0) {
        document.getElementById("pageStyle").setAttribute('href', "/static/styles/data/light.css");
        document.body.setAttribute('style', "background:linear-gradient(157deg, #ffffff 0%, rgb" + dominantColor + " 180%);");
        xhttp.open("GET", server + "/set-light", true);

    } else if (index == 1) {
        document.getElementById("pageStyle").setAttribute('href', '/static/styles/data/dark.css');
        document.body.setAttribute('style', "background:linear-gradient(157deg, #001e30 0%, rgb" + dominantColor + " 180%);");
        xhttp.open("GET", server + "/set-blue", true);

    } else {
        document.getElementById("pageStyle").setAttribute('href', '/static/styles/data/dark.css');
        document.body.setAttribute('style', "background:linear-gradient(157deg, #000000 0%, rgb" + dominantColor + " 180%);");
        xhttp.open("GET", server + "/set-dark", true);
    }
    xhttp.send();
}