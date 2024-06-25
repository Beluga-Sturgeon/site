$(document).ready(() => {
    $('#generate_action').on('click', (e) => {

        e.preventDefault();
        $("#c").addClass('hidden')
        $('#loader').removeClass('hidden')
    });
});

// Call to server

