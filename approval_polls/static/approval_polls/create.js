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
});
