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
function autocomplete(inputField, suggestionField, dictionary, multiple)
{
    // A timeout to delay requests
    var requestTimeout = undefined;
    // 0.25 second delay for timeout
    var timeoutDelay = 250;
    var menuActive = -1;
    var menuSize = -1;
    var isInit = true;
    var gotResults = true;
    var chosenSuggestion = "";
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
            if (menuActive !== -1)
            {
                $suggestionListItems.eq(menuActive).toggleClass("active");
            }
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
            if (menuActive == -1)
            {
                return;
            }
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
            isInit = true;
            selectedSuggestion = ""
        }
    });

    $inputField.on("keyup focusin", function (event)
    {
        var key = event['keyCode'];

        //Typing a-z, deleteing, or focusing on the input will generate a suggestion list
        if ((key > 47 && key < 58) || (key > 64 && key < 91) || key === 8 || event['type'] === "focusin")
        {
            if (multiple === 'list')
            {
                var split_vals = $inputField.val().split(";");
                var query = encodeURI(split_vals[split_vals.length - 1].trim());
            }
            else if (multiple === 'bool')
            {
                var split_vals = $inputField.val().split(/(AND|OR|NOT)/);
                var query = encodeURI(split_vals[split_vals.length - 1].trim());
            }
            else
            {
                query = encodeURI($inputField.val());
            }

            if (multiple === 'bool')
                var input_width = $inputField.parent().width();
            else
                var input_width = $inputField.parent().width() - 130;

            if (key === 8 || (query.length) < 2)
                isInit = true;

            //Sends the query to /suggest/ and prints the results to the suggestion-menu
            if ((gotResults || isInit) && query.length > 2)
            {
                // Clear an existing timeout
                window.clearTimeout(requestTimeout);
                // Set a new timeout
                requestTimeout = window.setTimeout(
                    function() {
                        $.ajax({
                            url: "/suggest/",
                            data: {q: query, d: dictionary},
                            success: function (data)
                            {
                                $suggestionMenu.html("");
                                menuSize = data.length;
                                menuActive = -1;

                                if (menuSize === 1 && query === chosenSuggestion)
                                {
                                    return false;
                                }

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
                                        suggestions += "<li class='list-group-item active suggestion-element' id='suggestion-item" + i + "'>" + data[i]['name'] + "</li>";
                                    }
                                    else
                                    {
                                        suggestions += "<li class='list-group-item suggestion-element' id='suggestion-item" + i + "'>" + data[i]['name'] + "</li>";
                                    }
                                }

                                $suggestionMenu.html("<ul class='listgroup suggestion-menu' style='width:" + input_width + "px'>" + suggestions + "</ul>");
                                $suggestionListItems = $suggestionMenu.children().children();
                                selectedSuggestion = $suggestionListItems.eq(menuActive).text();
                            },
                            dataType: "json"

                        });
                    },
                    timeoutDelay
                );
            }
            else
            {
                $suggestionMenu.html("");
                menuSize = 0;
                menuActive = 0;
                selectedSuggestion = "";
            }
        }
    });

    $inputField.on("focusout", function ()
    {
        if (selectedSuggestion !== "")
        {
            chosenSuggestion = encodeURI(selectedSuggestion);
        }
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
        console.log(event);
        if (event['target']['className'].indexOf('suggestion-element') > -1) // If you clicked on a selection element and not the scrollbar.
        {
            write_input();
            $suggestionMenu.html("");
            menuActive = -1;
            menuSize = 0;
        }
    });

    function write_input()
    {
        if (multiple === 'list')
        {
            var split_vals = $inputField.val().split(";");
            split_vals[split_vals.length - 1] = selectedSuggestion;
            var result = split_vals[0] + "; ";
            for (var i = 1; i < split_vals.length; i++)
            {
                result = result + split_vals[i].trim() + "; ";
            }
            $inputField.val(result);
        }
        else if (multiple === 'bool')
        {
            var split_vals = $inputField.val().split(/(AND|OR|NOT)/);
            split_vals[split_vals.length - 1] = selectedSuggestion;
            for (var i = 0; i < split_vals.length; i++)
            {
                split_vals[i] = $.trim(split_vals[i])
            }
            $inputField.val(split_vals.join(' '))
        }
        else
        {
            $inputField.val(selectedSuggestion);
        }
        chosenSuggestion = encodeURI(selectedSuggestion);
    }
}
