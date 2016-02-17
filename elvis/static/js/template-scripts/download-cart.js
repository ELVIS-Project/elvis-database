$(document).ready(function () {
    var task_id = null;
    var poll_interval;
    var $progress = $("#progress");
    var $progress_div = $("#progress-bar-div");


    $("#collection-table").tablesorter({
        headers: {0: {sorter: false}, 1: {sorter: false}},
        textExtraction: "complex",
        sortList: [[3, 0], [5, 0]]
    });


    $(".remove-row").click(function (event) {
        var id = $(event.target).parents('tr').children()[1].textContent;
        var item_type = $(event.target).parents('tr').children()[5].textContent;
        if (item_type[0] == "M")
            item_type = "elvis_movement";
        else
            item_type = "elvis_piece";
        $(event.target).parents('tr').remove();
        $.ajax({
            type: "post",
            url: "/download-cart/",
            data: {
                'action': "remove",
                'id': id,
                'item_type': item_type
            },
            success: function (data) {
                var $collection_count = $("#collection-count");
                $collection_count.fadeOut(100, function () {
                    $collection_count.text("(" + data.count + ")");
                });
                $collection_count.fadeIn(100);
            }
        })
    });

    $("#open-clear-modal").click(function () {
        $base_modal_title.html("Confirm clear");
        $base_modal_close_btn.show();
        $base_modal_body.html("<p>Are you sure you want to clear your current collection?</p>");
        var footer = [
            "<button type='button' class='btn btn-default' data-dismiss='modal'>No </button>",
            "<button id='clear-collection' type='button' class='btn btn-danger' data-dismiss='modal'>",
            "<span class='glyphicon glyphicon-remove'></span> Yes",
            "</button>"];
        $base_modal_footer.html(footer.join());

        $("#clear-collection").click(function () {
            $("#collection-table").find("tbody").empty();
            $.ajax({
                type: "post",
                url: "/download-cart/",
                data: {'clear-collection': true},
                success: function (data) {
                    var $collection_count = $("#collection-count");
                    $collection_count.fadeOut(100, function () {
                        $collection_count.text("(0)");
                    });
                    $collection_count.fadeIn(100);
                }
            })
        });
        $base_modal.modal("show");
    });



    $("#save-collection").click(function () {
        $('#save_modal').modal('show');
    });

    $("#open-download-modal").click(function () {
        close_progress_bar();
        $("#download-modal").modal("show");
    });

    $("#confirm-download").click(function () {
        /**
         * Get the file extensions that are currently checked.
         *
         * @returns {Array}
         */
        var getFileExtensions = function() {
            var fileExtensions = [];
            $('input[name="file-extension-selector"]:checked').each(function(index){
                fileExtensions.push($(this).val());
            });
            // Handle empty case
            if (fileExtensions.length === 0) {
                fileExtensions.push("all");
            }
            return fileExtensions;
        };
        $.ajax({
            type: "get",
            url: "/downloading/",
            async: false,
            data: {'extensions': getFileExtensions()},
            success: function (data) {
                console.log(data);
                $progress_div.slideDown();
                task_id = data['task'];
                poll_interval = setInterval(poll_status, 500, task_id);
            }
        });
    });

    $("#cancel-download").click(function()
    {
        clearInterval(poll_interval);
        close_progress_bar();
    });

    function poll_status(id)
    {
        if (id === null)
        {
            console.log("ping");
            return;
        }
        $.ajax({
            type: "get",
            url: "/downloading/?task=" + id,
            success: function (data) {
                console.log(data);
                update_progress_bar(data);
                if(data['ready'] === true)
                {
                    clearInterval(poll_interval);
                    window.location = data['path'];
                    update_progress_bar({'progress': 100});
                }
            },
            error: function(data)
            {
                console.log(data);
                clearInterval(poll_interval);
                close_progress_bar();
                $("#download-modal-body").html("Error zipping cart!")
            }
        });
    }

    function update_progress_bar(data)
    {
        $progress.css("width", data['progress'] + "%");
        if (data['progress'] === 100)
        {
            $progress_div.removeClass('progress-striped');
        }
    }

    function close_progress_bar(){
        update_progress_bar({'progress': 0});
        $progress_div.addClass('progress-striped');
        $progress_div.hide();
        clearInterval(poll_interval);
    }
});