// Append a download for the item to the DOM.
function create_download_badge(item_type, item_id, DOM_id)
{
    var $DOM = $("#" + DOM_id);
    $DOM.append("<form class='recursive-patch-download-form' action='/downloads/' method='post'>" +
        "<button type='button' class='btn btn-mini btn-success' data-container='body' data-toggle='tooltip' data-placement='top' title='Add to collection.' ><span class='glyphicon glyphicon-plus'> </span> </button>" +
        "<input type='hidden' name='item_type'  value='" + item_type + "'/>" +
        "<input type='hidden' name='item_id'  value='"+ item_id + "'/>" +
        "</form>");

    $('.btn.btn-mini.btn-success').on('click', function(event)
    {
        event.preventDefault();
        event.stopImmediatePropagation();
        $.ajax(
            {
                type: 'post',
                url: '/downloads/',
                data: $(event.target).parents('.recursive-patch-download-form').serialize(),
                success: function (data) {
                    var $collection_count = $('#collection-count');
                    $collection_count.fadeOut(100, function () {
                        $collection_count.text('(' + data.count + ')');
                    });
                    $collection_count.fadeIn(100);
                }
            })
    })
}