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
        runtTest()
    });

    function runtTest() {
      fetch(document.URL.split("/").slice(0, 3).join("/") + '/runTests/' + document.URL.split("/").pop())
          .then(function(response) {
              if (!response.ok) {
                  throw new Error('Network response was not ok');
              }
              return response.text();
          })
          .then(function(text) {
              //Check every ten seconds
              if (text === "Not Ready") {
                  setTimeout(function() {
                      runtTest();
                  }, 10000);
              } else {
                  window.location.href = text;
              }
          })
          .catch(function(error) {
              console.error(error);
          });
  }
  
});
