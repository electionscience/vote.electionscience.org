$(function () {

  $('#id_newslettercheckbox').change(function() {
  	if ($(this).prop('checked')) {
  	  $('#id_zipcode').prop('disabled', false);
  	}
  	else {
  	  $('#id_zipcode').val('');
  	  $('#id_zipcode').prop('disabled', true);
  	}
  });

  $('#id_newslettercheckbox').change();

});