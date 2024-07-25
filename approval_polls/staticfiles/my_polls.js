$(function () {
  var csrfSafeMethod = function (method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  };

  $('button[id^="delete-poll-"]').click(function (event) {
    disableAction(event.target, "Delete");
  });

  function disableAction(target, action) {
    var pollId = $(target).attr("id").split("-").pop();
    var alertDiv =
      "<div class='alert alert-danger' id='alert" +
      pollId +
      "'>" +
      "<p>This poll will be permanently deleted. " +
      "<button id='confirm-delete-" +
      pollId +
      "' type='button' class='btn btn-danger btn-xs'>Delete</button> " +
      "<button id='cancel-delete-" +
      pollId +
      "' type='button' class='btn btn-primary btn-xs'>Cancel</button>" +
      "</p></div>";

    if ($("#alert" + pollId).length == 0) {
      $("#poll-" + pollId).before(alertDiv);
    }

    $("#confirm-delete-" + pollId).click(function () {
      confirmAction(pollId);
    });

    $("#cancel-delete-" + pollId).click(function () {
      cancelAction(pollId);
    });
  }

  function confirmAction(pollId) {
    var csrfToken = $("#csrfmiddlewaretoken").val();
    console.info(csrfToken);
    $.ajax({
      method: "POST",
      url: "/" + pollId + "/delete/",
      headers: {
        "X-CSRFToken": csrfToken,
      },
      success: function (data) {
        if (data.status === "success") {
          $("#poll-" + pollId).remove();
          $("#alert" + pollId).remove();
        }
      },
      error: function (xhr, status, error) {
        console.error("Error deleting poll:", error);
        alert("An error occurred while deleting the poll.");
      },
    });
  }

  function cancelAction(pollId) {
    $("#alert" + pollId).remove();
  }
});
