var type = null;
var action = null;
var $button = null;
var cart_timeout = null;
var items = null;
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
        if ($button.hasClass('cart-badge'))
            type = 'badge';
        else
            type = 'button';
        if ($button.hasClass('btn-success'))
            action = 'add';
        else
            action = 'remove';

        if (action === 'add')
        {
            cart_timeout = setTimeout(function ()
            {
                $base_modal_header.html("<h4 class='modal-title'>Adding to Downloads...</h4>");
                $base_modal_body.html("<p>Adding large collections or composer oeuvres to your downloads can take a little time...</p>");
                $base_modal_footer.html("<div class='progress'>" +
                    "<div class='progress-bar progress-bar-striped active' role='progressbar' style='width: 100%'></div> " +
                    "</div>");
                $base_modal.modal('show');
            }, 1000);
        }
        else
        {
            cart_timeout = setTimeout(function ()
            {
                $base_modal_header.html("<h4 class='modal-title'>Removing from Downloads...</h4>");
                $base_modal_body.html("<p>Removing large collections or composer oeuvres from your downloads can take a little time...</p>");
                $base_modal_footer.html("<div class='progress'>" +
                    "<div class='progress-bar progress-bar-striped active' role='progressbar' style='width: 100%'></div> " +
                    "</div>");
                $base_modal.modal('show');
            }, 1000);
        }
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
                init_cart_buttons()
            },
            error: function (data)
            {
                $base_modal_header.html("<h4 class='modal-title'>Error modifying downloads!</h4>");
                $base_modal_body.html("<p>Something went wrong and your cart was not modified!</p>");
                $base_modal_footer.html("<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>");
            }
        });
    });
}

function init_cart_buttons()
{
    if ($forms === null)
        $forms = $(".recursive-patch-download-form");
    if (items === null)
        items = build_item_dict($forms);
    debugger;

    $.ajax({
        url: "/download-cart/",
        data: {check_in_cart: JSON.stringify(items)},
        success: function (data)
        {
            var keys = Object.keys(data);
            for (var i = 0; i < keys.length; i++)
            {
                var key = keys[i];
                if (items[key]['button_type'] == "button")
                    draw_button(data[key], items[key]["$elem"]);
                else
                    draw_badge(data[key], items[key]["$elem"]);
            }
            cartButtonRefresh()
        }
    });
}

function build_item_dict($forms)
{
    items = {};
    for (var i = 0; i < $forms.size(); i++)
    {
        var form_children = $forms[i].children;
        var item_type = null, item_id = null, button_type = null;
        for (var j in form_children)
        {
            if(item_type !== null && item_id !== null && button_type !== null)
                break;

            var child = form_children[j];
            if (child.name === "item_type")
            {
                item_type = child.value;
                continue;
            }
            if (child.name === "id")
            {
                item_id = child.value;
            }
            if (child.name === "button_type")
            {
                button_type = child.value;
            }
        }
        items[item_id] = {"type": item_type, "button_type": button_type, "$elem": $($forms[i])};
    }
    return items
}

function draw_button(data, element)
{
    var $elem = $(element);
    $elem.children(":button").remove();
    if (data['in_cart'] === true)
    {
        $elem.children("[name=action]").val("remove");
        $elem.prepend('<button type="button" class="btn btn-danger cart-button">Remove from Downloads </button>');
    }
    else if (data['in_cart'] === false)
    {
        $elem.children("[name=action]").val("add");
        $elem.prepend('<button type="button" class="btn btn-success cart-button">Add to Downloads </button>');
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

    $elem.prepend(new_button);
    $elem.children("[name=action]").val(new_action);
}