(function () {
  var numChoiceFields, addChoiceField, init;

  numChoiceFields = 8;

  /* Add an extra textfield for a poll choice on the poll creation page. */
  addChoiceField = function () {
    var choice_list, new_choice;

    choice_list = document.getElementById('choice-list');
    new_choice = document.createElement('li');

    numChoiceFields++;

    new_choice.innerHTML = 'Choice ' + numChoiceFields +
                           ': <input type=text maxlength=200 name=choice' +
                           numChoiceFields + ' size=24>';

    choice_list.appendChild(new_choice);
  };

  init = function () {
    var elt;

    elt = document.getElementById('add-choice-button');
    elt.addEventListener('click', addChoiceField);
  };

  addEventListener('load', init);
}());
