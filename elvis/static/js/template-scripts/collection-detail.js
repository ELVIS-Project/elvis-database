$(document).ready(function ($)
{
    $("#piece-table").tablesorter({
        headers: {0: {sorter: false}},
        textExtraction: "complex",
        sortList: [[2,0]]
    });

    $("#mov-table").tablesorter({
        headers: {0: {sorter: false}},
        textExtraction: "complex",
        sortList: [[2,0]]
    });

    $("#delete-button").click(function (event)
    {
        $base_modal_header.html("<h4 class='modal-title'>Confirm Deletion.</h4>");
        $base_modal_body.html("<p>Are you sure you want to delete this Collection?</p>");
        $base_modal_footer.html('<button type="button" class="btn btn-default" data-dismiss="modal">No</button>' +
            '<button id="confirm-delete-button" type="button" class="btn btn-danger" data-dismiss="modal">' +
            '<span class="glyphicon glyphicon-remove"></span>Yes</button>');
        $base_modal.modal('show');
        $("#confirm-delete-button").click(function (event)
        {
            $.ajax({
                type: "delete",
                url: window.location.href,
                success: function (data)
                {
                    console.log("Deleted {{ content.title }}");
                    document.location.href = '/collections/mine/';
                }
            })
        })
    });
    $("#remove-member-button").click(function (event)
    {
        event.preventDefault();

        var pieces = [];
        var movements = [];
        var names = [];
        $('input[name="remove-piece"]:checked').map(function() {
            pieces.push(parseInt($(this).val()));
            names.push($(this)["context"]["parentElement"].textContent.trim());
        });
        $('input[name="remove-movement"]:checked').map(function() {
            movements.push(parseInt($(this).val()));
            names.push($(this)["context"]["parentElement"].textContent.trim());
        });

        if (names.length > 0) {
            $base_modal_header.html("<h4 class='modal-title'>Confirm Removal.</h4>");
            $base_modal_body.html(
                "<p>Are you sure you want to remove the following items from the collection?</p>"
                +"<ul><li>" + names.join("</li><li>") + "</li></ul>"
            );
            $base_modal_footer.html('<button type="button" class="btn btn-default" data-dismiss="modal">No</button>' +
                '<button id="confirm-delete-button" type="button" class="btn btn-danger" data-dismiss="modal">' +
                '<span class="glyphicon glyphicon-remove"></span>Yes</button>');
            $base_modal.modal('show');
            $("#confirm-delete-button").click(function (event)
            {
                $.ajax({
                    type: "delete",
                    url: window.location.href + "elements/",
                    data: JSON.stringify({
                        piece_ids: pieces,
                        movement_ids: movements
                    }),
                    "contentType": "application/json",
                    success: function (data) {
                        console.log("Success:", data);
                        document.location.href = window.location.href;
                    },
                    error: function(data) {
                        console.log("Error:", data);
                        document.location.href = window.location.href;
                    }
                })
            });
        } else {
            $base_modal_header.html("<h4 class='modal-title'>Cannot Remove</h4>");
            $base_modal_body.html("<p>Please select at least 1 piece or movement to remove.</p>");
            $base_modal_footer.html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
            $base_modal.modal('show');
        }
    });

    $('form[name="add-curator"]').submit(function(event) {
        event.preventDefault();
        // Grab the username
        var userName = event.target[0].value;
        var errorMessage = event.target.children[3];
        console.log(event);
        // Hit the API
        var url = window.location.href + "curators/";
        $.ajax({
            url: url,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            type: "post",
            data: JSON.stringify({
                username: userName
            }),
            dataType: 'json',
            success: function(data) {
                console.log("success:", data);
                // Refresh the page
                document.location.href = window.location.href;
            },
            error: function (data) {
                console.log("error:", data);
                console.log(errorMessage);
                errorMessage.innerHTML = data.responseText;
            }
        });
    });

    $('form[name="remove-curator"]').submit(function(event) {
        event.preventDefault();

        var usernames = [];
        // Get the usernames
        $('input[name="remove-curator"]:checked').map(function() {
            usernames.push($(this).val());
        });

        if (usernames.length > 0) {
            var url = window.location.href + "curators/";
            // Some things were checked!
            $.ajax({
                url: url,
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                type: "delete",
                data: JSON.stringify({
                    usernames: usernames
                }),
                dataType: 'json',
                success: function(data) {
                    console.log("success:", data);
                    //// Refresh the page
                    //document.location.href = window.location.href;
                },
                error: function (data) {
                    console.log("error:", data);
                    //console.log(errorMessage);
                    //errorMessage.innerHTML = data.responseText;
                }
            });
        }
    });
});
