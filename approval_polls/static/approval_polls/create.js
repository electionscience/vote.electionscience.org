$(function () {
  this.numChoiceFields = 4;
  var changeDateLogic, roundMinutes, setDefaultOptions, changeDisabledOptions;

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

});
