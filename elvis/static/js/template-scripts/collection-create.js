$(document).ready(function ($) {
    var newCollectionForm = $("#new-collection-form");
    var titleInput = $('input[name="title"]');
    var isValid = false;

    newCollectionForm.submit(function (event) {
        if (!isValid) {
            event.preventDefault();
            // Get the title
            var title = titleInput[0].value;

            if (title.length > 0) {
                // Submit the form for realz
                isValid = true;
                newCollectionForm.submit();
            }
        }
    });
});