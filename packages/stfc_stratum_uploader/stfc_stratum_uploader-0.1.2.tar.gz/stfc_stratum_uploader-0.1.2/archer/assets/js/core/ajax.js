
$(function () {
    function clicked(url) {
        $.get(url, null, function(data, textStatus, jqXHR) {
            console.log(data);
            console.log(textStatus);
            console.log(jqXHR);
        });
    }
//    $('a.ajax-link').each(function(index) {
//        var that = this;
//        $(this).on('click', function(index) {
//            clicked($(that).attr('href'));
//        });
//        $(this).removeAttr('href');
////        return false;
//    });


    $('a.ajax-link').click(function() {
        console.log($('#actions-content'));
        $('#actions-content').load($(this).attr('href') + ' #content');
        return false;
    });
});
