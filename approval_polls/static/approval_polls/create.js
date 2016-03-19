$(function () {
  this.numChoiceFields = 4;
  var changeDateLogic, roundMinutes, setDefaultOptions, changeDisabledOptions;
  var validateTokenField;

  /* Add an extra textfield for a poll choice on the poll creation page. */
  this.addChoiceField = function () {
    var formGroup, input;

    this.numChoiceFields++;
    formGroup = $("<div class='form-group'></div>");
    input = $("<div class='input-group' id='div-choice" + this.numChoiceFields + "'><input class='form-control' type='text' maxlength=200 name='choice" +
            this.numChoiceFields + "' placeholder='Choice " +
            this.numChoiceFields + "'><span class='input-group-addon'>"+
            "<a href='#' id='link-choice" + this.numChoiceFields + "' title='Add link' data-toggle='tooltip' data-placement='bottom'>"+
            "<span class='glyphicon glyphicon-link'></span></a></span>" + 
            "<input type='hidden' id='linkurl-choice" + this.numChoiceFields + "' name='linkurl-choice" + this.numChoiceFields + "' value=''></div>");

    formGroup.append(input);

    $('.form-group').last().after(formGroup);
    $('[data-toggle=tooltip]').tooltip();
  };

  $('[data-toggle=tooltip]').tooltip();
  $('button#add-choice').click($.proxy(this.addChoiceField, this));
  
  /* Allow user to attach an external link to an option. */

  // Event delegation to capture dynamically added links
  $('.row-fluid').on('click', 'a', function() {
    var alertDiv, alertDivId, currentUrl;
    alertDivId = $(this).attr('id');
    alertDivId = alertDivId.split('-').pop();

    alertDiv = "<div class='alert alert-info' id='alert-" + alertDivId + "'>" + 
      "<p><input type='text' class='form-control' id='url-" + alertDivId + "' placeholder='Link to URL'></p><p>" + 
      "<button id='confirm-link-" + alertDivId + "' type='button' class='btn btn-success btn-xs'>Insert Link</button>" + 
      " <button id='remove-link-" + alertDivId + "' type='button' class='btn btn-danger btn-xs'>Reset Link</button>" + 
      " <button id='cancel-link-" + alertDivId + "' type='button' class='btn btn-info btn-xs'>Cancel</button></p></div>";

    if ($('#alert-' + alertDivId).length === 0) {
      // Remove all previous alerts
      $('.alert').remove();
      // Append the alert box before selected option
      $('#div-' + alertDivId).before(alertDiv);
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

  /* Allow user to select a poll closing date and time from a Jquery 
  DateTime picker. */

  roundMinutes = function ( today ) {
    var hr, min, time;    
    min = today.getMinutes();
    if (min >= 0 && min < 30){
      today.setMinutes(30);
    }
    else if (min >= 30 && min < 60){
      today.setHours(today.getHours() + 1);
      today.setMinutes(0);
    }
    hr = ('0' + today.getHours()).slice(-2);
    min = ('0'+ today.getMinutes()).slice(-2);
    time = hr + ':' + min;
    return [time, today];
  };

  setDefaultOptions = function () {
    var options, roundDateTime, roundDate, roundTime;
    options = {};
    roundDateTime = roundMinutes(new Date());
    roundTime = roundDateTime[0];
    roundDate = roundDateTime[1];
    options['defaultDate'] = roundDate;
    options['minDate'] = roundDate;
    options['defaultTime'] = roundTime;
    options['minTime'] = roundTime;
    return options;
  };

  changeDateLogic = function ( ct, $i ) {
    var selected, current, roundDate;
    roundDate = roundMinutes(new Date())[1];
    selected = new Date(ct.dateFormat('Y/m/d'));
    current = new Date(roundDate.dateFormat('Y/m/d'));
    if (selected.getTime() == current.getTime()){
      if (ct.dateFormat('H:i') < roundDate.dateFormat('H:i')){
        $('#datetimepicker').val('');
      }
      $i.datetimepicker(setDefaultOptions());
    }
    else if (selected.getTime() > current.getTime()){
      $i.datetimepicker({
        minTime:false,
      });
    }
    else if (selected.getTime() < current.getTime()){
      $('#datetimepicker').val('');
      $i.datetimepicker({
        defaultDate:false,
        minTime:'23:59',
      });
    }
    $('#datetimepicker').change();
  };

  $('#datetimepicker').datetimepicker(setDefaultOptions());

  $('#datetimepicker').datetimepicker({
    step:30,
    todayButton:false,
    onShow:changeDateLogic,
    onSelectDate:changeDateLogic,
    onChangeMonth:changeDateLogic,
  });

  $('#datetimepicker').keydown(function (e)
  {  
    if(e.keyCode == 8 || e.keyCode == 46) {
      $(this).val('');
      $(this).change();
      e.preventDefault();
    }
  });

  changeDisabledOptions = function () {
    if ($('#datetimepicker').val() == ''){
      $('#checkbox1').attr('disabled', true); 
      $('#checkbox2').attr('disabled', true);
    }
    else{
      $('#checkbox1').prop('disabled', false);
      $('#checkbox2').prop('disabled', false);
    }
  };

  $('#datetimepicker').change(function () {
    changeDisabledOptions();
  });

  $('#datetimepicker').change();


  /* Validate the token field for the email list. */
  validateTokenField = function() {
    var re = /\S+@\S+\.\S+/;
    var existingTokens;
    var tokensValid = true;
    existingTokens = $('#tokenEmailField').tokenfield('getTokens');

    if (existingTokens.length === 0) {
      $('#email-error').hide();
    }
    else {
      $.each(existingTokens, function(index, token) {
          if (!re.test(token.value)) {
            tokensValid = false;
          }  
      });
      if (tokensValid) {
        $('#email-error').hide();
      }
      else {
        $('#email-error').show();
      }
    }
  };
  $('#tokenEmailField')
    .on('tokenfield:createtoken', function (e) {
    var data = e.attrs.value.split('|');
    e.attrs.value = data[1] || data[0];
    e.attrs.label = data[1] ? data[0] + ' (' + data[1] + ')' : data[0];
  })
  .on('tokenfield:createdtoken', function (e) {
    // Simple E-mail validation
    var re = /\S+@\S+\.\S+/;
    var valid = re.test(e.attrs.value);
    if (!valid) {
      $(e.relatedTarget).addClass('invalid');
    }
    validateTokenField();
  })
  .on('tokenfield:removedtoken', function (e) {
    validateTokenField();
  })
  .tokenfield();

  // Toggle the visibility of the email input 
  $('input[name=radio-poll-type]:radio').click(function() {
    if ($(this).attr('value') == 3) {
      $('#email-input').show();
      $('#poll-visibility').prop('checked', false);
    }
    else {
      $('#email-input').hide();
      $('#poll-visibility').prop('checked', true);
    }
  });
});
