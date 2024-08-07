function changeColor() {
    let priceChange = document.getElementsByClassName("change");
    if (priceChange)
    {
        for (key in priceChange)
        {
            firstLetter = String(priceChange[key].innerText.substr(0,1))
            if (firstLetter == "-")
            {
                priceChange[key].classList.add("negative");
                priceChange[key].classList.remove("positive");
            }
            else
            {
                priceChange[key].classList.add("positive");
                priceChange[key].classList.remove("negative");
            }
        }
    }
};

function changeTableStyle()
{
    console.log("CALLED TABLE STYLE CHANGE")
    let inputs = document.querySelectorAll("input.anychart-label-input")
    inputs.forEach(input => {
        $(input).css({
            "background-color":"#1e1f1c",
            "color":"white",
            "font-family":"Open Sans",
            "border":"none"
        })
    })

    let buttons = document.querySelectorAll("button.anychart-button anychart-inline-block anychart-button-standard anychart-button-toggle anychart-button-collapse-right")
    buttons.forEach(button => {
        $(button).css({
            "background-color":"#1e1f1c",
            "color":"white",
            "font-family":"Open Sans",
            "border":"none"
        })
    })
    let credits = document.querySelectorAll("div.anychart-credits")
    $(credits[0]).css("display","none")
}

$( "div.card" ).hover(
    function(){
        $(this).children().css("color", "white")
    },
    function(){
        $(this).children().css("color", "#707070")
    },
);


function actioncolor() {
    const actionSpans = document.querySelectorAll(".action");
    
    actionSpans.forEach(function(span) {
        const content = span.textContent.trim();
        
        if (content === "LONG") {
            span.style.color = "#00ff00";
        } else if (content === "HOLD") {
            span.style.color = "#d7df00";
        } else if (content === "SHORT") {
            span.style.color = "#790000";
        }
    });
}
actioncolor()

function fixCss(){
    if (window.innerWidth / window.innerHeight < 3/2){
        const rect = document.getElementById('actionbox').getBoundingClientRect();
        const footer = document.querySelector('footer');
        const themeToggle = document.getElementById('theme_toggle');
    
        footer.style.marginTop = `calc(${rect.bottom}px - 50vh)`;
        themeToggle.style.top = `${rect.bottom}px`;
    } else {
        const rect = document.getElementById('window');
        themeToggle.style.top = `${rect.bottom}px`;
        footer.style.marginTop = `calc(${rect.bottom}px - 50vh)`;
    }
}

window.addEventListener("resize", (e) => {
    fixCss()
});

$(document).ready(() => {
    fixCss()
})