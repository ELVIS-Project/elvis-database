$(document).ready(function ($) {
    var collection = {};

    // Form fields
    var titleField = $('input[name="title"]');
    var commentField = $('textarea[name="comment"]');
    //var permissionField = $('input[name="permission"]');
    var permissionField = {
        public: $('input[name="permission"][value="Public"]'),
        private: $('input[name="permission"][value="Private"]')
    };


    /**
     * Request the server for the latest collection field data.
     */
    $.ajax({
        datatype: "json",
        url: window.location.href  + "?format=json",
        success: function (data)
        {
            collection = data;
            populateForm(collection);
        }
    });


    /**
     * Logic for form validation and submission.
     */
    $("#new-collection-form").submit(function (event) {
        event.preventDefault();

        $.ajax({
            type: "patch",
            url: "/collection/" + collection['id'] + "/",
            data: getFormValues(),
            success: function (data) {
                // Redirect back to the collection page
                window.location.href = data["url"];
            },
            error: function (data) {
                // TODO: Display an error message
                console.log(data);
            }
        })
    });


    /**
     * Populate the HTML form with existing values.
     *
     * @param collection
     */
    function populateForm(collection) {
        titleField.val(collection["title"]);
        commentField.val(collection["comment"]);
        if (collection["public"]) {
            // Mark the public box checked
            permissionField.public.prop("checked", true);
            permissionField.public.parent().addClass("active");
            permissionField.private.prop("checked", false);
            permissionField.private.parent().removeClass("active");
        } else {
            // Mark the private box checked
            permissionField.public.prop("checked", false);
            permissionField.public.parent().removeClass("active");
            permissionField.private.prop("checked", true);
            permissionField.private.parent().addClass("active");
        }
    }


    /**
     * Get an object representing the values of the form fields.
     *
     * @returns {{title: *, comment: *, public: *}}
     */
    function getFormValues() {
        return {
            "title": titleField.val(),
            "comment": commentField.val(),
            "public": permissionField.public.prop("checked")
        };
    }
});