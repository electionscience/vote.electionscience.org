$(function () {
  var id_NewsLetter, id_ZipCode;

  id_NewsLetter = $('#id_newslettercheckbox');
  id_ZipCode = $('#id_zipcode');

  id_NewsLetter.change(function() {
  	if ($(this).prop('checked')) {
  	  id_ZipCode.prop('disabled', false);
  	}
  	else {
  	  id_ZipCode.prop('disabled', true).val('');
  	}
  });

  id_NewsLetter.change();

});