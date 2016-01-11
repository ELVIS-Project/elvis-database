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

    $("#piece-submit").click(function()
    {
        $("#new-piece-form").submit();
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
            },
            error: function (data)
            {
                if (data['responseJSON'] == undefined || data['responseJSON']['errors'] === undefined) {
                    $base_modal_header.html("<h4 class='modal-title'>Server Error<h4>");
                    $base_modal_body.html("<p>An error occurred while updating this piece. Please try again, or, if the error persists, " +
                        "<a href='mailto:elvisdatabase@gmail.com?Subject=Upload%20Error'>contact us</a></p>");
                    $base_modal_footer.html("<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>");
                }
                else
                {
                    var errors = createErrorString(data['responseJSON']);
                    $base_modal_header.html("<h4 class='modal-title'>Form Error<h4>");
                    $base_modal_body.html("<p>Your submission has the following errors: <br>" + errors + "</p>");
                    $base_modal_footer.html("<button id='close-and-goto-button' type='button' class='btn btn-default' data-dismiss='modal'>Close</button>");
                    $("#close-and-goto-button").click(function(){
                        $('html, body').animate({
                            scrollTop: $(".validation-error").offset().top - 70
                        }, 500);
                    })
                }
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

    function createErrorString(data)
    {
        var errors = "";
        var form_inputs = $(":input");
        for (var i = 0; i < form_inputs.length; i++)
        {
            var label = form_inputs[i].getAttribute('aria-label');

            if (data['errors'][form_inputs[i].name] && !(label === "Religious Nature" || label === "Voice Type"))
            {
                errors += "<strong>"+ label + "</strong> is required. <br>";
                $("#"+form_inputs[i].id).addClass('validation-error');
            }
            else
            {
                $("#"+form_inputs[i].id).removeClass('validation-error');
            }
        }
        if (data['errors']['religiosity'])
        {
            errors += "<strong>Religious Nature</strong> is required. <br>";
            $("#religiosity").children().addClass('validation-error');
        }
        else
        {
            $("#religiosity").children().removeClass('validation-error');
        }
        if (data['errors']['vocalization'])
        {
            errors += "<strong>Voice Type</strong> is required. <br>";
            $("#vocalization").children().addClass('validation-error');
        }
        else
        {
            $("#vocalization").children().removeClass('validation-error');
        }

        if (data['errors']['__all__'])
        {
            for (var i = 0; i < data['errors']['__all__'].length; i += 2 )
            {
                var id = data['errors']['__all__'][i];
                if (id.indexOf('files') !== -1)
                {
                    var row_number = id.replace( /^\D+/g, '');
                    var file_val = $("[id$=files_"+row_number+"]").val();
                    if (file_val)
                    {
                        var path = file_val.split("\\");
                        var file_name = path[path.length-1];
                        errors += "<strong>File</strong><em> "+file_name+"</em> requires a source.<br>";
                        $("#"+id).css('border-color', '#FF9494').addClass('validation-error');
                    }
                }
            }
        }

        $(".validation-error").on("focus click", function(){
            if (this.parentElement.id === "vocalization")
            {
                $("#vocalization").children().css('border-color', '#ccc').removeClass('validation-error');
            }
            else if(this.parentElement.id === "religiosity")
            {
                $("#religiosity").children().css('border-color', '#ccc').removeClass('validation-error');
            }
            else{
                $(this).css("border-color", '#ccc').removeClass('validation-error');

            }
        });
        debugger;
        return errors;
    }
});
