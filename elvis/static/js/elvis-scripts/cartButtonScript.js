
function cartButtonRefresh()
{
    var $button = null;
    var cart_timeout = null;
    var $base_modal = $("#base-modal");
    var $base_modal_header = $("#base-modal-header");
    var $base_modal_body = $("#base-modal-body");
    var $base_modal_footer = $("#base-modal-footer");
    var $collection_count = $("#collection-count");


    $(".cart-button").off('click').tooltip().on("click", function (event)
    {
        $button = $(this);
        event.preventDefault();
        event.stopImmediatePropagation();

        if ($(this).hasClass('btn-success'))
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

                    $button.fadeOut(100, function ()
                    {
                        $button.blur()
                            .tooltip('hide')
                            .attr({'data-original-title': 'Remove From Downloads'})
                            .tooltip('fixTitle')
                            .removeClass('btn-success')
                            .addClass('btn-danger')
                            .html("<span class='glyphicon glyphicon-minus'></span>");
                        $($button.siblings()[2]).val('remove');
                    }).fadeIn(100)
                },
                error: function (data)
                {
                    $base_modal_header.html("<h4 class='modal-title'>Error adding file to downloads!</h4>");
                    $base_modal_body.html("<p>Something went wrong and your item was not added to your download cart./p>");
                    $base_modal_footer.html("<button type='button' class='btn btn-default' data-dismiss='base-modal'>Close</button>");
                }
            })
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

                    $button.fadeOut(100, function ()
                    {
                        $button.blur()
                            .tooltip('hide')
                            .attr({'data-original-title': 'Add to Downloads'})
                            .tooltip('fixTitle')
                            .removeClass('btn-danger')
                            .addClass('btn-success')
                            .html("<span class='glyphicon glyphicon-plus'></span>");
                        $($button.siblings()[2]).val('add');
                    }).fadeIn(100)
                },
                error: function (data)
                {
                    $base_modal_header.html("<h4 class='modal-title'>Error adding file to downloads!</h4>");
                    $base_modal_body.html("<p>Something went wrong and your item was not added to your download cart./p>");
                    $base_modal_footer.html("<button type='button' class='btn btn-default' data-dismiss='base-modal'>Close</button>");
                }
            })
        }


    });
}