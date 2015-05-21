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
    var menuSize = -1;
    var isInit = true;
    var gotResults = true;
    var query = "";
    var selectedSuggestion;
    var $inputField = $("#" + inputField);
    var $suggestionMenu = $("#" + suggestionField);

    $inputField.on("keydown", function (event)
    {
        var key = event['keyCode'];

        // Arrow key down moves the active block down the menu
        if (key === 40)
        {
            event.preventDefault();
            $suggestionMenu.children().eq(menuActive).toggleClass("active");
            menuActive = (menuActive + 1) % menuSize;
            $suggestionMenu.children().eq(menuActive).toggleClass("active");
            selectedSuggestion = $suggestionMenu.children().eq(menuActive).text();
        }

        //Arrow key up moves the active block up the menu
        if (key === 38)
        {
            event.preventDefault();
            $suggestionMenu.children().eq(menuActive).toggleClass("active");
            menuActive = (menuActive - 1);

            if (menuActive < 0)
                menuActive = menuSize - 1;

            $suggestionMenu.children().eq(menuActive).toggleClass("active");
            selectedSuggestion = $suggestionMenu.children().eq(menuActive).text();
        }

        //Enter key sends the active menu item to the input and deletes suggestions
        if (key === 13 && menuActive !== -1)
        {
            event.preventDefault();
            $inputField.val(selectedSuggestion);
            $suggestionMenu.html("");
            menuActive = -1;
            menuSize = 0;
        }

        if (key === 13)
            event.preventDefault()
    });

    $inputField.on("keyup focusin", function (event)
    {
        var key = event['keyCode'];

        //Typing a-z, deleteing, or focusing on the input will generate a suggestion list
        if ((key > 63 && key < 91) || key === 8 || event['type'] === "focusin")
        {

            if (key === 8 || (query.length - $inputField.val().length) > 1)
                isInit = true;

            query = $inputField.val();

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

                        for (var i = 0; i < data.length; i++)
                        {
                            if (i === menuActive)
                            {
                                $suggestionMenu.append(
                                    "<li class='list-group-item active' id='suggestion-item" + i + "'>" + data[i]['name'] + "</li>");
                            }
                            else
                            {
                                $suggestionMenu.append(
                                    "<li class='list-group-item' id='suggestion-item" + i + "'>" + data[i]['name'] + "</li>");
                            }
                        }
                        selectedSuggestion = $suggestionMenu.children().eq(menuActive).text();
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
            $suggestionMenu.children().eq(menuActive).toggleClass("active", false);
            $mouseTarget.toggleClass("active", true);
            var mouseoverTargetID = $mouseTarget.attr('id');
            menuActive = mouseoverTargetID[mouseoverTargetID.length - 1];
            selectedSuggestion = $suggestionMenu.children().eq(menuActive).text();
        }
    });

    //Clicking suggestion item sends its value to the input field
    $suggestionMenu.on("mousedown", function (event)
    {
        if (event['target'])
        {
            $inputField.val(selectedSuggestion);
            $suggestionMenu.html("");
            menuActive = -1;
            menuSize = 0;
        }
    });
}
