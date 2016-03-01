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

    $("#private-button").click(function (event)
    {
        $.ajax({
            type: "patch",
            url: "/collection/{{ content.id }}",
            data: {'public': false},
            success: function (data)
            {
                location.reload();
            }
        })
    });

    $("#public-button").click(function (event)
    {
        $.ajax({
            type: "patch",
            url: "/collection/{{ content.id }}",
            data: {'public': true},
            success: function (data)
            {
                location.reload();
            }
        })
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
                url: "/collection/{{ content.id }}",
                success: function (data)
                {
                    console.log("Deleted {{ content.title }}");
                    document.location.href = '/collections/?creator={{ user.username }}';
                }
            })
        })
    });
    $("#remove-member-button").click(function (event)
    {
        event.preventDefault();

        var pieces = [];
        var names = [];
        var pieceSelectors = $('input[name="remove-piece"]:checked').map(function() {
            pieces.push(parseInt($(this).val()));
            names.push($(this)["context"]["parentElement"].textContent.trim());
        });

        if (pieces.length > 0) {
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
                    url: "/collection/{{ content.id }}/elements/",
                    data: JSON.stringify({
                        piece_ids: pieces
                    }),
                    "contentType": "application/json",
                    success: function (data) {
                        console.log("Success:", data);
                        document.location.href = '/collection/{{ content.id }}/';
                    },
                    error: function(data) {
                        console.log("Error:", data);
                        document.location.href = '/collection/{{ content.id }}/';
                    }
                })
            });
        } else {
            $base_modal_header.html("<h4 class='modal-title'>Cannot Remove</h4>");
            $base_modal_body.html("<p>Please select at least 1 piece to remove.</p>");
            $base_modal_footer.html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
            $base_modal.modal('show');
        }
    });
});