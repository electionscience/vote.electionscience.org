$(function () {
  const pollOptions = {
    container: $("#poll-options"),
    addButton: $("#add-choice"),
    removeSelector: ".remove-choice",
  };

  // Initialize lastId based on the number of existing options
  let lastId = pollOptions.container.children().length;

  const initializePollOptions = () => {
    pollOptions.container.on("click", pollOptions.removeSelector, function (e) {
      e.preventDefault();
      $(this).closest(".poll-option").remove();
      updateOptionNumbers();
    });

    pollOptions.addButton.on("click", addChoiceField);
  };

  const addChoiceField = () => {
    lastId++;
    const newOption = `
      <div class="mb-3 poll-option">
        <label for="choice${lastId}" class="form-label">Option ${lastId}</label>
        <div class="input-group">
          <input type="text" class="form-control" id="choice${lastId}" name="choice${lastId}" maxlength="100" placeholder="Option Name">
          <button class="btn btn-outline-primary remove-choice" type="button" title="Remove Choice">
            <i class="fa fa-times"></i>
          </button>
        </div>
      </div>
    `;
    pollOptions.container.append(newOption);
  };

  const updateOptionNumbers = () => {
    pollOptions.container.children(".poll-option").each(function (index) {
      const newIndex = index + 1;
      $(this).find("label").text(`Option ${newIndex}`);
      $(this)
        .find("input")
        .attr("id", `choice${newIndex}`)
        .attr("name", `choice${newIndex}`);
    });
    lastId = pollOptions.container.children().length;
  };

  const initializeTokenFields = () => {
    const allTags = $("#allTags").length ? $("#allTags").val().split(",") : [];

    emailValidation.tokenField
      .on("tokenfield:createtoken", tokenize)
      .on("tokenfield:createdtoken", validateEmailToken)
      .on("tokenfield:removedtoken", validateTokenField)
      .tokenfield();

    $("#tokenTagField")
      .on("tokenfield:createtoken", tokenize)
      .tokenfield()
      .tokenfield("setTokens", allTags);
  };

  const tokenize = (e) => {
    const data = e.attrs.value.split("|");
    e.attrs.value = data[1] || data[0];
    e.attrs.label = data[1] ? `${data[0]} (${data[1]})` : data[0];
  };

  const validateEmailToken = (e) => {
    const valid = emailValidation.regex.test(e.attrs.value);
    if (!valid) {
      $(e.relatedTarget).addClass("invalid");
    }
    validateTokenField();
  };

  const validateTokenField = () => {
    const existingTokens = emailValidation.tokenField.tokenfield("getTokens");
    const tokensValid = existingTokens.every((token) =>
      emailValidation.regex.test(token.value),
    );

    emailValidation.errorElement.toggle(
      !tokensValid && existingTokens.length > 0,
    );
  };

  const initializeEmailPollDisplay = () => {
    if ($("#poll-vtype").val() == 3) {
      emailPollDisplay();
    }

    $("input[name=radio-poll-type]:radio").on("click", function () {
      if ($(this).val() == 3) {
        emailPollDisplay();
      } else {
        $("#email-input, #existing-emails").hide();
        $("#poll-visibility").prop("checked", true);
      }
    });
  };

  const emailPollDisplay = () => {
    $("#email-input, #existing-emails").show();
    if ($("#poll-id").length === 0) {
      $("#poll-visibility").prop("checked", false);
    }
  };

  // Initialize everything
  initializePollOptions();
  initializeTokenFields();
  initializeEmailPollDisplay();
});
