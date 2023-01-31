

var user_search_query = document.getElementById("id_search");
user_search_query.removeAttribute("required");
let form = document.querySelector("#api_user_search_form");

function set_user_listing_api_request(obj) {
  let search;
  if (!obj.value || obj.value < 3) {
    search = "";
  } else {
    search = obj.value;
  }

  const api_url = document.location.toString().replace(/users.*$/gi, `api/v1/users?search=${search}`);
  const request = new Request(api_url, {
    'method': "get",
    'headers': {
      "Content-Type": "application/json",
      "Accept": "application/json"
    }
  });
  return request
}

form.addEventListener("submit", function(event) {
  event.preventDefault()
})

window.addEventListener("DOMContentLoaded", function(event) {
  const url_query_params = (new URL(document.location)).searchParams;

  if (url_query_params.has("search")) {
    user_search_query.value = url_query_params.get("search");
  }
})

function get_json_response(response) {
  if (response.ok) {
    return response.json().then((data) => {
      data['http_status'] = response.status;
      return data
    })
  }
  return {}
}


user_search_query.addEventListener("keyup", function(event) {
  let page_warning_exists = document.querySelector("#no_users_warning");
  let page_listing = document.querySelector(".users_list");
  const pagination = document.querySelector(".main_pagination");
  const request = set_user_listing_api_request(this);
  fetch(request).then(get_json_response).then((data) => {
    let users = data['users'];
    let users_count = users !== undefined ? Object.keys(users).length : 0;
    if (users_count === 0) {
      const message = `No users exist with the username ${this.value}`;
      if (page_listing) {
        let page_warning = document.createElement("h3");
        page_warning.setAttribute("id", "no_users_warning");
        page_warning.style.cssText = `margin-top: 20px; text-align: center; border: 2px solid; padding: 10px; width: 500px; word-break: break-all;`;
        page_warning.textContent = message
        page_listing.replaceChildren(page_warning);
      }
      else {
        page_warning_exists = message
      }
      pagination.classList.add("hide");
    } else {
      pagination.classList.remove("hide");
      users = users.slice(0, 15);
      let active_page_nav_button_count = Math.ceil(users_count / 15);
      let paginated_buttons = Array.from(document.querySelectorAll(`a[id*=paginated]`));
      let numbered_page_buttons = Array.from(
        document.getElementsByClassName("page_num")
      );
      const navigation_buttons = [...numbered_page_buttons, ...paginated_buttons];
      const next_button_exists = navigation_buttons.find((button) => button.textContent === "Next");
      if (next_button_exists === undefined) {
        const next_button = document.createElement("a");
        next_button.id = "paginated_page_next";
        next_button.textContent = "Next";
        next_button.classList.add("inactive_page");
        navigation_buttons.push(next_button);
      }
      if (this.value) {
        navigation_buttons.forEach((page_button, index, array, user_search_query) => {
          let paginated_link;
          const button_label = page_button.textContent;
          if (button_label !== "Prev" && button_label !== "Next") {
            const page_num = index + 1;
            if (page_num > 5) {
              page_button.style.display = "none";
            } else {
              page_button.textContent = `${page_num}`;
              paginated_link = document.location.href.replace(/(?<=users)\/?.*/ig,`?page=${page_num}&search=${this.value}`);
              page_button.href = paginated_link;
              if (page_num === 1) {
                page_button.style.cssText = "background: darkorange; color: white; border: 1px solid darkorange";
              } else {
                page_button.style.cssText = "background: white; color: black; border: 1px solid lightgrey";
              }
              if (page_num > active_page_nav_button_count) {
                page_button.style.display = "none";
              } else {
                page_button.style.display = "inline-block";
              }
            }
          } else if (button_label === "Next") {
            if (active_page_nav_button_count > 1) {
              paginated_link = document.location.href.replace(/(?<=users)\/?.*/ig,`?page=2&search=${this.value}`);
              page_button.href = paginated_link;
              page_button.classList.remove("hide")
            } else {
              page_button.classList.add("hide");
            }

          } else {
            if (button_label === "Prev") {
              page_button.classList.add("hide");
            } else if (button_label === "Next") {
              page_button.classList.remove("hide");
            } else {
              if (button_label === "1") {
                page_button.style.cssText = `background: darkorange; color: white; border: 1px solid darkorange`;
              } else {
                page_button.style.cssText = `background: white; color: black; border: 1px solid lightgrey`;
              }
            }
          }
        })
      } else {
        navigation_buttons.forEach((page_button, index, array, user_search_query) => {
          let paginated_link;
          const button_label = page_button.textContent;
          if (button_label === "Prev") {
            page_button.style.display = "none";
          } else if (button_label !== "Next") {
            const page_num = index + 1;
            if (page_num > 5) {
              page_button.style.display = "none";
            } else {
              page_button.textContent = `${page_num}`;
              paginated_link = document.location.href.replace(/(?<=users)\/?.*/ig,`?page=${page_num}`);
              page_button.href = paginated_link;
              if (page_num === 1) {
                page_button.style.cssText = "background: darkorange; color: white; border: 1px solid darkorange; visibility: visible";
              } else {
                page_button.style.cssText = "background: white; color: black; border: 1px solid lightgrey; visibility: visible";
              }
            }
          } else {
            if (active_page_nav_button_count === 1) {
              page_button.classList.add("hide");
            } else {
              let navigation_wrapper = document.querySelector(".page_through_wrapper");
              const paginated_link = document.location.href.replace(/(?<=users)\/?.*/ig,`?page=2`);
              page_button.href = paginated_link;
              page_button.classList.remove("hide");
              navigation_wrapper.appendChild(page_button);
            }
          }
        })
      }
      let new_displayed_users = [];
      for (let user of users) {
        let user_div_wrapper = document.createElement("div");
        user_div_wrapper.setAttribute('class', "user_listing_data");
        const username = document.createElement("p");
        const link = document.createElement("a");
        link.setAttribute("href", `${document.location.href.replace(/\/users.*/i, user['profile']['url'])}`);
        delete user['profile']['url'];
        link.textContent = user.name;
        username.appendChild(link);
        user_div_wrapper.appendChild(username);
        for (let key in user['profile']) {
          let user_stat = document.createElement("p");
          user_stat.setAttribute("class", "user_subdata");
          if (key === "total_posts") {
            const posts = user['profile'][key];
            user_stat.textContent = `${posts} ${posts > 1 ? 'Posts': 'Post'}`;
          } else {
            const user_key = `${key.replaceAll(
              /(_|^)[a-z]/ig, (match) => {
                return match.toUpperCase().replace("_", " ")
              }
            )}`;

            user_stat.textContent = `${user_key}: ${user['profile'][key]}`;
          }
          user_div_wrapper.appendChild(user_stat);
        new_displayed_users.push(user_div_wrapper);
        }
      }
      page_listing.replaceChildren(...new_displayed_users);
    }
  })
})


user_search_query.addEventListener("focus", function(event) {
  this.style.cssText = "box-shadow: 0px 0px 2px 3px lightblue; border: 1px solid blue";
})

user_search_query.addEventListener("blur", function(event) {
  this.style.cssText = "box-shadow: none; border: 1px solid lightgrey";
})
