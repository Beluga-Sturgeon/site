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

    if (i > 0) {
        currentScene.on("enter", function (event) {
            var currentPanel = event.target.triggerElement();
            var previousPanel = currentPanel.previousElementSibling;
            if (previousPanel) {
                previousPanel.classList.add("hide");
            }
        });

        currentScene.on("leave", function (event) {
            var currentPanel = event.target.triggerElement();
            var previousPanel = currentPanel.previousElementSibling;
            if (previousPanel) {
                previousPanel.classList.remove("hide");
            }
        });
    }
}