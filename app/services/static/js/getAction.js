$(document).ready(() => {
    //Keep dimensions of div constant regardless of contents
    var $action = $('#generate_action');
    var minWidth = $action.outerWidth();
    var minHeight = $action.outerHeight();
    $action.css({
        'min-width': minWidth + 'px',
        'min-height': minHeight + 'px'
    });

    $('#generate_action').on('click', (e) => {

        e.preventDefault();
        $("#c").addClass('hidden')
        $('.loading').removeClass('hidden')
    });

    fetch(document.URL.split("/").slice(0, 3).join("/") + '/runModel/' + document.URL.split("/").pop())
        .then(function (response) {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(function (url) {
            // Add function that redirects to /data/<Ticker> once data is ready
            window.location.href = url
          });
});

// Call to server

