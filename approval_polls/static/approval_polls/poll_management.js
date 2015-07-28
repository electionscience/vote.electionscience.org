$(function () {
    var id = $(this).closest('div').attr('id');
  $('.show-alert').click(function() {
      $('#alert'+$(this).attr('id')).show();
  });
  
  $('.hide-alert').click(function() {
      $('#alert'+$(this).attr('id')).hide();
  });
  
  $('.delete-poll').click(function() {
	var id = $(this).attr('id');
	var csrf = $(this).attr('csrf');
	$('#poll'+id).remove();
    $.ajax({
      type: "POST",
      url: $(this).attr('onClick'),
      data: { pk : id,
              csrfmiddlewaretoken : csrf
      },
      success: function() {
        alert("Delete poll success!")
      },
      error:  function() {
        alert("Delete poll fail!")
      }
    });
  }); 
});

   