/**
 * Created by lexpar on 11/08/15.
 */

(function ($)
{
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

        function printStuff()
        {
            console.log(settings);
        }

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
                    "<td><input name='" + settings.table_name + "_title_" + settings.row_count + "' id='" + settings.table_name + "_title_" + settings.row_count + "' class='form-control' autocomplete='off'" +
                    "data-toggle='popover' data-placement='top' data-trigger='focus' data-html='true' title='<b>Movement Title</b>'" +
                    "data-content='If no title is provided, this movement will be ignored on upload. It is not necessary to number movements, as they will retain the ordering in which they are here presented.'> </td>" +
                    "<td><button id='show_advanced_" + settings.table_name + settings.row_count + "' type='button' tabindex='-1'class='btn btn-default'>Show Advanced</button></td></tr>" +
                    "<tr id='" + e + settings.table_name + settings.row_count + "_tags' hidden='hidden'> " +
                    "<td colspan='5'>" +
                    "<div class='row' style='padding-left:12%; padding-right:15px'>" +
                    "<div class='col-md-7'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Instrumentation</span><input name='" + settings.table_name + settings.row_count + "_instrumentation' id='" + settings.table_name + settings.row_count + "_instrumentation' type='text' class='form-control unstyled'></div>" +
                    "<div id='" + settings.table_name + settings.row_count + "_instrumentation_suggestions' style='padding-left:120px'></div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='col-md-5'>" +
                    "<div class='btn-group btn-group-justified form-inline radio' style='margin-top: 0px' id='" + settings.table_name + settings.row_count + "_vocalization' data-toggle='buttons'>" +
                    "<label class='btn btn-default'>" +
                    "<input type='radio' name='" + settings.table_name + settings.row_count + "_vocalization' value='Vocal'>Vocal" +
                    "</label>" +
                    "<label class='btn btn-default'>" +
                    "<input type='radio' name='" + settings.table_name + settings.row_count + "_vocalization' value='Instrumental'>Instrumental" +
                    "</label>" +
                    "<label class='btn btn-default'>" +
                    "<input type='radio' name='" + settings.table_name + settings.row_count + "_vocalization' value='Mixed'>Mixed" +
                    "</label>" +
                    "</div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='row' style='padding-left:12%; padding-right:15px'>" +
                    "<div class='col-md-8'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Tags</span><input name='" + settings.table_name + settings.row_count + "_free_tags' id='" + settings.table_name + settings.row_count + "_free_tags' type='text' class='form-control unstyled'></div>" +
                    "<div id='" + settings.table_name + settings.row_count + "_free_tags_suggestions' style='padding-left:120px'></div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='col-md-4'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Number of Voices</span><input name='" + settings.table_name + settings.row_count + "_number_of_voices' id='" + settings.table_name + settings.row_count + "_number_of_voices' type='number' class='form-control unstyled'></div>" +
                    "</div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='row' style='padding-left:12%; padding-right:15px'>" +
                    "<div class='col-md-12'>" +
                    "<strong>Comments:</strong> <div class='form-group'><textarea rows='7' class='form-control' name='" + settings.table_name + settings.row_count + "_comment' id='" + settings.table_name + settings.row_count + "_comment' style='resize:vertical'></textarea>" +
                    "</div>" +
                    "</div>" +
                    "</td></tr>");
            }
            else
            {
                settings.t_size = settings.$table.children().length;
                var append_row = "<tr id='" + e + settings.table_name + settings.row_count + "'><td class='text-center'><button id='del_" + settings.table_name + settings.row_count + "' type='button' tabindex='-1' class='btn btn-default'><span class='glyphicon glyphicon-remove'></span></button></td>";
                if(exists){append_row +="<td><a name='" + settings.table_name + e + "_files_" + settings.row_count + "' id='" + settings.table_name + e + "_files_" + settings.row_count + "'></a></td>";}
                else{append_row += "<td><input name='" + settings.table_name + e + "_files_" + settings.row_count + "' id='" + settings.table_name + e + "_files_" + settings.row_count + "' type='file' multiple='multiple'></td>";}
                settings.$table.append(append_row +
                    "<td><select class='selectpicker show-tick' name='" + settings.table_name + e + "_parent_" + settings.row_count + "'id='" + settings.table_name + e + "_parent_" + settings.row_count + "'>" +
                    "<option value='piece'>Attach to Piece</option></select></td>" +
                    "<td><input name='" + settings.table_name + e + "_source_" + settings.row_count + "' id='" + settings.table_name + e + "_source_" + settings.row_count + "' class='form-control' autocomplete='off' data-toggle='popover' data-placement='top' data-trigger='focus' data-html='true' title='<b>File Source</b>'" +
                    "data-content='Indicate the source of the file here, such as <em>Choral Wiki</em> or <em>Transcribed by Uploader</em>. If no source is provided, this file will be ignored. This file will be renamed automatically, so does not require a title.'> </td></tr>");
                $("#" + settings.table_name + e + "_files_" + settings.row_count).filestyle({
                    buttonBefore: true,
                    iconName: "glyphicon-file",
                    buttonText: settings.file_button_name
                });
            }
            initRow(settings.row_count);
            settings.row_count++;
        }

        function initRow(row)
        {
            drawAttachSelects();
            $("#del_" + settings.table_name + row).on("click", function(event)
            {
                var row_num = parseInt(event.currentTarget.getAttribute("id").substring(settings.table_name.length + 4));
                $("#" + settings.table_name + "_files" + row_num).filestyle('destroy');
                settings.$table.children().remove("#" + settings.table_name + row_num +  "_tags");
                settings.$table.children().remove("#" + settings.table_name + row_num);
                if (settings.table_name !== 'files')
                {
                    renumberRows();
                }
                drawAttachSelects();
            });

            $("#" + settings.table_name + "_title_" + row).on("keydown", function(event) {
                if (event.keyCode === 13)
                {
                    event.preventDefault();
                    return false
                }
            });
            $("#" + settings.table_name + "_title_" + row).focusout(function() {
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
            var movements = $("[id^=mov_title]");
            var content = "<option value='piece'>Attach to Piece</option>";
            var currentIDs = [];

            var attachSelects = $("[id^=files_parent_],[id^=files_existing_parent_]");
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

        this.printStuff = function()
        {
            return printStuff();
        };
        this.addRow = function(exists)
        {
            return addRow(exists);
        };
    };


    var methods = {
        printStuff : function() {$(this).data('dynamicTable').printStuff();},
        addRow : function(exists) {$(this).data('dynamicTable').addRow(exists);}
    };


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

    }


})(jQuery);

   /* var settings = {
        file_button_name: "Click to select",
        row_count: 1,
        t_size: 0,
        table_name: null,
        movement: false,
        $newRowButton: null
    }

    var methods = {
        init: function(options)
        {
            settings = $.extend({
                file_button_name: "Click to select",
                row_count: 1,
                t_size: 0,
                table_name: null,
                movement: false,
                $newRowButton: null,
                $table: $(this)
            }, options);

            settings.$newRowButton.on("click", function ()
            {
                methods['addRow']();
                settings.$newRowButton.blur()
            });

            return this
        },
        addRow: function()
        {
            if (settings.movement)
            {
                settings.t_size = ((settings.$table.children().length + 1) / 2);
                settings.$table.append("<tr id='" + settings.table_name + settings.row_count + "'>" +
                    "<td class='text-center'><button id='del_" + settings.table_name + settings.row_count + "' type='button' tabindex='-1' class='btn btn-default'><span class='glyphicon glyphicon-remove'></span></button></td>" +
                    "<td class='text-center' style='padding-top:14px'>" + settings.t_size + "</td>" +
                    "<td><input name='" + settings.table_name + "_title_" + settings.row_count + "' id='" + settings.table_name + "_title_" + settings.row_count + "' class='form-control' autocomplete='off'" +
                    "data-toggle='popover' data-placement='top' data-trigger='focus' data-html='true' title='<b>Movement Title</b>'" +
                    "data-content='If no title is provided, this movement will be ignored on upload. It is not necessary to number movements, as they will retain the ordering in which they are here presented.'> </td>" +
                    "<td><button id='show_advanced_" + settings.table_name + settings.row_count + "' type='button' tabindex='-1'class='btn btn-default'>Show Advanced</button></td></tr>" +
                    "<tr id='" + settings.table_name + settings.row_count + "_tags' hidden='hidden'> " +
                    "<td colspan='5'>" +
                    "<div class='row' style='padding-left:12%; padding-right:15px'>" +
                    "<div class='col-md-7'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Instrumentation</span><input name='" + settings.table_name + settings.row_count + "_instrumentation' id='" + settings.table_name + settings.row_count + "_instrumentation' type='text' class='form-control unstyled'></div>" +
                    "<div id='" + settings.table_name + settings.row_count + "_instrumentation_suggestions' style='padding-left:120px'></div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='col-md-5'>" +
                    "<div class='btn-group btn-group-justified form-inline radio' style='margin-top: 0px' data-toggle='buttons'>" +
                    "<label class='btn btn-default'>" +
                    "<input type='radio' name='" + settings.table_name + settings.row_count + "_vocalization' value='Vocal'>Vocal" +
                    "</label>" +
                    "<label class='btn btn-default'>" +
                    "<input type='radio' name='" + settings.table_name + settings.row_count + "_vocalization' value='Instrumental'>Instrumental" +
                    "</label>" +
                    "<label class='btn btn-default'>" +
                    "<input type='radio' name='" + settings.table_name + settings.row_count + "_vocalization' value='Mixed'>Mixed" +
                    "</label>" +
                    "</div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='row' style='padding-left:12%; padding-right:15px'>" +
                    "<div class='col-md-8'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Tags</span><input name='" + settings.table_name + settings.row_count + "_free_tags' id='" + settings.table_name + settings.row_count + "_free_tags' type='text' class='form-control unstyled'></div>" +
                    "<div id='" + settings.table_name + settings.row_count + "_free_tags_suggestions' style='padding-left:120px'></div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='col-md-4'>" +
                    "<div class='form-group'>" +
                    "<div class='input-group'><span class='input-group-addon'>Number of Voices</span><input name='" + settings.table_name + settings.row_count + "_number_of_voices' id='" + settings.table_name + settings.row_count + "_number_of_voices' type='number' class='form-control unstyled'></div>" +
                    "</div>" +
                    "</div>" +
                    "</div>" +
                    "<div class='row' style='padding-left:12%; padding-right:15px'>" +
                    "<div class='col-md-12'>" +
                    "<strong>Comments:</strong> <div class='form-group'><textarea rows='7' class='form-control' name='" + settings.table_name + settings.row_count + "_comment' id='" + settings.table_name + settings.row_count + "_comment' style='resize:vertical'></textarea>" +
                    "</div>" +
                    "</div>" +
                    "</td></tr>");
            }
            else
            {
                settings.t_size = settings.$table.children().length;
                settings.$table.append("<tr id='" + settings.table_name + settings.row_count + "'>" +
                    "<td class='text-center'><button id='del_" + settings.table_name + settings.row_count + "' type='button' tabindex='-1' class='btn btn-default'><span class='glyphicon glyphicon-remove'></span></button></td>" +
                    "<td><input name='" + settings.table_name + "_files_" + settings.row_count + "' id='" + settings.table_name + "_files_" + settings.row_count + "' type='file' multiple='multiple'></td>" +
                    "<td><select class='selectpicker show-tick' name='" + settings.table_name + "_parent_" + settings.row_count + "'id='" + settings.table_name + "_parent_" + settings.row_count + "'>" +
                    "<option value='piece'>Attach to Piece</option></select></td>" +
                    "<td><input name='" + settings.table_name + "_source_" + settings.row_count + "' id='" + settings.table_name + "_source_" + settings.row_count + "' class='form-control' autocomplete='off' data-toggle='popover' data-placement='top' data-trigger='focus' data-html='true' title='<b>File Source</b>'" +
                    "data-content='Indicate the source of the file here, such as <em>Choral Wiki</em> or <em>Transcribed by Uploader</em>. If no source is provided, this file will be ignored. This file will be renamed automatically, so does not require a title.'> </td></tr>");
                $("#" + settings.table_name + "_files_" + settings.row_count).filestyle({
                    buttonBefore: true,
                    iconName: "glyphicon-file",
                    buttonText: settings.file_button_name
                });
            }
            settings.row_count++;
        }
    };

    $.fn.table2 = function (methodOrOptions)
    {
        if (methods[methodOrOptions])
        {
           return methods[methodOrOptions].apply( this, Array.prototype.slice.call( arguments, 1 ));
        }
        else if (typeof methodOrOptions === 'object' || ! methodOrOptions)
        {
            return methods.init.apply( this, arguments );
        }
        else
        {
            $.error( 'Method ' +  methodOrOptions + ' does not exist on table2' );
        }

        function addRow()
        {

        }

        function initRow(row)
        {
            drawAttachSelects();

            $("#del_" + settings.table_name + row).on("click", function(event)
            {
                var row_num = parseInt(event.currentTarget.getAttribute("id").substring(settings.table_name.length + 4));
                $("#" + settings.table_name + "_files" + row_num).filestyle('destroy');
                settings.$table.children().remove("#" + settings.table_name + row_num +  "_tags");
                settings.$table.children().remove("#" + settings.table_name + row_num);
                if (settings.table_name !== 'files')
                {
                    renumberRows();
                }
                drawAttachSelects();
            });

            $("#" + settings.table_name + "_title_" + row).on("keydown", function(event) {
                if (event.keyCode === 13)
                {
                    event.preventDefault();
                    return false
                }
            });
            $("#" + settings.table_name + "_title_" + row).focusout(function() {
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
            var movements = $("[id^=mov_title]");
            var content = "<option value='piece'>Attach to Piece</option>";
            var currentIDs = [];

            var attachSelects = $("[id^=files_parent_]");
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
            return this;
    }
    }(jQuery));
*/