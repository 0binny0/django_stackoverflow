
let username_field = document.querySelector("#id_username");
let password_fields = Array.from(document.querySelectorAll(`input[id*=password]`));
let form_fields = [username_field, ...password_fields];

function create_api_request() {
  if (!this.value) {
    throw new Error();
  }
  const form = new FormData(this.form);
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
  const form = this.form.elements;
  form['button'].setAttribute("disabled", true);
  if (form['password2']) {
    const pass2_disabled = form['password2'].hasAttribute("disabled");
    if (pass2_disabled) {
      ['error_status', 'valid_status'].forEach((cls) => this.classList.remove(cls));
    } else {
      if (this.name === "username" || this.name === "password") {
        form['password2'].value = "";
        form['password2'].setAttribute("disabled", true);
        [this, form['password2']].forEach((field) => {
          field.classList.remove("valid_status");
          field.classList.remove("error_status");
        })
      } else {
        this.classList.remove("valid_status");
        this.classList.remove("error_status");
        form['password'].classList.remove("error_status");
        form['password'].classList.add("valid_status");
        if (form['username'].classList.contains("error_status") || form['password'].contains("error_status")) {
          this.setAttribute("disabled", true);
        }
      }
    }
  } else {
    this.classList.remove("valid_status");
    this.classList.remove("error_status");
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


form_fields.forEach((form_field) => {
  ['keyup', 'input'].forEach((user_action) => {
    form_field.addEventListener(user_action, function(event) {
      debugger;
      try {
        var api_request = create_api_request.call(this);
      } catch (error) {
          let form = handle_empty_form_field.call(this, event);
          return
      }
      fetch(api_request).then(api_response).then(
        (json) => {
          var form = this.form.elements;
          var json_keys = Object.keys(json.data);
          const response_200 = json.status;
          if (response_200) {
            if (json_keys.length === 3 && form['password2'] || json_keys.length === 2 & !form['password2']) {
              form['button'].removeAttribute("disabled");
            } else if (json_keys.length === 2 && form['password2']) {
              form['password2'].removeAttribute("disabled");
            }
            for (const name of json_keys) {
              const form_field = document.getElementById(`id_${name}`);
              form_field.classList.remove("error_status");
              form_field.classList.add("valid_status");
            }
          } else {
            form['button'].setAttribute("disabled", true);
            if (form['password2'] && !form['password2'].value && !form['password2'].hasAttribute("disabled")) {
              form['password2'].setAttribute("disabled", true);
            }
            for (const error of json_keys) {
              switch (true) {
                case error === "non_field_errors" && json.data[error][0] === "registration failed":
                  form_fields.forEach((form_field => {
                    form_field.classList.remove("valid_status");
                    form_field.classList.add("error_status");
                  }))
                  break;
                case error === "non_field_errors" && json.data[error][0] === "password confirmation failed":
                  if (!json_keys.includes("username")) {
                    username_field.classList.remove("error_status");
                    username_field.classList.add("valid_status");
                  }
                  password_fields.forEach((form_field => {
                    form_field.classList.remove("valid_status");
                    form_field.classList.add("error_status");
                  }))
                  break;
                case error === "non_field_errors" && json.data[error][0] === "password cannot be username":
                  [username_field, password_fields[0]].forEach((form_field) => {
                    form_field.classList.remove("valid_status");
                    form_field.classList.add("error_status");
                  })
                  const p2_disabled = password_fields.length === 2 && password_fields[-1].hasAttribute("disabled");
                  if (!p2_disabled) {
                    form['password2'].value = "";
                    form['password2'].setAttribute("disabled");
                    ['valid_status', 'error_status'].forEach((cls) => {
                      form['password2'].classList.remove(cls);
                    })
                  }
                  break;
                case error === "password":
                case error === "password2":
                  if (!json_keys.includes("username") && username_field.value) {
                    username_field.classList.remove("error_status");
                    username_field.classList.add("valid_status");
                  }
                  if (form['password2']) {
                    const [p1, p2] = password_fields;
                    const p2_disabled = p2.hasAttribute("disabled");
                    // password field error; no password2 field
                    if (p2_disabled) {
                      p1.classList.remove("valid_status");
                      p1.classList.add('error_status');
                    } else {
                      if (p1.value && p2.value) {
                        if (json_keys.includes("password") || json_keys.includes("password2")) {
                          password_fields.forEach((field) => {
                            field.classList.remove("valid_status");
                            field.classList.add("error_status");
                          })
                        }
                      }
                    }
                  }
                  if (!json_keys.includes('username') && username_field.value) {
                    username_field.classList.remove("error_status");
                    username_field.classList.add("valid_status");
                  }
                  break;
                case error === "username":
                  username_field.classList.remove("valid_status");
                  username_field.classList.add("error_status");
                  if (form['password2']) {
                    const [p1, p2] = password_fields;
                    const p2_disabled = p2.hasAttribute("disabled");
                    if (!p2_disabled) {
                      // verify password fields are equal
                      if (p1.value !== p2.value) {
                          password_fields.forEach((field) => {
                            field.classList.remove("valid_status");
                            field.classList.add("error_status");
                          })
                      } else {
                        password_fields.forEach((field) => {
                          field.classList.remove("error_status");
                          field.classList.add("valid_status");
                        })
                      }
                    } else {
                      if (!json_keys.includes("password") && p1.value) {
                        p1.classList.remove("error_status");
                        p1.classList.add("valid_status");
                      }
                    }
                  break;
              }
            }
          }
        }}
      )
    })
  })
})



































































































































//
// const username_field = document.getElementById("id_username");
// const password_fields = Array.from(document.querySelectorAll("input[id*=password]"));
// const form_fields = [username_field, ...password_fields];
// const submit_btn = document.querySelector("#account_submit_btn");
//
//
// document.addEventListener("DOMContentLoaded", (event) => {
//   password_fields[0].id = "id_password";
//   password_fields[0].name = "password";
// })
//
// function create_api_request() {
//   if (!this.value) {
//     throw new Error()
//   }
//   let form = new FormData(this.form);
//   for (const input_label of form.keys()) {
//     if (input_label === "csrfmiddlewaretoken" || form.get(input_label) === "") {
//       form.delete(input_label);
//     }
//   }
//   let query_string = new URLSearchParams(form);
//   let page_url = document.location;
//   if (page_url.pathname.includes("signup")) {
//     query_string.append("action", "register");
//   } else {
//     query_string.append("action", "login");
//   }
//   return new Request(
//     `http://localhost:8000/api/v1/users?${query_string}`, {
//       'headers': {
//         "Accept": "application/json"
//       }
//     }
//   );
// }
//
// function validate_empty_field(field, event) {
//   debugger;
//   const form = field.form.elements;
//   form['form_button'].setAttribute("disabled", true);
//   if (event.key === "Backspace" || event.key === "Delete") {
//     if (form['password2']) {
//       if (field.name === "username" || field.name === "password") {
//         if (form['password2'].value || !form['password2'].hasAttribute("disabled")) {
//           [field, form['password2']].forEach((field) => {
//             field.classList.remove("valid_status");
//             field.classList.remove("error_status");
//           })
//           form['password2'].setAttribute("disabled", true);
//           form['password2'].value = "";
//         }
//       } else {
//         field.classList.remove("valid_status");
//         field.classList.remove("error_status");
//       }
//     } else {
//       field.classList.remove("valid_status");
//       field.classList.remove("error_status");
//     }
//     return form
//   }
//   if (form['password2'] && field.name === "password2") {
//     const [min_len, max_len] = [
//       parseInt(form['password'].getAttribute("min_length")),
//       parseInt(form['password'].getAttribute("max_length"))
//     ];
//     if (form['password'].value && min_len <= form['password'].value.length <= max_len
//                                 && form['username'].value != form['password'].value) {
//                                     form['password'].classList.remove("error_status");
//                                     form['password'].classList.add("valid_status");
//                                     form['password2'].removeAttribute("disabled")
//                                 } else {
//                                   form['password2'].setAttribute("disabled", true);
//                                   ['valid_status', 'error_status'].forEach((cls) => form['password2'].classList.remove(cls));
//                                   form['password2'].value = "";
//                                 }
//
//   }
//   return form;
// }
//
// function json_response(response) {
//   return Promise.resolve(
//     response.json().then(
//       (data) => ({
//         'status_200': response.ok,
//         'data': data
//       })
//     )
//   )
// }
//
// function resolve_json(data) {
//   let [keys, values] = [[], []];
//   Array.from(Object.entries(data)).forEach((key_value_pair) => {
//     keys.push(key_value_pair[0]);
//     values.push(key_value_pair[1]);
//   })
//   return [keys, values];
// }
//
// form_fields.forEach((form_field) => {
//   ['keydown', 'keyup'].forEach((action) => {
//     form_field.addEventListener(action, function(event) {
//       debugger;
//       try {
//         var request = create_api_request.call(this);
//       } catch (error) {
//         var form = validate_empty_field(this, event);
//         return
//       }
//       fetch(request).then(json_response).then((json) => {
//         // debugger;
//         var form = this.form;
//         const [json_keys, json_values] = resolve_json(json.data)
//         // response sent with a 200 status code
//         if (json.status_200) {
//           for (const key of json_keys) {
//             const field = document.querySelector(`#id_${key}`);
//             field.classList.remove("error_status");
//             field.classList.add("valid_status");
//           }
//           if (
//             json_keys.length === 3 && form.name === "RegisterUserForm" ||
//             json_keys.length === 2 && form.name === "UserLoginForm") {
//               submit_btn.removeAttribute("disabled");
//           } else if (json_keys.length === 2 && form.name === "RegisterUserForm") {
//               form['password2'].removeAttribute("disabled");
//           }
//         // response sent with a 400 status code
//         } else {
//           var meets_username_len_constraint = (
//             parseInt(username_field.getAttribute("min_length")) <= username_field.value.length
//             <= parseInt(username_field.getAttribute("max_length"))
//           );
//           var meets_password_len_constraint = password_fields.every(
//             (field) => {
//               if (field.value.length) {
//                 let [min_len, max_len] = [
//                   parseInt(field.getAttribute('min_length')), parseInt(field.getAttribute('max_length'))
//                 ];
//                 return min_len <= field.value.length <= max_len
//               }
//             }
//           );
//           submit_btn.setAttribute("disabled", true)
//           for (let error of json_keys) {
//             switch (true) {
//               case error === "non_field_errors" && json.data[error][0] === "registration failed":
//                 form_fields.forEach((form_field) => {
//                   form_field.classList.remove("valid_status");
//                   form_field.classList.add("error_status");
//                 })
//                 break;
//               case error === "non_field_errors" && json.data[error][0] === "password cannot be username":
//                 [username_field, password_fields[0]].forEach((field) => {
//                   field.classList.remove("valid_status");
//                   field.classList.add("error_status");
//                 })
//                 break;
//               case error === "non_field_errors" && json.data[error][0] === "password confirmation failed":
//               case error === "password2":
//               case error === "password":
//                 const [password, password2] = password_fields;
//                 if (password2) {
//                   var p2_disabled = password2.hasAttribute("disabled");
//                 }
//                 password_fields.forEach((password_field, i) => {
//                   if (i === 1 && form['password2'] && p2_disabled) {
//                     return
//                   } else if (i === 1 && form['password2'] && !p2_disabled && !password2.value) {
//                     return
//                   }
//                   password_field.classList.remove("valid_status");
//                   password_field.classList.add("error_status");
//                 })
//                 if (meets_username_len_constraint && !json_keys.includes("username")) {
//                   username_field.classList.remove("error_status");
//                   username_field.classList.add("valid_status");
//                 }
//                 break;
//               case error === "username":
//                 username_field.classList.remove("valid_status");
//                 username_field.classList.add("error_status");
//                 if (meets_password_len_constraint) {
//                   if (form['password2']) {
//                     let [pass, pass2] = password_fields;
//                     if (!pass2.hasAttribute("disabled") && pass.value == pass2.value) {
//                       password_fields.forEach((field) => {
//                         field.classList.remove("error_status");
//                         field.classList.add("valid_status");
//                       })
//                     } else {
//                       password_fields.forEach((field) => {
//                         field.classList.remove("valid_status");
//                         field.classList.add("error_status");
//                       })
//                     }
//                   } else {
//                     password_fields[0].classList.remove("error_status");
//                     password_fields[0].classList.add("valid_status");
//                     passw
//                   }
//                 }
//                 break;
//             }
//           }
//         }
//       })
//     })
//   })
//
// })
