$(document).ready(function ($)
{
    var oldPiece = {};
    var changes = {};
    changes['modify'] = [];
    changes['delete'] = [];
    changes['add'] = [];

    //Loading plugins for the various form fields
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
    });

    var file_table = $("#piece_file_table");
    file_table.dynamicTable({
        button: $("#new_piece_file"),
        table_name: "files"
    });

    fillUpdateForm();

    // Get a json representation of the piece, and fill the form with its values, create input listeners.
    function fillUpdateForm()
    {
        $.ajax({
            datatype: "json",
            url: window.location.href  + "?format=json",
            success: function (data)
            {
                oldPiece = data;
                drawWelcomeModal();
                fillPieceForm();
                fillDynamicTables();
                createListeners();
            }
        });
    }

    //Create a list of database changes (deleting and moving objects) and write to screen.
    $("#piece-submit").click(function()
    {
        findChanges();
        if (changes['delete'].length > 0 || changes['add'].length > 0 ||changes['modify'].length > 0 )
        {
            var body_string = "";
            var deletion_string = "";
            var addition_string = "";
            var modify_string = "";
            if (changes['delete'].length > 0)
            {
                deletion_string = "<h4>Delete</h4><ul>";
                for (var i = 0; i < changes['delete'].length; i++)
                {
                    var item = changes['delete'][i];
                    if (item['type'] === 'A')
                    {
                        deletion_string += "<li>Delete file <em>" + item['name'] + "</em> attached to <strong>" + item['parent'] + "</strong>.</li>"
                    }
                    else
                    {
                        deletion_string += "<li>Delete movement <strong>" + item['name'] + "</strong>.</li>"
                    }
                }
                deletion_string += "</ul>";
                body_string += deletion_string;
            }
            if (changes['add'].length > 0)
            {
                addition_string = "<h4>Add</h4><ul>";
                for (var i = 0; i < changes['add'].length; i++)
                {
                    var item = changes['add'][i];
                    if (item['type'] === 'A')
                    {
                        addition_string += "<li>Add file <em>" + item['name'] + "</em> attached to <strong>" + item['parent'] + "</strong>.</li>"
                    }
                    else
                    {
                        addition_string += "<li>Add movement <strong>" + item['name'] + "</strong> to <strong>"+oldPiece['title']+"</strong></li>"
                    }
                }
                addition_string += "</ul>";
                body_string += addition_string;
            }
            if (changes['modify'].length > 0)
            {
                var isObjectFound = false;
                modify_string = "<h4>Moving</h4><ul>";
                for (var i = 0; i < changes['modify'].length; i++)
                {
                    var item = changes['modify'][i];
                    if (item['type'] === 'A' && item['oldParent'] !== item['newParentTitle'])
                    {
                        isObjectFound = true;
                        modify_string += "<li>Moving file <em>" + item['name'] + "</em> from <strong>" + item['oldParent'] + "</strong> to <strong>" + item['newParentTitle'] + "</strong>.</li>"
                    }
                }
                modify_string += "</ul>";
                if (isObjectFound)
                {
                    body_string += modify_string;
                }
            }
            if (body_string !== "")
            {
                $base_modal_header.html("<h4 class='modal-title'>Confirm Database Changes</h4>");
                $base_modal_body.html(body_string);
                $base_modal_footer.html('.modal-footer').html("<div class='row'><div class='col-xs-2'><button type='button' class='btn btn-warning' id='restart-button'>Restart</button></div>" +
                    "<div class='col-xs-10'><button type='button' class='btn btn-default btn' data-dismiss='modal'>Change something</button>" +
                    "<button class='btn btn-success' id='confirm-changes'>Looks good!</a></div></div>");
                $base_modal.modal('show');
                $("#restart-button").click(function ()
                {
                    location.reload();
                });
                $("#confirm-changes").click(function ()
                {
                    $("#new-piece-form").submit();
                })
            }
            else
            {
                $("#new-piece-form").submit();
            }
        }
        else
        {
            $("#new-piece-form").submit();
        }

    });

    // Logic for form validation and submission, as well as the modal which appears on submission.,
    $("#new-piece-form").submit(function (event)
    {
        event.preventDefault();
        $base_modal_header.html("<h4 class='modal-title'>Modifying Piece...</h4>");
        $base_modal_body.html("<div class='progress'>" +
            "<div class='progress-bar progress-bar-striped active' role='progressbar' style='width: 100%'></div> " +
            "</div>");
        $base_modal_footer.html("");
        $base_modal.modal('show');

        var formData = new FormData(this);
        formData.append('changes', JSON.stringify(changes));

        $.ajax({
            type: "patch",
            url: "/piece/" + oldPiece['id'] +"/",
            data: formData,
            processData: false,
            contentType: false,
            success: function (data)
            {
                $base_modal_header.html("<h4 class='modal-title'>Done!</h4>");
                $base_modal_body.html("<p>Piece succesfuly updated!</p>");
                $base_modal_footer.html('.modal-footer').html( "<a href='"+ window.location.href + "' class='btn btn-default' id='success-refresh'>Refresh Page</a>" +
                    "<a href='" + data['url'] + "' class='btn btn-default' id='goto-piece'>Go to Piece</a>");
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

    //Listeners to open popovers on the labels of inputs when the input is focused.
    function createListeners()
    {
        $('[data-toggle="popover"]').popover();
        var $upload_fields = $(".upload-input-field");
        $upload_fields.focus(function (event)
        {
            $(event.target.parentElement.children[0]).popover('show');
        });
        $upload_fields.focusout(function (event)
        {
            $(event.target.parentElement.children[0]).popover('hide');
        });
        $("#collections").prop('disabled', true);
        $("#collections-input-group")
            .mouseenter(function (event)
            {
                $(event.target.parentElement.children[0]).popover('show');
            })
            .mouseleave(function (event){
                $(event.target.parentElement.children[0]).popover('hide');
            });

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

        //If an input is changed, set a listener to warn user when leaving the page.
        $(":input").on('input', function()
        {
            $(window).on('beforeunload', function (event)
            {
                if (event['target']['activeElement']['id'] === 'goto-piece'
                    || event['target']['activeElement']['id'] === 'success-refresh')
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
    }



    //$("#upload-page-content").html("<p class='lead text-center'>Sorry, uploads are temporarily disabled while the database is updated.</p>")


    // Fill the text and number form inputs.
    function fillPieceForm()
    {
        $("#title").val(oldPiece['title']);
        oldPiece['composer'] = oldPiece['composer'].title;
        $("#composer").val(oldPiece['composer']);
        $("#comment").val(oldPiece['comment']);
        $("#composition_start_date").val(oldPiece['composition_start_date']);
        $("#composition_end_date").val(oldPiece['composition_end_date']);
        $("#number_of_voices").val(oldPiece['number_of_voices']);
        oldPiece['languages'] = writeList(oldPiece['languages']);
        oldPiece['collections'] = writeList(oldPiece['collections'], true);
        oldPiece['genres'] = writeList(oldPiece['genres']);
        oldPiece['locations'] = writeList(oldPiece['locations']);
        oldPiece['instruments_voices'] = writeList(oldPiece['instruments_voices']);
        oldPiece['sources'] = writeList(oldPiece['sources']);
        oldPiece['tags'] = writeList(oldPiece['tags']);
        $("#collections").val(oldPiece['collections']);
        $("#languages").val(oldPiece['languages']);
        $("#genres").val(oldPiece['genres']);
        $("#locations").val(oldPiece['locations']);
        $("#instruments_voices").val(oldPiece['instruments_voices']);
        $("#sources").val(oldPiece['sources']);
        $("#tags").val(oldPiece['tags']);

        var $religButtons = $("#religiosity");
        for (var i = 0; i < 3; i++)
        {

            if ($religButtons.children()[i].children[0].value === oldPiece['religiosity'])
            {
                $religButtons.children()[i].className += " active ";
                $($religButtons.children()[i].children[0]).prop("checked", "true");
                break;
            }
        }
        var $vocalButtons = $("#vocalization");
        for (var i = 0; i < 3; i++)
        {
            if ($vocalButtons.children()[i].children[0].value === oldPiece['vocalization'])
            {
                $vocalButtons.children()[i].className += " active ";
                $($vocalButtons.children()[i].children[0]).prop("checked", "true");
                break;
            }
        }
    }

    // Populate and fill the dynamicTables.
    function fillDynamicTables()
    {
        var file_table = $("#piece_file_table");
        var mov_table = $("#movement_table");
        var fc = 1;

        for (var i = 0; i < oldPiece['attachments'].length; i++)
        {
            file_table.dynamicTable('addRow', true);
            var $file = file_table.find("#files_existing_files_" + (fc));
            var $source = file_table.find("#_existingfiles_source_" + (fc));
            var row = file_table.find("#_existingfiles" + (fc));
            row.attr('name', oldPiece['attachments'][i]['id']);
            row.css('background-color', '#E8E8E8');
            $file.attr("href", oldPiece['attachments'][i]['attachment']).text(oldPiece['attachments'][i]['title']);
            $source.val(oldPiece['attachments'][i]['source']);
            oldPiece['attachments'][i]['parent'] = "piece";

            fc++;
        }

        for (var i = 0; i < oldPiece['movements'].length; i++)
        {
            mov_table.dynamicTable('addRow', true);
            var row = mov_table.find("#_existingmov" + (i + 1));
            row.attr('name',oldPiece['movements'][i]['id'] );
            row.css('background-color', '#E8E8E8');
            var $title = mov_table.find("#_existingmov_title_" + (i + 1));
            var $instruments = mov_table.find("#_existingmov" + (i + 1) + "_instrumentation");
            var $tags = mov_table.find("#_existingmov" + (i + 1) + "_free_tags");
            var $num_voices = mov_table.find("#_existingmov" + (i + 1) + "_number_of_voices");
            var $comment = mov_table.find("#_existingmov" + (i + 1) + "_comment");
            var $vocalization = mov_table.find("#_existingmov" + (i + 1) + "_vocalization");
            for (var j = 0; j < 3; j++)
            {
                if ($vocalization.children()[j].children[0].value === oldPiece['movements'][i]['vocalization'])
                {
                    $vocalization.children()[j].className += " active ";
                    $($vocalization.children()[j].children[0]).prop("checked", "true");
                    break;
                }
            }
            oldPiece['movements'][i]['instruments_voices'] = writeList(oldPiece['movements'][i]['instruments_voices']);
            oldPiece['movements'][i]['tags'] = writeList(oldPiece['movements'][i]['tags']);
            oldPiece['movements'][i]['position'] = i + 1;
            $title.val(oldPiece['movements'][i].title);
            $instruments.val(oldPiece['movements'][i].instruments_voices);
            $tags.val(oldPiece['movements'][i].tags);
            $num_voices.val(oldPiece['movements'][i].number_of_voices);
            $comment.val(oldPiece['movements'][i].comment);
            for (var j = 0; j < oldPiece['movements'][i]['attachments'].length; j++)
            {
                file_table.dynamicTable('addRow', true);
                var row = file_table.find("#_existingfiles" + (fc));
                row.css('background-color', '#E8E8E8');
                var $file = file_table.find("#files_existing_files_" + (fc));
                var $attach = file_table.find("#_existingfiles_parent_" + (fc));
                var $source = file_table.find("#_existingfiles_source_" + (fc));
                var row = file_table.find("#_existingfiles" + (fc));
                row.attr('name', oldPiece['movements'][i]['attachments'][j]['id']);
                $file.attr("href", oldPiece['movements'][i]['attachments'][j]['attachment']).text(oldPiece['movements'][i]['attachments'][j]['title']);
                $source.val(oldPiece['movements'][i]['attachments'][j]['source']);
                $attach.selectpicker('val', "_existingmov_title_" + (i + 1));
                oldPiece['movements'][i]['attachments'][j]['parent'] = "_existingmov_title_" + (i + 1);
                fc++;
            }
            file_table.dynamicTable('drawAttachSelects');
        }

        //Listener for deleting existing movements or files. Adds the information to the
        //changes dict when one is deleted.
        $("[id^=del_mov], [id^=del_files]").click(function (event)
        {
            var row = $(event['target']).parents("[id^=_existing]")[0];
            var type,
                id,
                name,
                parent;
            if (row.id.indexOf('mov') !== -1)
                type = "M";
            else
                type = "A";
            if (type == "A")
            {
                parent = row.children[2].children[1].children[0].title;
                name = row.children[1].children[0].text;
                id = row.getAttribute('name');
                changes['delete'].push({type: type, id: id, name: name, parent: parent});
            }
            else
            {
                name = row.children[2].children[0].value;
                id = row.getAttribute('name');
                changes['delete'].push({type: type, id: id, name: name});
            }
        });
    }

    //Draws a modal with instructions for uploading, but only once per session.
    function drawWelcomeModal()
    {
        if (sessionStorage.getItem('saw_instructions') !== 'true')
        {
            $base_modal_header.html("<h4 class='modal-title'>Modifying an existing piece...<h4>");
            $base_modal_body.html("<p>This form has been pre-filled with the current state of <em>"+oldPiece['title']+"</em>.<ul><li>You may modify any of its properties.</li>" +
                "<li>Do not modify any fields that you do not wish to change.</li> <li>Existing movements and files are colored dark grey - you may modify or delete these as well.</li>" +
                "<li>You may also add new movements and files.</li></ul>" +
                "<strong>No changes are applied until you click the submit button </strong> at the bottom of the page. If you make a mistake, or need to restart the process, simply reload the page. </p>");
            $base_modal_footer.html("<button type='button' class='btn btn-success' data-dismiss='modal'>Got it</button>");
            $base_modal.modal('show');
            sessionStorage.setItem("saw_instructions", 'true');
        }
    }

    //Utility function. Turns a json list objects into a semicolon separated string.
    function writeList(jlist, collection)
    {
        var result = "";
        if (collection)
        {
            for (var i = 0; i < jlist.length; i++)
            {
                if (jlist[i].public)
                {
                    result += jlist[i].title + "; "
                }
            }
        }
        else
        {
            for (var i = 0; i < jlist.length; i++)
            {
                result += jlist[i].title + "; "
            }
        }
        return result
    }

    //Scan the form and dynamic tables, comparing the current values to the values stored in
    //oldPiece. Record differences in the changes dict.
    function findChanges()
    {
        changes['modify'] = [];
        changes['add'] = [];

        // Compare text and number fields to their previous values, save
        // changes in the changes dict.
        var $inputs = $(".upload-input-field");
        for (var i = 0; i < $inputs.length; i++)
        {
            var id = $inputs[i].getAttribute('id');
            var $selector = $("#" + id);
            var new_val = $selector.val();
            if (new_val != oldPiece[id])
            {
                if (new_val === "" && oldPiece[id] === null)
                    continue;
                //A text field from the top of the form doesnt match the previous value.
                changes['modify'].push({
                    type: 'F',
                    id: id,
                    value: new_val
                });
            }
        }
        var $religButtons = $("#religiosity");
        for (var i = 0; i < 3; i++)
        {
            if ($religButtons.children()[i].className.indexOf("active") !== -1)
            {
                if ($religButtons.children()[i].children[0].value == oldPiece['religiosity'])
                {
                    break
                }
                else
                {
                    changes['modify'].push({
                        type: 'F', id: 'religiosity',
                        value: $religButtons.children()[i].children[0].value
                    })
                }
            }
        }
        var $vocalButtons = $("#vocalization");
        for (var i = 0; i < 3; i++)
        {
            if ($vocalButtons.children()[i].className.indexOf("active") !== -1)
            {
                if ($vocalButtons.children()[i].children[0].value == oldPiece['vocalization'])
                {
                    break
                }
                else
                {
                    changes['modify'].push({
                        type: 'F', id: 'vocalization',
                        value: $vocalButtons.children()[i].children[0].value
                    })
                }
            }
        }

        // Find changed movements, record their changes.
        var $existing_movements = mov_table.children('[id^=_existingmov]');
        for (var i = 0; i < $existing_movements.length; i += 2)
        {
            // Get info from form
            var modifications = {};
            var oldMov = null;
            var fields = [];
            var $titleRow = $($existing_movements[i]);
            var $advancedRow = $($existing_movements[i + 1]);
            var id = parseInt($titleRow[0].getAttribute('name'));
            fields.push(['title', $titleRow.find("[id^=_existingmov_title_]")[0].value]);
            fields.push(['position', $titleRow.find("[id$=_position]")[0].value]);
            fields.push(['instruments_voices', $advancedRow.find("[id$=_instrumentation]")[0].value]);
            fields.push(['tags', $advancedRow.find("[id$=_free_tags]")[0].value]);
            fields.push(['number_of_voices', $advancedRow.find("[id$=_number_of_voices]")[0].value]);
            fields.push(['comment', $advancedRow.find("[id$=_comment]")[0].value]);
            var selected_vocal = $($advancedRow.find("[id$=_vocalization]")[0]).children(".active")[0];
            if (selected_vocal)
                fields.push(['vocalization', selected_vocal.children[0].value]);

            // Find the old movement in the oldPiece.
            for (var j = 0; j < oldPiece['movements'].length; j++)
            {
                if (oldPiece['movements'][j]['id'] === id)
                {
                    oldMov = oldPiece['movements'][j];
                    break
                }
            }


            //Compare the old to the new, and record differences in a modifications dict.
            var key = 0;
            var value = 1;
            for (var j = 0; j < fields.length; j++)
            {
                if (oldMov[fields[j][key]] != fields[j][value])
                {
                    if (fields[j][key] === "comment" && fields[j][value] === "" && oldMov[fields[j][key]] === null)
                        continue;
                    modifications[fields[j][key]] = fields[j][value]
                }
            }
            if (!$.isEmptyObject(modifications))
            {
                //if the movement has been modified, push the modifications to changes dict.
                modifications['id'] = id;
                modifications['type'] = "M";
                modifications['oldTitle'] = oldMov['title'];
                changes['modify'].push(modifications)
            }
        }

        // Find and log new movements.
        var $new_movements = mov_table.children('[id^=mov]');
        for (var i = 0; i < $new_movements.length; i += 2)
        {
            var $titleRow = $($new_movements[i]);
            var title = $titleRow.find("[id^=mov_title_]")[0].value;
            var position = $titleRow.find("[id$=_position]")[0].value;
            if (title === "")
                continue;

            changes['add'].push({type:"M", name: title, position: position})
        }

        //Find changed attachments - record changes
        var $existing_attachments = file_table.children('[id^=_existingfiles]');
        for (var i = 0; i < $existing_attachments.length; i++)
        {
            var modifications = {};
            var oldAtt = null;
            var fields = [];
            var row = $($existing_attachments[i]);
            var id = parseInt(row.attr('name'));
            fields.push(['parent', row.find("[id^=_existingfiles_parent_]")[0].value]);
            fields.push(['source', row.find("[id^=_existingfiles_source_]")[0].value]);

            //Find old attachment. First search piece attachments
            for (var j = 0; j < oldPiece['attachments'].length; j++)
            {
                if (oldPiece['attachments'][j]['id'] === id)
                {
                    oldAtt = oldPiece['attachments'][j];
                    var oldParent = 'Attach to Piece';
                    break;
                }
            }
            //If not found, search movement attachments.
            if (oldAtt === null)
            {
                for (var j = 0; j < oldPiece['movements'].length; j++)
                {
                    for (var k = 0; k < oldPiece['movements'][j]['attachments'].length; k++)
                    {
                        if (oldPiece['movements'][j]['attachments'][k]['id'] === id)
                        {
                            oldAtt = oldPiece['movements'][j]['attachments'][k];
                            var oldParent = oldPiece['movements'][j]['title'];
                            break;
                        }
                    }
                    if (oldAtt !== null)
                    {
                        break
                    }
                }
            }
            //Compare the old to the new
            for (var j = 0; j < fields.length; j++)
            {
                if (oldAtt[fields[j][key]] !== fields[j][value])
                {
                    if (fields[j][key] === "source" && fields[j][value] === "" && oldAtt[fields[j][key]] === null)
                        continue;
                    modifications[fields[j][key]] = fields[j][value]
                }
            }

            //If differences exist, push them to changes.
            if (!$.isEmptyObject(modifications))
            {
                modifications['id'] = id;
                modifications['type'] = "A";
                modifications['name'] = row.children()[1].children[0].text;
                modifications['oldParent'] = oldParent;
                modifications['oldSource'] = oldAtt['source'];
                modifications['newParentTitle'] = row.children()[2].children[1].children[0].title;
                if (modifications['parent'] !== "piece")
                {
                    modifications['newParent'] = row.children()[2].children[0].value;
                }
                changes['modify'].push(modifications)
            }
        }
        // Find and log new attachments.
        var $new_attachments = file_table.children('[id^=files]');
        for (var i = 0; i < $new_attachments.length; i ++)
        {
            var row = $($new_attachments[i]);
            var title = row.children()[1].children[1].children[1].value;
            if (title === "")
                continue;

            var parent = row.children()[2].children[1].children[0].title;
            if (parent === "Attach to Piece")
                parent = "the piece";

            changes['add'].push({type:"A", name: title, parent: parent})
        }
    }
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
                    var file_val = null;
                    var row_number = id.replace(/^\D+/g, '');
                    id.indexOf('existing') === -1 ? file_val = $("[id$=files_" + row_number + "]").val() : file_val = $("[id$=files_" + row_number + "]").text();
                    if (file_val)
                    {
                        var path = file_val.split("\\");
                        var file_name = path[path.length - 1];
                        errors += "<strong>File</strong><em> " + file_name + "</em> requires a source.<br>";
                        $("#" + id).css('border-color', 'red').addClass('validation-error');
                    }
                }
                if (id.indexOf('mov') !== -1)
                {
                    errors += "<strong>Movements</strong> requires a title!<br>";
                    $("#" + id).css('border-color', 'red').addClass('validation-error');
                }
            }
        }

        $(".validation-error").on("focus", function(){
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

        return errors
    }
});