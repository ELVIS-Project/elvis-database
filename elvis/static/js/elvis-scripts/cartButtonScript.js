var type = null;
var action = null;
var $button = null;
var cart_timeout = null;

function cartButtonRefresh()
{
    var $collection_count = $("#collection-count");

    $(".cart-badge, .cart-button").off('click').tooltip().on("click", function (event)
    {
        event.preventDefault();
        event.stopImmediatePropagation();

        $button = $(this);
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
            data: $(event.target).parents(".recursive-patch-download-form").serialize(),
            success: function (data)
            {
                clearTimeout(cart_timeout);
                $base_modal.modal('hide');
                debugger;
                $collection_count.fadeOut(100, function ()
                {
                    $collection_count.text("(" + data.count + ")");
                });
                $collection_count.fadeIn(100);

                if (action === 'add')
                {
                    $button.fadeOut(100, function ()
                    {
                        $button.blur()
                            .tooltip('hide')
                            .attr({'data-original-title': 'Remove From Downloads'})
                            .tooltip('fixTitle')
                            .removeClass('btn-success')
                            .addClass('btn-danger');
                        $($button.siblings("[name='action']")).val('remove');
                        if (type === 'badge')
                            $button.html("<span class='glyphicon glyphicon-minus'></span>");
                        else
                        {
                            $button.html("Remove from Downloads");
                            location.reload();
                        }
                    }).fadeIn(100)
                }
                else
                {
                    $button.fadeOut(100, function ()
                    {
                        $button.blur()
                            .tooltip('hide')
                            .attr({'data-original-title': 'Add to Downloads'})
                            .tooltip('fixTitle')
                            .removeClass('btn-danger')
                            .addClass('btn-success');
                        $($button.siblings("[name='action']")).val('add');
                        if (type === 'badge')
                            $button.html("<span class='glyphicon glyphicon-plus'></span>");
                        else
                        {
                            $button.html("Add to Downloads");
                            location.reload();
                        }

                    }).fadeIn(100)
                }
            },
            error: function (data)
            {
                $base_modal_header.html("<h4 class='modal-title'>Error modifying downloads!</h4>");
                $base_modal_body.html("<p>Something went wrong and your cart was not modified!</p>");
                $base_modal_footer.html("<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>");
            }
        })
    });
}
function init_cart_buttons()
{

    var $forms = $(".recursive-patch-download-form");
    var items = [];
    for (var i = 0; i < $forms.size(); i++)
    {
        var form_children = $forms[i].children;
        var item_type = null, item_id = null;
        for (var j in form_children)
        {
            if(item_type !== null && item_id !== null)
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
        }
        items.push({"type": item_type, "id": item_id, "num": i});
    }
    $.ajax({
        url: "/download-cart/",
        data: {check_in_cart: JSON.stringify(items)},
        async: false,
        success: function (data)
        {
            console.log(data);
            for (var i = 0; i < $forms.size(); i++)
            {
                if (data[i]['in_cart'] === "Piece")
                {
                    $($forms[i]).prepend('<button type="button" class="btn btn-mini btn-info disabled" data-container="body" data-toggle="tooltip" data-placement="top" title="Movement in Downloads under parent Piece. Remove Piece to modify."><span class="glyphicon glyphicon-lock"> </span> </button>');
                    continue;
                }
                if (data[i]['in_cart'] === true)
                {
                    $($forms[i].children[2]).val("remove");
                    $($forms[i]).prepend('<button type="button" class="btn btn-mini btn-danger cart-badge" data-container="body" data-toggle="tooltip" data-placement="top" title="Remove from Downloads"><span class="glyphicon glyphicon-minus"> </span> </button>');
                    continue
                }
                if (data[i]['in_cart'] === false)
                {
                    $($forms[i]).prepend('<button type="button" class="btn btn-mini btn-success cart-badge" data-container="body" data-toggle="tooltip" data-placement="top" title="Add to Downloads"><span class="glyphicon glyphicon-plus"> </span> </button> ');
                }
            }
        }
    });
    cartButtonRefresh()
}
