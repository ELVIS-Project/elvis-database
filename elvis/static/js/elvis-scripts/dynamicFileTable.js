
(function ($)
{
    $.fn.dynamicTable = function(options)
    {
        if (typeof options === 'object' || ! options)
        {
            return this.each(function()
            {
                var element = $(this);

                //  Return nothing if element is already a dynamic table.
                if (element.data('dynamicTable'))
                    return;

                // Construct dynamic table
                var dt = new dynamicTable(this, options);
                // Store table in element data
                element.data('dynamicTable', dt);
            })
        }
        else if (methods[options])
        {
            return methods[options].apply( this, Array.prototype.slice.call( arguments, 1 ));
        }
        else
        {
            $.error(options + " is not a valid dynamicTable option");
        }
    };

    var methods = {
        addRow : function(exists) {$(this).data('dynamicTable').addRow(exists);},
        drawAttachSelects : function(){$(this).data('dynamicTable').drawAttachSelects()}
    };

    var dynamicTable = function(element, options)
    {
        var elem = $(element);
        var obj = this;
        var settings = $.extend({
            file_button_name: "Click to select",
            row_count: 1,
            t_size: 0,
            table_name: null,
            movement: false,
            button: null,
            $table: elem
        }, options);

        settings.button.on("click", function ()
        {
            settings.button.blur();
            addRow();
        });

        function addRow(exists)
        {
            if (exists)
            {
                var e = "_existing"
            }
            else
            {
                var e = ""
            }
            if (settings.movement)
            {
                settings.t_size = ((settings.$table.children().length + 1) / 2);
                settings.$table.append("<tr id='" + e + settings.table_name + settings.row_count + "'>" +
                    "<td class='text-center'><button id='del_" + settings.table_name + settings.row_count + "' type='button' tabindex='-1' class='btn btn-default'><span class='glyphicon glyphicon-remove'></span></button></td>" +
                    "<td class='text-center' style='padding-top:14px'>" + settings.t_size + "</td>" +
                    "<td><input name='" +  e + settings.table_name + "_title_" + settings.row_count + "' id='" +  e + settings.table_name + "_title_" + settings.row_count + "' class='form-control' autocomplete='off'" +
                    "data-toggle='popover' data-placement='top' data-trigger='focus' data-html='true' title='<b>Movement Title</b>'" +
                    "data-content='If no title is provided, this movement will be ignored on upload. It is not necessary to number movements, as they will retain the ordering in which they are here presented.'> </td>" +
                    "<td><button id='show_advanced_" + settings.table_name + settings.row_count + "' type='button' tabindex='-1'class='btn btn-default'>Show Advanced</button></td></tr>" +
                    "<tr id='" + e + settings.table_name + settings.row_count + "_tags' hidden='hidden'> " +
                    "<td colspan='4'>" +
                    "<div class='row' style='padding-left:12%; padding-right:15px'>" +
                    "<div class='col-md-7'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Instrumentation</span><input name='" +  e + settings.table_name + settings.row_count + "_instrumentation' id='" +  e + settings.table_name + settings.row_count + "_instrumentation' type='text' class='form-control unstyled'></div>" +
                    "<div id='" +  e + settings.table_name + settings.row_count + "_instrumentation_suggestions' style='padding-left:120px'></div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='col-md-5'>" +
                    "<div class='btn-group btn-group-justified form-inline radio' style='margin-top: 0px' id='" +  e + settings.table_name + settings.row_count + "_vocalization' data-toggle='buttons'>" +
                    "<label class='btn btn-default'>" +
                    "<input type='radio' name='" +  e + settings.table_name + settings.row_count + "_vocalization' value='Vocal'>Vocal" +
                    "</label>" +
                    "<label class='btn btn-default'>" +
                    "<input type='radio' name='" +  e + settings.table_name + settings.row_count + "_vocalization' value='Instrumental'>Instrumental" +
                    "</label>" +
                    "<label class='btn btn-default'>" +
                    "<input type='radio' name='" +  e + settings.table_name + settings.row_count + "_vocalization' value='Mixed'>Mixed" +
                    "</label>" +
                    "</div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='row' style='padding-left:12%; padding-right:15px'>" +
                    "<div class='col-md-8'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Tags</span><input name='" +  e + settings.table_name + settings.row_count + "_free_tags' id='" +  e + settings.table_name + settings.row_count + "_free_tags' type='text' class='form-control unstyled'></div>" +
                    "<div id='" +  e + settings.table_name + settings.row_count + "_free_tags_suggestions' style='padding-left:120px'></div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='col-md-4'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Number of Voices</span><input name='" +  e + settings.table_name + settings.row_count + "_number_of_voices' id='" +  e + settings.table_name + settings.row_count + "_number_of_voices' type='number' class='form-control unstyled'></div>" +
                    "</div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='row' style='padding-left:12%; padding-right:15px'>" +
                    "<div class='col-md-12'>" +
                    "<div class='form-group'><textarea rows='7' class='form-control' name='" +  e + settings.table_name + settings.row_count + "_comment' id='" +  e + settings.table_name + settings.row_count + "_comment' placeholder='Comments...' style='resize:vertical'></textarea>" +
                    "</div>" +
                    "</div>" +
                    "</td></tr>");
                autocomplete(e + settings.table_name + settings.row_count + "_free_tags", e + settings.table_name + settings.row_count + "_free_tags_suggestions", "tagSuggest", true);
                autocomplete(e + settings.table_name + settings.row_count + "_instrumentation", e + settings.table_name + settings.row_count + "_instrumentation_suggestions", "instrumentSuggest", true);
                $("#" + e + settings.table_name + settings.row_count + "_comment").markdown({autofocus:false,savable:false})
            }
            else
            {
                settings.t_size = settings.$table.children().length;
                var append_row = "<tr id='" + e + settings.table_name + settings.row_count + "'><td class='text-center'><button id='del_" + settings.table_name + settings.row_count + "' type='button' tabindex='-1' class='btn btn-default'><span class='glyphicon glyphicon-remove'></span></button></td>";
                if(exists){append_row +="<td><a name='" +  settings.table_name + e + "_files_" + settings.row_count + "' id='" + settings.table_name + e + "_files_" + settings.row_count + "'></a></td>";}
                else{append_row += "<td><input name='" + settings.table_name + e + "_files_" + settings.row_count + "' id='" + settings.table_name + e + "_files_" + settings.row_count + "' type='file' multiple='multiple'></td>";}
                settings.$table.append(append_row +
                    "<td><select class='selectpicker show-tick' name='" + e + settings.table_name + "_parent_" + settings.row_count + "'id='" + e + settings.table_name + "_parent_" + settings.row_count + "'>" +
                    "<option value='piece'>Attach to Piece</option></select></td>" +
                    "<td><input name='" +  e + settings.table_name + "_source_" + settings.row_count + "' id='" +  e + settings.table_name + "_source_" + settings.row_count + "' class='form-control' autocomplete='off' data-toggle='popover' data-placement='top' data-trigger='focus' data-html='true' title='<b>File Source</b>'" +
                    "data-content='Indicate the source of the file here, such as <em>Choral Wiki</em> or <em>Transcribed by Uploader</em>. If no source is provided, this file will be ignored. This file will be renamed automatically, so does not require a title.'> </td></tr>");
                $("#" +  e + settings.table_name + "_files_" + settings.row_count).filestyle({
                    buttonBefore: true,
                    iconName: "glyphicon-file",
                    buttonText: settings.file_button_name
                });
            }
            initRow(settings.row_count, exists);
            settings.row_count++;
        }

        function initRow(row, exists)
        {
            if (exists)
            {
                var e = "_existing"
            }
            else
            {
                var e = ""
            }
            drawAttachSelects();
            $("#del_" + settings.table_name + row).on("click", function(event)
            {
                var row_num = parseInt(event.currentTarget.getAttribute("id").substring(settings.table_name.length + 4));
                $("#" + settings.table_name + "_files" + row_num).filestyle('destroy');
                settings.$table.children().remove("#" + e + settings.table_name + row_num +  "_tags");
                settings.$table.children().remove("#" + e + settings.table_name + row_num);
                if (settings.table_name !== 'files')
                {
                    renumberRows();
                }
                drawAttachSelects();
            });

            $("#" + e + settings.table_name + "_title_" + row).on("keydown", function(event) {
                if (event.keyCode === 13)
                {
                    event.preventDefault();
                    return false
                }
            });
            $("#" + e + settings.table_name + "_title_" + row).focusout(function() {
                drawAttachSelects();
            });

            $("#show_advanced_"+ settings.table_name + settings.row_count).click(function(event)
            {
                $(event.target.parentElement.parentElement.nextElementSibling).toggle();
            });

            $("input[type=number]").off().keypress(function (event)
            {
                if (event.which !== 0 && event.which !== 8)
                {
                    if (this.value.length > 3 || (event.which < 48 || event.which > 57))
                    {
                        return false
                    }
                }
            });
        }

        function renumberRows()
        {
            for(var j = 1; j < settings.$table.children().length; j++)
            {
                if (j % 2 !== 0)
                {
                    var temp = settings.$table.children()[j];
                    temp.children[1].innerHTML = (j+1)/2;
                }
            }
        }

        function drawAttachSelects(){
            var movements = $("[id^=mov_title], [id^=_existingmov_title] ");
            var content = "<option value='piece'>Attach to Piece</option>";
            var currentIDs = [];
            var attachSelects = $("[id^=files_parent_],[id^=_existingfiles_parent_]");
            var i = 0;
            var oldVal = null;
            for (i = 0; i < movements.length; i++)
            {
                if (movements[i].value !== "")
                {
                    if (i == 0)
                    {
                        content += "<option data-divider='true'></option>";
                    }
                    content += "<option value='" + movements[i].id + "'>" +movements[i].value + "</option>";
                    currentIDs.push(movements[i].id);
                }
            }
            for (i = 0; i < attachSelects.length; i++)
            {
                oldVal = attachSelects[i].value;
                attachSelects[i].innerHTML = content;
                if (oldVal === "" || $.inArray(oldVal, currentIDs) === -1)
                {
                    $(attachSelects[i]).selectpicker('refresh').selectpicker('val', 'piece');
                }
                else
                {
                    $(attachSelects[i]).selectpicker('refresh').selectpicker('val', oldVal);
                }
            }
        }

        this.addRow = function(exists)
        {
            return addRow(exists);
        };
        this.drawAttachSelects = function()
        {
            return drawAttachSelects();
        };
    };

    function autocomplete(inputField, suggestionField, dictionary, multiple) {
        var menuActive = -1;
        var menuSize = -1;
        var isInit = true;
        var gotResults = true;
        var selectedSuggestion;
        var $inputField = $("#" + inputField);
        var $suggestionMenu = $("#" + suggestionField);
        var $suggestionListItems = $suggestionMenu.children().children();

        $inputField.on("keydown", function (event)
        {
            var key = event['keyCode'];

            // Arrow key down moves the active block down the menu
            if (key === 40)
            {
                event.preventDefault();
                $suggestionListItems.eq(menuActive).toggleClass("active");
                menuActive = (menuActive + 1) % menuSize;
                $suggestionListItems.eq(menuActive).toggleClass("active");
                selectedSuggestion = $suggestionListItems.eq(menuActive).text();
            }

            //Arrow key up moves the active block up the menu
            if (key === 38)
            {
                event.preventDefault();
                $suggestionListItems.eq(menuActive).toggleClass("active");
                menuActive = (menuActive - 1);

                if (menuActive < 0)
                    menuActive = menuSize - 1;

                $suggestionListItems.eq(menuActive).toggleClass("active");
                selectedSuggestion = $suggestionListItems.eq(menuActive).text();
            }

            //Enter key sends the active menu item to the input and deletes suggestions
            if (key === 13 && menuSize > 0)
            {
                event.preventDefault();
                write_input();
                $suggestionMenu.html("");
                menuActive = -1;
                menuSize = 0;
                $inputField.focusout()
            }

            if (key === 13)
            {
                event.preventDefault();
                $inputField.focusout()
            }

            if (key === 186)
            {
                $suggestionMenu.html("");
                menuActive = -1;
                menuSize = 0;
                selectedSuggestion = ""
            }
        });

        $inputField.on("keyup focusin", function (event)
        {
            var key = event['keyCode'];

            //Typing a-z, deleteing, or focusing on the input will generate a suggestion list
            if ((key > 63 && key < 91) || key === 8 || event['type'] === "focusin")
            {
                if (multiple)
                {
                    var split_vals = $inputField.val().split(";");
                    var query = encodeURI(split_vals[split_vals.length-1].trim());
                }
                else
                {
                    query = encodeURI($inputField.val());
                }

                if (key === 8 || (query.length - $inputField.val().length) > 1)
                    isInit = true;
                var input_width = $(this).parent().width() - 120;
                //Sends the query to /suggest/ and prints the results to the suggestion-menu
                if ((gotResults || isInit) && selectedSuggestion !== $inputField.val())
                {
                    $.ajax({
                        url: "/suggest/",
                        data: {q: query, d: dictionary},
                        success: function (data)
                        {
                            $suggestionMenu.html("");
                            menuSize = data.length;
                            menuActive = 0;

                            if (isInit && menuSize !== 0)
                                isInit = false;

                            if (menuSize > 0)
                                gotResults = true;
                            else
                                gotResults = false;
                            var suggestions = "";
                            for (var i = 0; i < data.length; i++)
                            {
                                if (i === menuActive)
                                {
                                    suggestions +="<li class='list-group-item active' id='suggestion-item" + i + "'>" + data[i]['name'] + "</li>";
                                }
                                else
                                {
                                    suggestions += "<li class='list-group-item' id='suggestion-item" + i + "'>" + data[i]['name'] + "</li>";
                                }
                            }

                            $suggestionMenu.html("<ul class='listgroup' style='position: absolute; padding-left: 0px; z-index:10; cursor: pointer; width:"+input_width+"px'>" + suggestions + "</ul>");
                            $suggestionListItems = $suggestionMenu.children().children();
                            selectedSuggestion = $suggestionListItems. eq(menuActive).text();
                        },
                        dataType: "json"
                    });
                }
            }
        });

        $inputField.on("focusout", function()
        {
            $suggestionMenu.html("");
            isInit = true;
        });

        //Mouseover on suggestion item activates it
        $suggestionMenu.on("mouseover", function (event)
        {
            var $mouseTarget = $(event['target']);

            if ($mouseTarget.hasClass("list-group-item"))
            {
                $suggestionListItems.eq(menuActive).toggleClass("active", false);
                $mouseTarget.toggleClass("active", true);
                var mouseoverTargetID = $mouseTarget.attr('id');
                menuActive = mouseoverTargetID[mouseoverTargetID.length - 1];
                selectedSuggestion = $suggestionListItems.eq(menuActive).text();
            }
        });

        //Clicking suggestion item sends its value to the input field
        $suggestionMenu.on("mousedown", function (event)
        {
            if (event['target'])
            {
                write_input();
                $suggestionMenu.html("");
                menuActive = -1;
                menuSize = 0;
            }
        });

        function write_input()
        {
            if (multiple)
            {
                var split_vals = $inputField.val().split(";");
                split_vals[split_vals.length-1] = selectedSuggestion;
                var result = split_vals[0] + "; ";
                for (var i = 1; i < split_vals.length; i++)
                {
                    result = result + split_vals[i].trim() + "; ";
                }
                $inputField.val(result);
            }
            else
            {
                $inputField.val(selectedSuggestion);
            }
        }
    }


})(jQuery);