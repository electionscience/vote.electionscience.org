$(function () {
  // Social sharing
  $("#share").jsSocials({
    showLabel: false,
    showCount: false,
    shares: ["email", "twitter", "facebook", "linkedin", "pinterest"],
  });

  // Poll options
  const pollOptions = {
    container: $("#poll-options"),
    addButton: $("#add-option"),
    removeSelector: ".remove-choice",
  };

  let lastId = pollOptions.container.children().length;

  const addChoiceField = () => {
    lastId++;
    const newOption = `
      <div class="form-check mb-2 poll-option">
        <input class="form-check-input" type="checkbox" name="choice${lastId}" id="choice${lastId}">
        <label class="form-check-label" for="choice${lastId}">
          <div class="input-group">
            <input type="text" class="form-control" name="choice${lastId}txt" maxlength="200" placeholder="Choice ${lastId}">
            <button class="btn btn-outline-secondary add-link" type="button" title="Add link">
              <i class="bi bi-link"></i>
            </button>
          </div>
          <input type="hidden" id="linkurl-choice${lastId}" name="linkurl-choice${lastId}" value="">
        </label>
      </div>
    `;
    pollOptions.container.append(newOption);
  };

  pollOptions.addButton.on("click", addChoiceField);

  // Link handling
  pollOptions.container.on("click", ".add-link", function (e) {
    e.preventDefault();
    const choiceId = $(this)
      .closest(".form-check")
      .find('input[type="checkbox"]')
      .attr("id");
    const alertDiv = createAlertDiv(choiceId);
    $(this).closest(".form-check").before(alertDiv);
  });

  function createAlertDiv(choiceId) {
    return `
      <div class="alert alert-info" id="alert-${choiceId}">
        <input type="text" class="form-control mb-2" id="url-${choiceId}" placeholder="Link to URL">
        <button id="confirm-link-${choiceId}" type="button" class="btn btn-success btn-sm me-2">Insert Link</button>
        <button id="remove-link-${choiceId}" type="button" class="btn btn-danger btn-sm me-2">Reset Link</button>
        <button id="cancel-link-${choiceId}" type="button" class="btn btn-secondary btn-sm">Cancel</button>
      </div>
    `;
  }

  pollOptions.container.on("click", "[id^='confirm-link-']", function () {
    const choiceId = this.id.split("-").pop();
    const linkUrl = $(`#url-${choiceId}`).val().trim();
    if (validateUrl(linkUrl)) {
      $(`#linkurl-${choiceId}`).val(linkUrl);
      $(`#alert-${choiceId}`).remove();
      $(`#${choiceId}`)
        .closest(".form-check")
        .find(".add-link")
        .addClass("btn-success");
    } else {
      $(`#alert-${choiceId}`)
        .addClass("alert-danger")
        .removeClass("alert-info")
        .prepend('<p class="text-danger">Please enter a valid URL</p>');
    }
  });

  pollOptions.container.on("click", "[id^='remove-link-']", function () {
    const choiceId = this.id.split("-").pop();
    $(`#linkurl-${choiceId}`).val("");
    $(`#url-${choiceId}`).val("");
    $(`#alert-${choiceId}`).removeClass("alert-danger").addClass("alert-info");
    $(`#${choiceId}`)
      .closest(".form-check")
      .find(".add-link")
      .removeClass("btn-success");
  });

  pollOptions.container.on("click", "[id^='cancel-link-']", function () {
    const choiceId = this.id.split("-").pop();
    $(`#alert-${choiceId}`).remove();
  });

  function validateUrl(url) {
    const pattern =
      /^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})).?)(?::\d{2,5})?(?:[/?#]\S*)?$/i;
    return pattern.test(url);
  }

  // Countdown timer
  const timeDifference = $("#time_difference").val();
  if (timeDifference) {
    startCountdown(Math.ceil(timeDifference));
  }

  function startCountdown(duration) {
    const timer = $("#timer");
    const message = "before poll closes";

    function updateTimer() {
      const timeString = formatTime(duration);
      timer.html(`${timeString} ${message}`);

      if (--duration < 0) {
        clearInterval(interval);
        window.location.reload();
      }
    }

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
  }

  function formatTime(totalSeconds) {
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor(((totalSeconds % 86400) % 3600) / 60);
    const seconds = Math.floor(((totalSeconds % 86400) % 3600) % 60);
    return `${days}d:${padZero(hours)}h:${padZero(minutes)}m:${padZero(seconds)}s`;
  }

  function padZero(num) {
    return num.toString().padStart(2, "0");
  }
});
