(function() {
  var setIframeHeightAndCode;

  /* Sets the iframe height and the corresponding embed instruction code in the
     textarea. */
  setIframeHeightAndCode = function(iframeId, textareaId) {
    var iframeHeight, pollLink;
 
    iframeHeight = $(iframeId).contents().height();
    $(iframeId).height(iframeHeight);
    pollLink = $(iframeId).attr('src');

    $(textareaId).val("<iframe src='" + pollLink + "' width='350px' height='" +
      iframeHeight + "px'></iframe>");
  }

  $(window).load(function() {
    setIframeHeightAndCode('#iframePreview', '#textAreaCode');
  });

}());
