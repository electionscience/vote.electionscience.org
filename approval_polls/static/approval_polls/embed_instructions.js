/* Code related to templates/approval_polls/embed_instructions.html */

// Sets the iframe height and the corresponding embed instruction code in the textarea.
function setIframeHeightAndCode(iframeId, textareaId) {

  var iframeHeight, pollLink;

  // get the height of the contents of the iframe.
  iframeHeight = $(iframeId).contents().height();

  // set the height of the iframe to that of its contents.
  $(iframeId).height(iframeHeight);

  // obtain the src attribute of the iframe.
  pollLink = $(iframeId).attr('src');

  // write the HTML code into the textarea.
  $(textareaId).val("<iframe src='" + pollLink + "' width='350px' height='" + iframeHeight + "px'></iframe>");
}


$(window).load(function() {

  setIframeHeightAndCode('#iframePreview', '#textAreaCode');
});

