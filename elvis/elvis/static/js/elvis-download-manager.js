
function executeDownload()
{

}

function addToDownloads(obj)
{
    console.log("Adding to downloads");
    var type = $(obj).data('type');
    var item_id = $(obj).data('itemId');
    $.ajax("/downloads",
    {
        type: "PUT",
        data: {
            "type": type,
            "item_id": item_id
        }
    }).done(function(data)
    {
        console.log("Success!");
    });
}

function initializeDownloadBadges()
{
    $(".download-badge").on('click', function(event)
    {
        console.log("I have been clicked!");
        addToDownloads(this);
    });
}

function initializeDownloadButton()
{
    $("#download-all").on('click', function(event)
    {
        $.ajax('/download-files',
        {

        }).done(function(data)
        {
            console.log(data);
        });
    });
}