$(function () {
  var csrfSafeMethod;

  csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  };

  $('a[id^="delete-poll-"]').click(function (event) {
    disableAction(event.target, "Delete");
  });
  $('a[id^="suspend-poll-"]').click(function (event) {
    disableAction(event.target, "Suspend");
  });
  $('a[id^="unsuspend-poll-"]').click(function (event) {
    disableAction(event.target, "Unsuspend");
  });

  function disableAction(target, action) {
    _action = action.toLowerCase();
    var alertDiv, alertDivId;
    alertDivId = $(target).attr("id");
    alertDivId = alertDivId.split("-").pop();

    alertDiv =
      "<div class='alert alert-danger' id='alert" +
      alertDivId +
      "'>" +
      "<p>This poll will be " +
      verbalizeAction(_action) +
      "." +
      (action == "Suspend"
        ? "Suspending the poll will not allow any voting on it."
        : "") +
      " <button id='confirm-" +
      _action +
      "-" +
      alertDivId +
      "' type='button' class='btn btn-danger btn-xs'>" +
      action +
      "</button>" +
      " <button id='cancel-" +
      _action +
      "-" +
      alertDivId +
      "' type='button' class='btn btn-primary btn-xs'>Cancel</button>" +
      "</p></div>";

    if ($("#alert" + alertDivId).length == 0) {
      $(".well").css("border-color", "#dcdcdc");
      $(".alert").remove();
      $("#well" + alertDivId).before(alertDiv);
      $("#well" + alertDivId).css("border-color", "red");
    }

    function confirmAction() {
      var csrfToken, buttonId;
      buttonId = $(target).attr("id");
      buttonId = buttonId.split("-").pop();
      csrfToken = $("#csrfmiddlewaretoken").val();
      $("#well" + buttonId).css("border-color", "#dcdcdc");
      $("#alert" + buttonId).remove();
      if (action == "Delete") {
        $.ajax({
          method: "DELETE",
          url: "/approval_polls/" + buttonId + "/",
          beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
          },
          success: function (data) {
            $("#well" + buttonId).remove();
            window.location.reload();
          },
          error: function (data) {},
        });
      } else {
        $.ajax({
          method: "PUT",
          url: "/approval_polls/" + buttonId + "/change_suspension/",
          beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
          },
          success: function (data) {
            window.location.reload();
          },
        });
      }
    }
    $('button[id^="confirm-delete-"]').click(confirmAction);
    $('button[id^="confirm-suspend-"]').click(confirmAction);
    $('button[id^="confirm-unsuspend-"]').click(confirmAction);

    $('button[id^="cancel-delete-"]').click(cancelAction);
    $('button[id^="cancel-suspend-"]').click(cancelAction);
    $('button[id^="cancel-unsuspend-"]').click(cancelAction);
  }

  function cancelAction() {
    var buttonId;
    buttonId = $(this).attr("id");
    buttonId = buttonId.split("-").pop();
    $("#well" + buttonId).css("border-color", "#dcdcdc");
    $("#alert" + buttonId).remove();
  }

  function verbalizeAction(action) {
    switch (action) {
      case "delete":
        return "permanently deleted";
      case "unsuspend":
        return "unsuspended";
      case "suspend":
        return "suspended";
    }
  }
});
