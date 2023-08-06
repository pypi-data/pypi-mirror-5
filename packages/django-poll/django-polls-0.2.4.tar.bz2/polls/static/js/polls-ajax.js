$(document).ready(function() {
    if(window.location.hash == '#voted') {
        window.location = '/poll/' + 'results/' + $('input[name="pk"]').val();
    }
    
    $('.poll.vote form').on('submit', function() {
        var form = $(this);
        
        $.post(form.attr('action'), form.serialize(), function(data) {
            var source = $(data).find(form.attr('data-source'));
            
            if(source.length > 0) {
                $('.poll').replaceWith(source);
                window.location.hash = '#voted'
            } else {
                if($(':checked').length == 0 && $(':selected').length == 0) {
                    $('.alerts').html(message1);
                } else {
                    $('.alerts').html(message2);
                }
            }
        });
        
        
        return false;
    });
});