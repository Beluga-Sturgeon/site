const controller = new ScrollMagic.Controller();

var slides = document.querySelectorAll("section.panel");

// create scene for every slide
for (var i=0; i<slides.length; i++) {
    var currentScene = new ScrollMagic.Scene({
        triggerElement: slides[i],
        offset:(window.innerHeight)*0.3
    })
    .setPin(slides[i], {pushFollowers: false})
    .addTo(controller);

    currentScene.on("enter", function (event) {
        var currentPanel = event.target.triggerElement().parentElement;
        var previousPanel = currentPanel.previousElementSibling;
        if (previousPanel && !previousPanel.classList.contains('header')) {
            previousPanel.style.opacity = 0;
        }
    });

    currentScene.on("leave", function (event) {
        var currentPanel = event.target.triggerElement().parentElement;
        var previousPanel = currentPanel.previousElementSibling;
        if (previousPanel) {
            previousPanel.style.opacity = 1;
        }
    });
}