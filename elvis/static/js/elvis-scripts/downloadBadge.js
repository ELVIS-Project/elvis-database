// Append a download for the item to the DOM.
function create_download_badge(item_type, item_id, DOM_id)
{
    var $DOM = $("#" + DOM_id);
    $DOM.append("<form class='recursive-patch-download-form' action='/download-cart/' method='post'>" +
        "<a class='button btn btn-mini btn-success cart-badge' data-container='body' data-toggle='tooltip' data-placement='top' title='Add to Downloads' ><span class='glyphicon glyphicon-plus'></span></a>" +
        "<input type='hidden' name='item_type'  value='" + item_type + "'/>" +
        "<input type='hidden' name='item_id'  value='" + item_id + "'/>" +
        "<input type='hidden' name='action' value='add' />" +

        "</form>");
}

function create_download_form(item_type, item_id, DOM_id)
{
    var $DOM = $("#" + DOM_id);
    $DOM.append("<form class='recursive-patch-download-form' action='/download-cart/' method='post'>" +
        "<input type='hidden' name='item_type'  value='" + item_type + "'/>" +
        "<input type='hidden' name='item_id'  value='" + item_id + "'/>" +
        "<input type='hidden' name='action' value='add' />" +

        "</form>");
}

