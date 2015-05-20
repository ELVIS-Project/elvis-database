/*
    Generates typeahead style suggestions based on a solr search. The /suggest/ page should
    be configured to process GET requests by querying the Solr suggestion module and returning
    a JSON array of names.

    Example:
    Given q = 'ba' and d = 'composerSearch', /suggest/ should request a JSON string from
    SOLR_SERVER/suggest/?wt=json&suggest.dictionary=composerSearch&q=ba

    inputField: The id of the HTML input field who's value will be sent as a query.
    suggestionField: The id of the HTML list where results will be sent.
    dictionary: The name of the suggestion dictionary to be used.
 */
function autocomplete(inputField, suggestionField, dictionary) {
    var menuActive = -1;
    var previousSize = -1;
    var menuSize = -1;
    var $inputField = $("#" + inputField);
    var $suggestionMenu = $("#" + suggestionField);

    $inputField.on("keydown", function (event)
    {
        var key = event['keyCode'];

        // Arrow key down moves the active block down the menu
        if (key == 40)
        {
            event.preventDefault();
            $suggestionMenu.children().eq(menuActive).toggleClass("active");
            menuActive = (menuActive + 1) % menuSize;
            $suggestionMenu.children().eq(menuActive).toggleClass("active");
        }

        //Arrow key up moves the active block up the menu
        if (key == 38)
        {
            event.preventDefault();
            $suggestionMenu.children().eq(menuActive).toggleClass("active");
            menuActive = (menuActive - 1);

            if (menuActive < 0)
                menuActive = menuSize - 1;

            $suggestionMenu.children().eq(menuActive).toggleClass("active");
        }

        //Enter key sends the active menu item to the input and deletes suggestions
        if (key == 13 && menuActive != -1 && menuSize > 0)
        {
            event.preventDefault();
            $inputField.val($suggestionMenu.children().eq(menuActive).text());
            $suggestionMenu.html("");
            menuActive = -1;
            menuSize = 0;
        }

        if (key == 13)
            event.preventDefault()
    });

    $inputField.on("keyup", function (event)
    {
        var key = event['keyCode'];

        //This block triggers on a-z and del to populate the suggestion list.
        if ((key > 63 && key < 91) || key == 8)
        {
            var query = $inputField.val();

            if (key == 8)
                previousSize = -1;

            if (!(previousSize == -1) && !(menuSize == 0))
                previousSize = menuSize;

            //Sends the query to /suggest/ and prints the results to the suggestion-menu
            if (previousSize != 0)
            {
                $.ajax({
                    url: "/suggest/",
                    data: {q: query, d: dictionary},
                    success: function (data) {
                        $suggestionMenu.html("");
                        menuSize = data.length;
                        menuActive = 0;

                        for (i = 0; i < data.length; i++)
                        {
                            if (i == menuActive)
                            {
                                $suggestionMenu.append(
                                    "<li class='list-group-item active' id='suggestion-item" + i + "'>" + data[i].name + "</li>");
                            }
                            else
                            {
                                $suggestionMenu.append(
                                    "<li class='list-group-item' id='suggestion-item" + i + "'>" + data[i].name + "</li>");
                            }
                        }
                    },
                    dataType: "json"
                });
            }
        }
    });

    $inputField.on("focusout", function()
    {
        menuActive = -1;
        $suggestionMenu.html("");
    });

    //Mouseover on suggestion item activates it
    $suggestionMenu.on("mouseover", function (event) {
        var $mouseTarget = $(event['target']);

        if ($mouseTarget.hasClass("list-group-item")) {
            $suggestionMenu.children().eq(menuActive).toggleClass("active", false);
            $mouseTarget.toggleClass("active", true);
            var mouseoverTargetID = $mouseTarget.attr('id');
            menuActive = mouseoverTargetID[mouseoverTargetID.length - 1];
        }
    });

    //Clicking suggestion item sends its value to the input field
    $suggestionMenu.on("click", function (event) {
        if (event['target']) {
            $inputField.val($suggestionMenu.children().eq(menuActive).text());
            $suggestionMenu.html("");
            menuActive = -1;
            menuSize = 0;
        }
    })

}
