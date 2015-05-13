/* Code related to templates/approval_polls/embed_instructions.html */

// Sets the iframe height and the corresponding embed instruction code in the textarea.
function setIframeHeightAndCode(iframeId, textareaId, pollLink) {

    // get the height of the contents of the iframe.
    var iframeHeight = $(iframeId).contents().height();

    // set the height of the iframe to that of its contents.
    $(iframeId).height(iframeHeight);

    // write the HTML code into the textarea.
    $(textareaId).val("<iframe src='"+pollLink+"' width='350px' height='"+iframeHeight+"px'></iframe>");
}


$(window).load(function() {

    var iframeId = '#iframePreview';
    var textareaId = '#textAreaCode';
    var pollLink = $(iframeId).attr('src');

    // Set the iframe height and textarea code.
    setIframeHeightAndCode(iframeId, textareaId, pollLink);
});

