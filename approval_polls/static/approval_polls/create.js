$(function () {
  this.numChoiceFields = 4;
  var changeDateLogic, roundMinutes, roundDate;

  /* Add an extra textfield for a poll choice on the poll creation page. */
  this.addChoiceField = function () {
    var formGroup, input;

    this.numChoiceFields++;
    formGroup = $("<div class='form-group'></div>");
    input = $("<input class='form-control' type='text' maxlength=200 name='choice" +
            this.numChoiceFields + "' placeholder='Choice " +
            this.numChoiceFields + "'>");

    formGroup.append(input);

    $('.form-group').last().after(formGroup);
  };

  $('[data-toggle=tooltip]').tooltip();
  $('button#add-choice').click($.proxy(this.addChoiceField, this));

  /* Allow user to select a poll closing date and time from a Jquery 
  DateTime picker. */

  roundMinutes = function( today ) {
    var hr, min, time;
    hr = today.getHours();
    min = today.getMinutes();
    if (min >= 0 && min < 30){
      min = 30;
    }
    else if (min >= 30 && min < 60){
      hr = hr + 1;
      min = 0;      
    }
    hr = ('0'+ hr).slice(-2);
    min = ('0'+ min).slice(-2);
    time = hr + ':' + min;
    return time;
  };

  roundDate = function ( today ) {
    var hr, min;
    hr = today.getHours();
    min = today.getMinutes();
    if (hr == 23  && min >= 30){
      today.setDate(today.getDate()+1);
    }
    return today;
  };

  changeDateLogic = function ( ct, $i ) {
    var today, ceilTime, ctHours, ctMinutes, ctTime;
    today = roundDate(new Date());
    ceilTime = roundMinutes(new Date());
    ctHours = ('0'+ ct.getHours()).slice(-2);
    ctMinutes = ('0'+ ct.getMinutes()).slice(-2)
    ctTime = ctHours + ':' + ctMinutes;
    ct = new Date(
      ct.getFullYear(),
      ct.getMonth(),
      ct.getDate()
      );
    today = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate()
      );
    if (ct.getTime() == today.getTime()){
      if (Date.parse('01/01/2000' + ' ' + ctTime) < Date.parse('01/01/2000' + ' ' + ceilTime)){
        $('#datetimepicker').val('');
      }
      $i.datetimepicker({
        defaultDate:today,
        minDate:today,
        defaultTime:ceilTime,
        minTime:ceilTime,
      });      
    }
    else if (ct.getTime() > today.getTime()){
      $i.datetimepicker({
        minTime:false,
      });
    }
    else if (ct.getTime() < today.getTime()){
      $('#datetimepicker').val('');
      $i.datetimepicker({
        defaultDate:false,
        minTime:'23:59',
      });
    }
  };

  $('#datetimepicker').datetimepicker({
    step:30,
    todayButton:false,
    defaultDate:roundDate(new Date()),
    minDate:roundDate(new Date()),
    defaultTime:roundMinutes(new Date()),
    minTime:roundMinutes(new Date()),
    onShow:changeDateLogic,
    onSelectDate:changeDateLogic,
    onChangeMonth:changeDateLogic,
  });

  $('#datetimepicker').keydown(function (e)
  {  
    if(e.keyCode == 8 || e.keyCode == 46) {
      $(this).val("");
      e.preventDefault();
    }
  });
});
