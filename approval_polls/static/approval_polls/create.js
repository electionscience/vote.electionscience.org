var ap = ap || {};

ap.num_choice_fields = 8;

/* Add an extra textfield for a poll choice on the poll creation page. */
ap.addChoiceField = function () {
    ap.num_choice_fields += 1;

    var choice_list = document.getElementById("choice-list"),
        new_choice = document.createElement("li");

    new_choice.innerHTML = 'Choice ' +
        ap.num_choice_fields +
        ': <input type="text" maxlength="200" name="choice' +
        ap.num_choice_fields +
        '" size="24" />';

    choice_list.appendChild(new_choice);
};
