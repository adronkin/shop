$( document ).on( 'click', '.details a', function(event) {
    if (event.target.hasAttribute('href')) {
        let link = event.target.href + 'ajax/';
        let link_array = link.split('/');
        if (link_array[3] == 'category') {
            $.ajax({
                url: link,
                success: function (data) {
                    $('.details').html(data.result);
                },
            });

            event.preventDefault();
        }
    }
});
