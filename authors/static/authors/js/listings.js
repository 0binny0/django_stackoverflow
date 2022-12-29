

var user_search_query = document.getElementById("id_search");

function set_user_listing_api_request(obj) {
  let search;
  if (!obj.value || obj.value < 3) {
    search = "";
  } else {
    search = obj.value;
  }

  const api_url = document.location.toString().replace(/users\/$/gi, `api/v1/users?search=${search}`);
  const request = new Request(api_url, {
    'method': "get",
    'headers': {
      "Content-Type": "application/json",
      "Accept": "application/json"
    }
  });
  return request
}

function get_json_response(response) {
  debugger;
  if (response.ok) {
    return response.json().then((data) => {
      data['http_status'] = response.status;
      return data
    })
  }
  return {}
}

user_search_query.addEventListener("keyup", function(event) {
  const request = set_user_listing_api_request(this);
  fetch(request).then(get_json_response).then((data) => {
    let page_listing = document.querySelector(".users_list");
    if (!data) {
      let page_warning = document.createElement("h3");
      page_warning.textContent = `No users exist with the username ${this.value}`;
      page_listing.appendChild(page_warning);
    } else {
      let page_buttons = Array.from(document.getElementsByClassName("page_num"));
      page_buttons.forEach((page_button) => {
        page_button.href = `${document.location.href.replace(/(?<=users)\//ig,'')}?page=${page_button.textContent}&search=${this.value}`;
      })
      let paginated_buttons = document.querySelectorAll(`a[id*=paginated_page]`);
      paginated_buttons.forEach((button) => {
        button.href = `${button.href.replace(/(?<=users)\//ig,'')}&search=${this.value}`;
      });
      debugger;
      let users = data['users'];
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
            user_stat.textContent = `${posts} ${posts > 1 ? 'posts': 'post'}`;
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
