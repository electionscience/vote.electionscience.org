$(function () { 
  
  var csrfSafeMethod; 

  csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  };

  $('a:contains("remove")').click(function() {
    var alertDiv, alertDivId;
    alertDivId = $(this).attr('id');

    alertDiv = "<div class='alert alert-danger' id='alert" + alertDivId + "'>" + 
    "<p>This poll will be permanently deleted. Are you sure?</p><p>" + 
      "<button id='" + alertDivId + "' type='button' class='btn btn-danger btn-xs'>Delete</button>" + 
      " <button id='" + alertDivId + "' type='button' class='btn btn-primary btn-xs'>Cancel</button>" + 
    "</p</div>";

    if ($('#alert' + alertDivId).length == 0) {
      $('#well' + alertDivId).before(alertDiv);
      $('#well' + alertDivId).css('border-color', 'red');
    }

    $('button:contains("Delete")').click(function() {
      var csrfToken, buttonId;
      buttonId = $(this).attr('id');
      csrfToken = $('#csrfmiddlewaretoken').val();
      $('#well' + buttonId).css('border-color', '#dcdcdc');
      $('#alert' + buttonId).remove();
      $.ajax({
        method: 'DELETE',
        url: '/approval_polls/' + buttonId + '/',
        beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrfToken);
          }
        },
        success: function (data) {
          if ($('.well').length == 1) {
            window.location.reload();
          }
          else {
            $('#well' + buttonId).fadeOut(100, function(){ $(this).remove();});
          }         
        },
        error: function (data) {
        }
      });
    });

    $('button:contains("Cancel")').click(function() {
      var buttonId;
      buttonId = $(this).attr('id');
      $('#well' + buttonId).css('border-color', '#dcdcdc');
      $('#alert' + buttonId).remove();
    });

  });

});
