function handle_js_mediasearch_listing() {

    $.post('js_mediasearch_listing',
        $('#search-form').serialize(),
        function(data){
            $('#mediasearch-results').html(data);

            $( ".unlock" ).click(function(event) {
                uid=$(event.target).attr('data-uid');

                dict_={}
                dict_['uid']=uid;

                $.post('@@mediasearch/unlock',
                    dict_,
                        function(data){ }
                );
            });

            $('.link-overlay').prepOverlay({
                subtype: 'ajax',
            });

            $('.image-overlay').prepOverlay({
                subtype: 'image',
            });

            $('.delete-overlay').prepOverlay({
                subtype: 'ajax',
                filter : '#content'
            });

            $('.rename-overlay').prepOverlay({
                subtype: 'ajax',
                filter : '#content'
            });

        }
    ).error(function() {});
}

$( document ).ready(function() {

    handle_js_mediasearch_listing();

    $("body").delegate( "#search", "click", function(event) {
        $('#b_start').attr('value','0');
        handle_js_mediasearch_listing();
    });

    $("body").delegate( ".click-paste-reload", "click", function(event) {
        event.preventDefault();
        href_=$(event.target).attr('href');
        $.post(href_,
            '',
                function(data){
                    $('.pb-ajax').html(data);
                }
        );

    });

    $(document).keypress(function(event) {
        if(event.which == 13) {
            event.preventDefault();
            handle_js_mediasearch_listing();
            return false;
        }

    });

});