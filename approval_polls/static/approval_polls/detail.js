$(function () {  

  var invitation_key, invitation_email;

  this.numChoiceFields = $('input:checkbox').length;

  this.addChoiceField = function () {
    var checkBox, input;

    this.numChoiceFields++;
    checkBox = $("<div class='checkbox'></div>");
    input = $("<label id='label-choice" + this.numChoiceFields + "'>" + 
            "<input type='checkbox' name='choice" +
            this.numChoiceFields + "' id='choice" +
            this.numChoiceFields + "'>" + 
            "<div class='input-group' id='div-choice" + this.numChoiceFields + "' style='width:auto'><input class='form-control' type='text' maxlength=200 name='choice" +
            this.numChoiceFields + "txt' placeholder='Choice " +
            this.numChoiceFields + "'><span class='input-group-addon' style='width:auto'>"+
            "<a href='#' id='link-choice" + this.numChoiceFields + "' title='Add link' data-toggle='tooltip' data-placement='bottom'>"+
            "<span class='glyphicon glyphicon-link'></span></a></span>" + 
            "<input type='hidden' id='linkurl-choice" + this.numChoiceFields + "' name='linkurl-choice" + this.numChoiceFields + "' value=''></div></label>");

    checkBox.append(input);

    $('.checkbox').last().after(checkBox);
    $('[data-toggle=tooltip]').tooltip();
  };

  $('[data-toggle=tooltip]').tooltip();
  $('button#add-option').click($.proxy(this.addChoiceField, this));

  /* Allow user to attach an external link to an option. */

  // Event delegation to capture dynamically added links
  $('.row-fluid').on('click', 'a', function() {
    var alertDiv, alertDivId, currentUrl;
    alertDivId = $(this).attr('id');
    alertDivId = alertDivId.split('-').pop();

    alertDiv = "<div class='alert alert-info' id='alert-" + alertDivId + "' style='width:60%'>" + 
      "<p><input type='text' class='form-control' id='url-" + alertDivId + "' placeholder='Link to URL' style='width:100%'></p><p>" + 
      "<button id='confirm-link-" + alertDivId + "' type='button' class='btn btn-success btn-xs'>Insert Link</button>" + 
      " <button id='remove-link-" + alertDivId + "' type='button' class='btn btn-danger btn-xs'>Reset Link</button>" + 
      " <button id='cancel-link-" + alertDivId + "' type='button' class='btn btn-info btn-xs'>Cancel</button></p></div>";

    if ($('#alert-' + alertDivId).length === 0) {
      // Remove all previous alerts
      $('.alert').remove();
      // Append the alert box before selected option
      $('#label-' + alertDivId).before(alertDiv);
      // Populate textbox with the last 'valid and inserted' URL
      currentUrl = $('#linkurl-' + alertDivId).val();
      $('#url-' + alertDivId).val(currentUrl);
    }

    $('button[id^="confirm-link-"]').click(function() {
      var buttonId, linkUrl, validUrl, urlPattern;
      buttonId = $(this).attr('id');
      buttonId = buttonId.split('-').pop();
      linkUrl = $('#url-' + buttonId).val();
      linkUrl = $.trim(linkUrl);
      // Check if URL begins with http or https or ftp
      // If not, prepend 'http://'
      urlPattern = new RegExp('^(http|https|ftp)://', 'i');
      if (!urlPattern.test(linkUrl)) {
        linkUrl = 'http://' + linkUrl;
      }
      // Source: https://github.com/jzaefferer/jquery-validation/blob/master/src/core.js
      validUrl = /^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})).?)(?::\d{2,5})?(?:[/?#]\S*)?$/i.test(linkUrl);
      if (!validUrl) {
        // If URL is not valid, change class of alert box
        $('#alert-' + buttonId).attr('class', 'alert alert-info has-error');
        // If URL is not valid, show an error message
        $('label[for="url-' + buttonId + '"]').remove();
        $('#alert-' + buttonId).prepend("<label class='control-label' for='url-" + alertDivId + "'>Please enter a valid URL</label>");
      }
      else {
        // Reset class of alert box
        $('#alert-' + buttonId).attr('class', 'alert alert-info');
        // Remove any error message
        $("label[for='url-" + buttonId + "']").remove();
        // Update value of hidden input field
        $('#linkurl-' + alertDivId).val(linkUrl);
        // Remove alert box
        $('#alert-' + buttonId).remove();
        // Change color of link to show a valid insertion
        $('#link-' + buttonId).attr('class','text-success');
      }
    });

    $('button[id^="cancel-link-"]').click(function() {
      var buttonId;
      buttonId = $(this).attr('id');
      buttonId = buttonId.split('-').pop();
      // Remove alert box
      $('#alert-' + buttonId).remove();
    });

    $('button[id^="remove-link-"]').click(function() {
      var buttonId;
      buttonId = $(this).attr('id');
      buttonId = buttonId.split('-').pop();
      // Reset value of hidden input field to empty string
      $('#linkurl-' + buttonId).val('');
      // Reset value of textbox
      $('#url-' + alertDivId).val('');
      // Reset class of alert box
      $('#alert-' + buttonId).attr('class', 'alert alert-info');
      // Remove any error message
      $("label[for='url-" + buttonId + "']").remove();
      // Reset color of link to show no current insertion
      $('#link-' + buttonId).removeAttr('class');
    });
    // To prevent navigation
    return false;
  });

  var convertSeconds, onZero, time_difference;

  convertSeconds = function (total_seconds) {
    var days, hours, minutes, seconds, currentTime;

    days = Math.floor(total_seconds / 86400);
    hours = Math.floor((total_seconds % 86400) / 3600);
    minutes = Math.floor(((total_seconds % 86400) % 3600) / 60);
    seconds = Math.floor(((total_seconds % 86400) % 3600) % 60);
    hours = ('0' + hours).slice(-2);
    minutes = ('0' + minutes).slice(-2);
    seconds = ('0' + seconds).slice(-2);
    currentTime = days + 'd:' + hours + 'h:' + minutes + 'm:' + seconds + 's';

    return currentTime;
  };

  $.fn.countdown = function (callback, duration) {
    var currentTimeString, container, countdown, message;

    message = 'before poll closes';
    currentTimeString = convertSeconds(duration);
    container = $(this[0]).html(currentTimeString + ' ' + message);

    countdown = setInterval(function () {
      if (--duration) {
        currentTimeString = convertSeconds(duration);
        container.html(currentTimeString + ' ' + message);
      }
      else {
        clearInterval(countdown);
        callback.call(container); 
      }
    }, 1000);
  };

  onZero = function () {
    window.location.reload();
  };

  time_difference = document.getElementById('time_difference').value;

  $('#timer').countdown(onZero, Math.ceil(time_difference));

});
