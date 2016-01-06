$(function () {
  this.numChoiceFields = 4;

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

  function roundMinutes(date) {
    if (date.getMinutes() > 0 && date.getMinutes() < 30){
      date.setHours(date.getHours());
      date.setMinutes(30);
    }
    else if (date.getMinutes() > 30 && date.getMinutes() < 60){
      date.setHours(date.getHours()+1);
      date.setMinutes(0);
    }
    return date;
  }

  var minDateTimelogic = function( currentDateTime ){
    this.setOptions({
      minDate: roundMinutes(currentDateTime),
      minTime: currentDateTime,
    });
  };

  $('#datetimepicker').datetimepicker({
    step:30,
    onShow:minDateTimelogic,
  });

  $("#datetimepicker").keyup(function (e)
  {
    if(e.keyCode == 8 || e.keyCode == 46) {
        $(this).val("");
    }
  });
});
