$(document).ready(function ($) {
    var newCollectionForm = $("#new-collection-form");
    var titleInput = $('input[name="title"]');
    var titleGroup = $("#title-group");
    var isValid = false;
    var statusClassNames = {
        success: "has-success",
        error: "has-error"
    };

    $('[data-toggle="popover"]').popover();

    newCollectionForm.submit(function (event) {
        if (!isValid) {
            event.preventDefault();
            // Get the title
            var title = titleInput[0].value;
            titleInput.focus();
            titleGroup.addClass(statusClassNames.error);

            if (title.length > 0) {
                // Submit the form for realz
                isValid = true;
                titleGroup.removeClass(statusClassNames.error);
                titleGroup.addClass(statusClassNames.success);
                newCollectionForm.submit();
            }
        }
    });
});