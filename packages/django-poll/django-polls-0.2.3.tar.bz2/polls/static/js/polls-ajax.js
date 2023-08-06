$(document).ready(function() {
    if(window.location.hash == '#voted') {
        window.location = '/poll/' + 'results/' + $('input[name="pk"]').val();
    }
    
    $('.poll.vote form').on('submit', function() {
        var form = $(this);
        
        $.post(form.attr('action'), form.serialize(), function(data) {
            $('.alerts').html($(data).find('.alerts').html());
            $('.poll').replaceWith($(data).find(form.attr('data-source')));
            window.location.hash = '#voted'
        });
        
        
        return false;
    });
});