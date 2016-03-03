$(function () { 
  
  var csrfSafeMethod; 

  csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  };

  $('a[id^="delete-poll-"]').click(function() {
    var alertDiv, alertDivId;
    alertDivId = $(this).attr('id');
    alertDivId = alertDivId.split('-').pop();

    alertDiv = "<div class='alert alert-danger' id='alert" + alertDivId + "'>" + 
    "<p>This poll will be permanently deleted. Are you sure?</p><p>" + 
      "<button id='confirm-delete-" + alertDivId + "' type='button' class='btn btn-danger btn-xs'>Delete</button>" + 
      " <button id='cancel-delete-" + alertDivId + "' type='button' class='btn btn-primary btn-xs'>Cancel</button>" + 
    "</p></div>";

    if ($('#alert' + alertDivId).length == 0) {
      $('.well').css('border-color', '#dcdcdc');
      $('.alert').remove();
      $('#well' + alertDivId).before(alertDiv);
      $('#well' + alertDivId).css('border-color', 'red');
    }

    $('button[id^="confirm-delete-"]').click(function() {
      var csrfToken, buttonId;
      buttonId = $(this).attr('id');
      buttonId = buttonId.split('-').pop();
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
          $('#well' + buttonId).remove();
          window.location.reload();       
        },
        error: function (data) {
        }
      });
    });

    $('button[id^="cancel-delete-"]').click(function() {
      var buttonId;
      buttonId = $(this).attr('id');
      buttonId = buttonId.split('-').pop();
      $('#well' + buttonId).css('border-color', '#dcdcdc');
      $('#alert' + buttonId).remove();
    });

  });

});
