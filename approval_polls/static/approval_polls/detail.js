$(function () {  

  var invitation_key, invitation_email;

  this.numChoiceFields = $('input:checkbox').length;

  this.addChoiceField = function () {
    var checkBox, input;

    this.numChoiceFields++;
    checkBox = $("<div class='checkbox'></div>");
    input = $("<label><input type='checkbox' name='choice" +
            this.numChoiceFields + "' id='choice" +
            this.numChoiceFields + "'>" + 
            "<input class='form-control' type='text' maxlength=200 name='choice" +
            this.numChoiceFields + "txt' placeholder='Choice " +
            this.numChoiceFields + "'></label>");

    checkBox.append(input);

    $('.checkbox').last().after(checkBox);
  };

  $('[data-toggle=tooltip]').tooltip();
  $('button#add-option').click($.proxy(this.addChoiceField, this));

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
