$(document).ready(function ($)
{
    autocomplete("title", "title_suggestion_menu", "pieceSuggest");
    autocomplete("composer", "composer_suggestion_menu", "composerSuggest");
    autocomplete("collections", "collection_suggestion_menu", "collectionSuggest", 'list');
    autocomplete("languages", "language_suggestion_menu", "languageSuggest", 'list');
    autocomplete("genres", "genre_suggestion_menu", "genreSuggest", 'list');
    autocomplete("locations", "location_suggestion_menu", "locationSuggest", 'list');
    autocomplete("sources", "source_suggestion_menu", "sourceSuggest", 'list');
    autocomplete("instruments_voices", "instrumentation_suggestion_menu", "instrumentSuggest", 'list');
    autocomplete("tags", "tags_suggestion_menu", "tagSuggest", 'list');

    var mov_table = $("#movement_table");
    mov_table.dynamicTable({
        button: $("#new_mov"),
        table_name: "mov",
        movement: true
    }).dynamicTable('addRow');

    var file_table = $("#piece_file_table");
    file_table.dynamicTable({
        button: $("#new_piece_file"),
        table_name: "files"
    }).dynamicTable('addRow');

    $('[data-toggle="popover"]').popover();

    // The dropdown form for additional composer information.
    var $newComposerMenu = $("#composer-create-new-menu");
    var $composerInput = $("#composer");
    $newComposerMenu.hide();

    $composerInput.on("focusout", function (event)
    {
        var query = $("#composer").val();

        if (query.length > 0)
        {
            $.ajax({
                url: "/composers/",
                data: {q: query},
                success: function (data)
                {
                    if (data['count'] == 0)
                    {
                        $newComposerMenu.children().remove(".top-message");
                        $newComposerMenu.prepend("<div class='top-message'><span class='help-block'>" +
                            "<hr>We don't have <strong>" + query + "</strong> in our database. " +
                            "Submitting a piece by an unknown composer will add the composer to the database. <br>" +
                            "Do you have additional information to add to this new composer?<br><br></span></div>");
                        $newComposerMenu.slideDown("slow");
                    }
                }
            });
        }
    });

    $composerInput.on("keydown", function (event)
    {
        if (event['keyCode'] !== 13)
        {
            $newComposerMenu.slideUp("slow");
        }
    });

    $(":input").on('input', function()
    {
        $(window).on('beforeunload', function (event)
        {
            if (event['target']['activeElement']['id'] === 'goto-piece')
            {
                $(window).off('beforeunload');
            }
            else
            {
                return 'Leaving this page will clear your form.'
            }
        });
        $(":input").off('input')
    });


    //Disable default behaviour for hitting 'enter' for all inputs except the comment.
    $('input:not(#comment)').on("keydown", function (event)
    {
        if (event.keyCode === 13)
        {
            event.preventDefault()
        }
    });


    // Logic for form validation and submission, as well as the modal which appears on submission.
    $("#new-piece-form").submit(function (event)
    {
        event.preventDefault();
        $base_modal_header.html("<h4 class='modal-title'>Creating Piece...</h4>");
        $base_modal_body.html("<div class='progress'>" +
            "<div class='progress-bar progress-bar-striped active' role='progressbar' style='width: 100%'></div> " +
            "</div>");
        $base_modal.modal('show');

        $.ajax({
            type: "post",
            url: "/pieces/",
            data: new FormData(this),
            processData: false,
            contentType: false,
            success: function (data)
            {
                if (data['errors'] === undefined)
                {
                    $base_modal_header.html("<h4 class='modal-title'>Done!</h4>");
                    $base_modal_body.html("<p>Piece succesfuly uploaded!</p>");
                    $base_modal_footer.html('.modal-footer').html( " <button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>" +
                        "<a href='" + data['url'] + "' class='btn btn-default' id='goto-piece'>Go to Piece</a>");
                }
                else
                {
                    var errors = "";
                    for (var key in data['errors'])
                    {
                        if (key === "religiosity")
                        {
                            $("input[name='religiosity']").parent().removeClass("btn-default").addClass("btn-danger")
                        }
                        if (key === "vocalization")
                        {
                            $("input[name='vocalization']").parent().removeClass("btn-default").addClass("btn-danger")
                        }

                        else
                        {
                            $("#" + key).parent().addClass("has-error");
                        }

                        $("#" + key + "_error").html("<b style='color:red'>" + data['errors'][key][0] + "</b>");
                        errors = errors + "<strong>" + (key.charAt(0).toUpperCase() + key.slice(1)).replace(/_/g, ' ') + "</strong>: " + data['errors'][key][0] + "<br>"
                    }
                    $base_modal_header.html("<h4 class='modal-title'>Form Error<h4>");
                    $base_modal_body.html("<p>Your submission has the following errors: <br>" + errors + "</p>");
                    $base_modal_footer.html("<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>");
                }


                $('#close_modal').click(function ()
                {
                    $upload_modal.modal('hide');
                });
            },
            error: function(data)
            {
                $base_modal_header.html("<h4 class='modal-title'>Server Error<h4>");
                $base_modal_body.html("<p>An error occurred while uploading your file. Please try again, or, if the error persists, " +
                    "<a href='mailto:elvisdatabase@gmail.com?Subject=Upload%20Error'>contact us</a></p>");
                $base_modal_footer.html("<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>");
            }
        })
    });

    var $upload_fields = $(".upload-input-field");
    $upload_fields.focus(function (event)
    {
        $(event.target.parentElement.children[0]).popover('toggle');
    });
    $upload_fields.focusout(function (event)
    {
        $(event.target.parentElement.children[0]).popover('hide');
    });

    //Limit date inputs to 4 characters.
    $("input[type=number]").keypress(function (event)
    {
        if (event.which !== 0 && event.which !== 8)
        {
            if (this.value.length > 3 || (event.which < 48 || event.which > 57))
            {
                return false
            }
        }
    });

    //$("#upload-page-content").html("<p class='lead text-center'>Sorry, uploads are temporarily disabled while the database is updated.</p>")
})