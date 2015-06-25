
// Given a button and a table body, this function will add new rows to the table with an input field
// and a file upload field. The inputs will be named table_name_title_# and table_name_files_# and will
// be sent in the post request for the form (the files will appear in request.FILES).
function dynamicFileTable(add_row_button_id, table_body_id, table_name, file_button_name)
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
        var t_size = $table.children().length;
        $table.append("<tr id='"+ table_name + row_count + "'>" +
        "<td class='text-center'><button id='del_"+ table_name + row_count + "' type='button' tabindex='-1' class='btn btn-default'>-</button></td>" +
        "<td class='text-center' style='padding-top:14px'>" + t_size + "</td>" +
        "<td><input name='" + table_name + "_title_" + row_count + "' id='" + table_name + "_title" + row_count + "' class='form-control' autocomplete='off'> </td>" +
        "<td><input name='" + table_name +"_files_" + row_count + "' id='" + table_name + "_files" + row_count + "' type='file' multiple='multiple' value=''></td></tr>");
        $("#" + table_name + "_files" + row_count).filestyle({input:false, iconName: "glyphicon-file", buttonText: file_button_name});
        initRow(row_count);
        row_count++;
    }

    function initRow(row)
    {
        $("#del_" + table_name + row).on("click", function(event)
        {
            console.log(event);
            var row_num = parseInt(event.currentTarget.getAttribute("id").substring(table_name.length + 4));
            $("#" + table_name + "_files" + row_num).filestyle('destroy');
            $table.children().remove("#" + table_name + row_num);
            renumberRows();
        });

        $("#" + table_name + "_title" + row).on("keydown", function(event) {
            if (event.keyCode === 13)
            {
                event.preventDefault();
                return false
            }
        })
    }


    function renumberRows()
    {
        for(var j = 1; j < $table.children().length; j++)
        {
            var temp = $table.children()[j];
            temp.children[1].innerHTML = j;
        }
    }
}