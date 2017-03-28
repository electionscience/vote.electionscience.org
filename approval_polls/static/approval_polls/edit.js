$(function(){
   /* Add an extra textfield for a poll choice on the poll creation page. */
  this.addChoiceField = function () {
    var formGroup, input;

    formGroup = $("<div class='form-group'></div>");
    input = $("<div class='input-group' id='div-choice" + this.numChoiceFields + "'><input class='form-control' type='text' maxlength=200 name='choice" +
            this.numChoiceFields + "' placeholder='Choice " +
            this.numChoiceFields + "'><span class='input-group-addon'>"+
            "<a href='#' class='add-link' id='link-choice" + this.numChoiceFields + "' title='Add link' data-toggle='tooltip' data-placement='bottom'>"+
            "<span class='glyphicon glyphicon-link'></span></a></span>" +
            "<span class='input-group-addon'>"+
            "<a href='#' class='remove-choice' id='remove-choice" + this.numChoiceFields + "' title='Remove Choice' >"+
            "<span class='glyphicon glyphicon-remove'></span></a></span>" +
            "<input type='hidden' id='linkurl-choice" + this.numChoiceFields + "' name='linkurl-choice" + this.numChoiceFields + "' value=''></div>");

    formGroup.append(input);

    $('.form-group').last().after(formGroup);
    $('[data-toggle=tooltip]').tooltip();
  };
});
