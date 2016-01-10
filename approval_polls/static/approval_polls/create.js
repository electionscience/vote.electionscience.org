$(function () {
  this.numChoiceFields = 4;
  var changeDateLogic;

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
  
  changeDateLogic = function ( ct, $i ) {
    var ct, today;
    ct = new Date(
      ct.getFullYear(),
      ct.getMonth(),
      ct.getDate()
      );
    today = new Date();
    today = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate()
      );
    if ( ct.getTime() == today.getTime() ) {
      $i.datetimepicker({ 
        minTime:new Date(),
      });
    }
    else if ( ct.getTime() > today.getTime() ) {
      $i.datetimepicker({
        minTime:false,
      });
    }
    else if ( ct.getTime() < today.getTime() ) {
      $i.datetimepicker({
        minTime:'23:59',
      });
    }
  };

  $('#datetimepicker').datetimepicker({
    step:30,
    roundTime:'ceil',
    todayButton:false,
    minDate:new Date(),
    minTime:new Date(),
    onChangeMonth:changeDateLogic,
    onSelectDate:changeDateLogic,
    onShow:changeDateLogic,
  });

  $('#datetimepicker').keydown(function (e)
  {  
    if(e.keyCode == 8 || e.keyCode == 46) {
      $(this).val("");
      e.preventDefault();
    }
  });
});
