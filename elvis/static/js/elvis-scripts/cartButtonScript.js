var type = null;
var action = null;
var $button = null;
var cart_timeout = null;
var $base_modal = $("#base-modal");
var $base_modal_header = $("#base-modal-header");
var $base_modal_body = $("#base-modal-body");
var $base_modal_footer = $("#base-modal-footer");
var $collection_count = $("#collection-count");

function cartButtonRefresh()
{
    $base_modal = $("#base-modal");
    $base_modal_header = $("#base-modal-header");
    $base_modal_body = $("#base-modal-body");
    $base_modal_footer = $("#base-modal-footer");
    $collection_count = $("#collection-count");

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
            url: "/downloads/",
            data: $(event.target).parents(".recursive-patch-download-form").serialize(),
            success: function (data)
            {
                clearTimeout(cart_timeout);
                $base_modal.modal('hide');
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