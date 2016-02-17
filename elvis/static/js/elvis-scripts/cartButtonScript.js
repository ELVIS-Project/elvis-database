var type = null;
var action = null;
var $button = null;
var cart_timeout = null;
var items = null;
var light_items = {};
var $forms = null;

function cartButtonRefresh()
{
    var $collection_count = $("#collection-count");

    $(".cart-badge, .cart-button").off('click').tooltip().on("click", function (event)
    {
        event.preventDefault();
        event.stopImmediatePropagation();

        $button = $(this);
        $button.tooltip('hide');

        if ($button.hasClass('disabled'))
        {
            $button.blur();
            return false
        }

        $button.addClass("disabled");
        if ($button.hasClass('cart-badge'))
            type = 'badge';
        else
            type = 'button';

        if ($button.hasClass('btn-success'))
            action = 'add';
        else
            action = 'remove';
        $.ajax({
            type: "post",
            url: "/download-cart/",
            data: $button.parents(".recursive-patch-download-form").serialize(),
            success: function (data)
            {
                clearTimeout(cart_timeout);
                $base_modal.modal('hide');
                $collection_count.fadeOut(100, function ()
                {
                    $collection_count.text("(" + data.count + ")");
                });
                $collection_count.fadeIn(100);
                init_cart_buttons();
            },
            error: function (data)
            {
                $base_modal_header.html("<h4 class='modal-title'>Error modifying downloads!</h4>");
                $base_modal_body.html("<p>Something went wrong and your cart was not modified!</p>");
                $base_modal_footer.html("<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>");
                $base_modal.modal('show');
            }
        });
    });
}

function redirect_to_login()
{
    $(".cart-badge, .cart-button").off('click').tooltip().on("click", function (event)
    {
        window.location = "/login/?error=download";
    });
}

function init_cart_buttons(force_redraw)
{
    if(typeof force_redraw === "undefined")
    {
        force_redraw = false
    }
    if ($forms === null || force_redraw)
        $forms = $(".recursive-patch-download-form");
    if (items === null || force_redraw)
        items = build_item_dict($forms);

    $.ajax({
        url: "/download-cart/",
        type: "POST",
        data: {check_in_cart: JSON.stringify(light_items)},
        success: function (data)
        {
            if (data !== null || force_redraw)
            {
                var keys = Object.keys(data);
                for (var i = 0; i < keys.length; i++)
                {
                    var key = keys[i];
                    var back = data[key]['in_cart'];
                    if (back === items[key]['in_cart'] && !force_redraw)
                        continue;

                    items[key]['in_cart'] = back;
                    light_items[key]['in_cart'] = back;
                    if (items[key]['button_type'] == "button")
                        draw_button(data[key], items[key]["$elem"]);
                    else
                        draw_badge(data[key], items[key]["$elem"]);
                }
            }
            cartButtonRefresh()
        },
        error: function (data)
        {
            redirect_to_login();
        }
    });
}

function build_item_dict($forms)
{
    items = {};
    for (var i = 0; i < $forms.size(); i++)
    {
        var fields = $forms[i].children;
        items[fields[2].value] = {
            "button_type": fields[0].value,
            "item_type": fields[1].value,
            "$elem": $($forms[i]),
            "in_cart": str_to_bool(fields[3].value)
        };
        light_items[fields[2].value] = {
            "item_type": fields[1].value,
            "in_cart": str_to_bool(fields[3].value)
        };
    }
    return items
}

function str_to_bool(str)
{
    if (str.toLowerCase() === "true")
    {
        return true
    }
    else if (str.toLowerCase() === "init")
    {
        return "init"
    }
    return false
}

function draw_button(data, element)
{
    var $elem = $(element);
    $elem.children(":button").remove();
    if (data['in_cart'] === true)
    {
        $elem.children("[name=action]").val("remove");
        $elem.append('<button type="button" class="btn btn-danger cart-button">Remove from Downloads </button>');
    }
    else if (data['in_cart'] === false)
    {
        $elem.children("[name=action]").val("add");
        $elem.append('<button type="button" class="btn btn-success cart-button">Add to Downloads </button>');
    }
}

function draw_badge(data, element)
{
    var $elem = $(element);
    $elem.children(":button").remove();
    var new_button = "", new_action = "";

    if (data['in_cart'] === "Piece")
    {
        new_button = '<button type="button" class="btn btn-mini btn-info disabled cart-badge" data-container="body" data-toggle="tooltip" data-placement="top" title="In cart under piece."><span class="glyphicon glyphicon-lock"> </span> </button>'
        new_action = "add"
    }
    else if (data['in_cart'] === true)
    {
        new_button =  '<button type="button" class="btn btn-mini btn-danger cart-badge" data-container="body" data-toggle="tooltip" data-placement="top" title="Remove from Downloads"><span class="glyphicon glyphicon-minus"> </span> </button>';
        new_action = "remove"
    }
    else if (data['in_cart'] === false)
    {
        new_button = '<button type="button" class="btn btn-mini btn-success cart-badge" data-container="body" data-toggle="tooltip" data-placement="top" title="Add to Downloads"><span class="glyphicon glyphicon-plus"> </span> </button> ';
        new_action = "add"
    }

    $elem.append(new_button);
    $elem.children("[name=action]").val(new_action);
    $elem.children("[name=in_cart]").val(data['in_cart']);
}

function create_download_form(item_type, id, DOM_id)
{
    var $DOM = $("#" + DOM_id);
    $DOM.append(
        '<form class="recursive-patch-download-form" action="/download-cart/" method="post"> \
            <input type="hidden" name="button_type" value="badge"> \
            <input type="hidden" name="item_type"  value="' + item_type + '"/> \
            <input type="hidden" name="id"  value="' + id + '"/> \
            <input type="hidden" name="in_cart" value="false" /> \
            <input type="hidden" name="action" value="add" /> \
            <button type="button" class="btn btn-mini btn-success cart-badge" data-container="body" data-toggle="tooltip" data-placement="top" title="" data-original-title="Add to Downloads"><span class="glyphicon glyphicon-plus"> </span> </button> \
        </form>'
    );
}