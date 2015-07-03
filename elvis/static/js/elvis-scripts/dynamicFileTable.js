
// Given a button and a table body, this function will add new rows to the table with an input field
// and a file upload field. The inputs will be named table_name_title_# and table_name_files_# and will
// be sent in the post request for the form (the files will appear in request.FILES).
function dynamicFileTable(add_row_button_id, table_body_id, table_name, file_button_name, movement_bool)
{
    //The movement table javascript.
    if (file_button_name === undefined) file_button_name = "Files";
    var row_count = 1;
    var $newRowButton = $("#"+add_row_button_id);
    var $table = $("#"+ table_body_id);
    addRow();

    //Defines row adding behaviour for the plus button
    $newRowButton.on("click", function()
    {
        console.log($table);
        addRow($table);
        $newRowButton.blur();
    });

    function addRow()
    {
        if (movement_bool)
        {
            var t_size = (($table.children().length + 1) / 2);
            $table.append("<tr id='"+ table_name + row_count + "'>" +
            "<td class='text-center'><button id='del_"+ table_name + row_count + "' type='button' tabindex='-1' class='btn btn-default'>-</button></td>" +
            "<td class='text-center' style='padding-top:14px'>" + t_size + "</td>" +
            "<td><input name='" + table_name + "_title_" + row_count + "' id='" + table_name + "_title" + row_count + "' class='form-control' autocomplete='off'> </td>" +
            "<td><input name='" + table_name +"_files_" + row_count + "' id='" + table_name + "_files" + row_count + "' type='file' multiple='multiple' value=''></td>" +
            "<td><button id='show_advanced_"+ table_name + row_count + "' type='button' tabindex='-1'class='btn btn-default'>Show</button></td></tr>"+
            "<tr id='"+ table_name + row_count + "_tags' hidden='hidden'> " +
            "<td colspan='5'>" +
            "<span class='help-block' style='padding:10px'>" +
                "You my override these fields on a per-movement basis. If these fields are left blank, they will default to the values you defined on the previous page." +
            "</span>" +
            "<div class='row' style='padding-left:20px; padding-right:20px'>" +
                "<div class='col-md-6'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Instrumentation</span><input name='"+ table_name + row_count + "_instrumentation' id='"+ table_name + row_count + "_instrumentation' type='text' class='form-control unstyled'></div>" +
                    "<div id='"+ table_name + row_count + "_instrumentation_suggestions' style='padding-left:120px'></div>" +
                    "</div>" +
                "</div>" +
                "<div class='col-md-6'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Number of Voices</span><input name='"+ table_name + row_count + "_number_of_voices' id='"+ table_name + row_count + "_number_of_voices' type='number' class='form-control unstyled'></div>" +
                    "</div>" +
                "</div>" +
            "</div>" +
            "<div class='row' style='padding-left:20px; padding-right:20px'>" +
                "<div class='col-md-12'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Tags</span><input name='"+ table_name + row_count + "_free_tags' id='"+ table_name + row_count + "_free_tags' type='text' class='form-control unstyled'></div>" +
                    "<div id='"+ table_name + row_count + "_free_tags_suggestions' style='padding-left:120px'></div>" +
                    "</div>" +
                "</div>" +
            "</div>" +
            "<div class='row' style='padding-left:20px; padding-right:20px'>" +
                "<div class='col-md-12'>" +
                    "Comments: <div class='form-group'><textarea rows='7' class='form-control' name='"+ table_name + row_count + "_comment' id='"+ table_name + row_count + "_comment' style='resize:vertical'></textarea>"+
                "</div>" +
            "</div>" +
            "</td></tr>");
            autocomplete(table_name + row_count + "_free_tags", table_name + row_count + "_free_tags_suggestions", "tagSuggest", true);
            autocomplete(table_name + row_count + "_instrumentation", table_name + row_count + "_instrumentation_suggestions", "instrumentSuggest", true);
            $("#" + table_name + "_files" + row_count).filestyle({input:false, iconName: "glyphicon-file", buttonText: file_button_name});
        }
        else
        {
            var t_size = $table.children().length;
            $table.append("<tr id='"+ table_name + row_count + "'>" +
            "<td class='text-center'><button id='del_"+ table_name + row_count + "' type='button' tabindex='-1' class='btn btn-default'>-</button></td>" +
            "<td class='text-center' style='padding-top:14px'>" + t_size + "</td>" +
            "<td><input name='" + table_name + "_title_" + row_count + "' id='" + table_name + "_title" + row_count + "' class='form-control' autocomplete='off'> </td>" +
            "<td><input name='" + table_name +"_files_" + row_count + "' id='" + table_name + "_files" + row_count + "' type='file' multiple='multiple' value=''></td></tr>");
            $("#" + table_name + "_files" + row_count).filestyle({input:false, iconName: "glyphicon-file", buttonText: file_button_name});
        }

        initRow(row_count);
        row_count++;
    }

    function initRow(row)
    {
        $("#del_" + table_name + row).on("click", function(event)
        {
            var row_num = parseInt(event.currentTarget.getAttribute("id").substring(table_name.length + 4));
            $("#" + table_name + "_files" + row_num).filestyle('destroy');
            $table.children().remove("#" + table_name + row_num +  "_tags");
            $table.children().remove("#" + table_name + row_num);
            renumberRows();
        });

        $("#" + table_name + "_title" + row).on("keydown", function(event) {
            if (event.keyCode === 13)
            {
                event.preventDefault();
                return false
            }
        });

        $("#show_advanced_"+ table_name + row_count).click(function(event)
        {
            $(event.target.parentElement.parentElement.nextElementSibling).toggle();
        });
    }


    function renumberRows()
    {
        for(var j = 1; j < $table.children().length; j++)
        {
            if (j % 2 !== 0)
            {
                var temp = $table.children()[j];
                temp.children[1].innerHTML = (j+1)/2;
            }
        }
    }
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

}