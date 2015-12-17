(function() {
  var setIframeHeightAndCode;

  /* Sets the iframe height and the corresponding embed instruction code in the
     textarea. */
  setIframeHeightAndCode = function(iframeId, textareaId) {
    var iframeHeight, pollLink;
 
    iframeHeight = $(iframeId).contents().height();
    $(iframeId).height(iframeHeight);
    pollLink = $(iframeId).attr('src');

    $(textareaId).text("<iframe src='" + pollLink + "' width='400px' height='" +
      iframeHeight + "px'></iframe>");
  };

  $(window).load(function() {
    setIframeHeightAndCode('#iframePreview', '#textAreaCode');
  });

}());

$(document).ready(function() {
  $("#copyText").click(function(){

    /* Copy the HTML Code in textarea to ClipBoard */

    var copyTextarea = document.querySelector('#textAreaCode');
    copyTextarea.select();

    try {
      document.execCommand('copy');
      if ($("#alert-success").length === 0)
      {
        $("<div id = 'alert-success' class='alert alert-success' style='margin-top:10px'>" +
          "<strong>Success!</strong> Text copied to clipboard!.</div>")
        .insertAfter($("#copyText"));
      }      
    } 
    catch (err) {
      if ($("#alert-danger").length === 0)
      {
        $("<div id = 'alert-danger' class='alert alert-danger' style='margin-top:10px'>" +
          "<strong>Oops, unable to copy!</strong>" +
          " To copy the text to clipboard: Ctrl+C!.</div>")
        .insertAfter($("#copyText"));
      }
    }
  });
});
