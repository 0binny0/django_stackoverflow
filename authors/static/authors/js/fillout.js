
let username_field = document.querySelector("#id_username");
let password_fields = Array.from(document.querySelectorAll(`input[id*=password]`));
let form_fields = [username_field, ...password_fields];
let form = document.querySelector("form[name*=UserForm]");

window.addEventListener("DOMContentLoaded", function(event) {
  let password_field = document.getElementById("id_password1");
  if (password_field) {
    password_field.id = "id_password";
  } else {
    password_field = document.getElementById("id_password");
  }
  password_field.form['button'].setAttribute("disabled", true);
})


function create_api_request(event) {
  if (!event.target.value) {
    return
  }
  const form = new FormData(this);
  for (const key of form.keys()) {
    if (key === "csrfmiddlewaretoken" || !form.get(key)) {
      form.delete(key);
    } else if (key === "password1") {
      const password_value = form.get(key);
      form.delete(key);
      form.append("password", password_value)
    }
  }
  const query_string = new URLSearchParams(form);
  const page_url_path = window.location.pathname;
  if (page_url_path === "/users/signup/") {
    query_string.append("action", "register");
  } else {
    query_string.append("action", "login")
  }
  const api_url = `http://localhost:8000/api/v1/users?${query_string}`;
  return new Request(api_url, {
    'headers': {
      'Accept': "application/json"
    }
  });
}

function handle_empty_form_field(event) {
  const field = event.target;
  const form = event.target.form;
  form['button'].setAttribute("disabled", true);
  if (form['password2']) {
    const pass2_disabled = form['password2'].hasAttribute("disabled");
    if (pass2_disabled) {
      field.classList.remove("error_status");
      password_fields.forEach((field) => {
        ['error_status', 'valid_status'].forEach((cls) => field.classList.remove(cls));
      })
    } else {
      if (field.name === "username" || field.name === "password1") {
        form['password2'].value = "";
        form['password2'].setAttribute("disabled", true);
        [field, form['password2']].forEach((field) => {
          field.classList.remove("valid_status");
          field.classList.remove("error_status");
        })
      } else {
        field.classList.remove("valid_status");
        field.classList.remove("error_status");
        form['password1'].classList.remove("error_status");
        form['password1'].classList.add("valid_status");
        if (form['username'].classList.contains("error_status") || form['password1'].classList.contains("error_status")) {
          field.setAttribute("disabled", true);
        }
      }
    }
  } else {
    field.classList.remove("valid_status");
    field.classList.remove("error_status");
  }
  return form
}

function api_response(response) {
  return Promise.resolve(
    response.json().then((data) => ({
      'status': response.ok,
      'data': data
    }))
  )
}


form.addEventListener("input", function(event) {
  const submitted_form = this;
  var api_request = create_api_request.call(submitted_form, event);
  if (api_request === undefined) {
    let form = handle_empty_form_field(event)
    return
  }
  fetch(api_request).then(api_response).then((json) => {
    const validated_response = json.status;
    const response_data = json.data;
    if (validated_response) {
      for (let key in response_data) {
        const form_field = this[`id_${key}`];
        form_field.classList.remove("error_status");
        form_field.classList.add("valid_status");
      }
      const field_inputs = Array.from(form.elements).filter((field) => field.nodeName === "INPUT" && field.type !== "hidden");
      const validated_form = field_inputs.every((field) => {
        return field.classList.contains("valid_status")
      });
      if (validated_form && (field_inputs.length === 3 || field_inputs.length === 2)) {
        form['button'].removeAttribute("disabled");
      } else {
        const validated_fields = Object.keys(response_data).length;
        if (validated_fields === 2) {
          form['id_password2'].removeAttribute("disabled");
        }
      }
      return
    } else {
      this['button'].setAttribute("disabled", true);
      var form_elements = Array.from(this.elements).filter((field) => !field.hidden);
      for (let error in response_data) {
        switch (true) {
          case error === "non_field_errors" && response_data[error][0] === "registration failed":
            form_fields.forEach((field) => {
              field.classList.remove("valid_status");
              field.classList.add("error_status");
            })
            break;
          case error === "non_field_errors" && response_data[error][0] === "password confirmation failed":
            const username_field_has_error = username_field.classList.contains("valid_status");
            if (!username_field_has_error) {
              this['id_username'].classList.remove("error_status");
              this['id_username'].classList.add("valid_status");
            }
            password_fields.forEach((field) => {
              field.classList.remove("valid_status");
              field.classList.add("error_status");
            })
            break;
          case error === "non_field_errors" && response_data[error][0] === "password cannot be username":
            const password_field = this["id_password"];
            [username_field, password_field].forEach((field) => {
              let active_field_error = field.classList.contains("error_status");
              if (!active_field_error) {
                field.classList.remove("valid_status");
                field.classList.add("error_status");
              }
            })
            if (form_fields.length === 3) {
              let confirmation_field = this['id_password2'];
              if (!confirmation_field.hasAttribute("disabled")) {
                confirmation_field.value = "";
                ['valid_status', 'error_status'].forEach((css_rule) => {
                  confirmation_field.classList.remove(css_rule);
                });
                confirmation_field.setAttribute("disabled", true);
              }
            }
            break;
          case error === "username":
            let active_error = username_field.classList.contains("error_status");
            if (!active_error) {
              username_field.classList.remove("valid_status");
              username_field.classList.add("error_status");
            }
            if (form_fields.length == 3) {
              let [password_field, confirmation_field] = password_fields;
              const confirmation_disabled = confirmation_field.hasAttribute("disabled");
              if (!confirmation_disabled) {
                const password_min = password_field.getAttribute("min_length");
                const password_max = password_field.getAttribute("max_length");
                if (password_field.value === confirmation_field.value && password_min <= password_field.value.length <= password_max) {
                  password_fields.forEach((field) => {
                    field.classList.remove("error_status");
                    field.classList.add("valid_status");
                  })
                } else {
                  password_fields.forEach((field) => {
                    field.classList.remove("valid_status");
                    field.classList.add("error_status");
                  })
                }
              }
            }
            break;
          case error === "password":
            let word_field = password_fields[0];
            word_field.classList.remove("valid_status");
            word_field.classList.add("error_status");
            if (form_fields.length === 3) {
              let confirmation_field = this['id_password2'];
              if (!confirmation_field.hasAttribute("disabled")) {
                  if (confirmation_field.value) {
                    confirmation_field.classList.remove("valid_status");
                    confirmation_field.classList.add("error_status");
                  } else {
                    confirmation_field.setAttribute("disabled", true);
                  }
              }
            }
            break;
          case error === "password2":
            let confirmation = password_fields.at(-1);
            let field_has_error = confirmation.classList.contains("error_status");
            if (!field_has_error) {
              confirmation.classList.add("error_status");
            }
            const username_min = username_field.getAttribute("minlength");
            const username_max = username_field.getAttribute("maxlength");
            if (username_min <= username_field.value.length <= username_max) {
              username_field.classList.remove("error_status");
              username_field.classList.add("valid_status");
            }
        }
      }
    }
  })
})
