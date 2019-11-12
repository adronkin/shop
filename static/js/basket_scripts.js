window.onload = function () {
    console.log('DOM LOADED');
    $(".basket-list").on('change',
        'input[type="number"]',
        function (event) {
            $.ajax({
                url: "/basket/update/" + event.target.name + "/" + event.target.value + "/",
                success: function (data) {
                    // console.log(data);
                    $('.basket-list').html(data.result);
                }
            });
        });
};