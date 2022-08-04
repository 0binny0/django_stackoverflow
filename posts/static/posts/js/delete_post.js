
const csrf_token = Cookies.get('csrftoken');
const posted_question = document.querySelector("li[id*=delete_question]");

function set_api_request(id) {
  const [method, post, post_id] = id.split("_");
  debugger;
  const request = new Request(
    `http://localhost:8000/api/v1/posts/${post_id}?post=${post}`, {
      'method': 'PUT',
      'headers': {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-CSRFToken': csrf_token
      }
    }
  );
  return request
}

function show_deleted_post_message() {
  const main_page_content = document.querySelector(".main_topic");
  const post_status = document.querySelector("li[id]")
  const main_page_content_dims = [
    main_page_content.clientHeight, main_page_content.clientWidth
  ];
  const blocked_post = document.createElement("div");
  blocked_post.style.height = main_page_content_dims[0];
  blocked_post.style.width = `490px`;
  blocked_post.setAttribute("id", "post_temp_blocked")
  blocked_post.classList.add("temp_removed")
  let deleted_warning = document.createElement("p");
  deleted_warning.textContent = "This post is temporaily deleted. Click \"Undelete\" to display post."
  blocked_post.appendChild(deleted_warning);
  return [main_page_content, blocked_post]
}

window.addEventListener("load", function(event) {
  const page_url = window.location;

  const request = new Request(
    "http://localhost:8000/api/v1/posts/62", {
      'method': "GET",
      'Content-Type': "application/json",
      "Accept": "application/json",
      "X-CSRFToken": csrf_token
    }
  );
  fetch(request).then(
    (response) => response.json()
  ).then((json) => {
    const temp_deleted = json['visible'];
    if (temp_deleted) {
      debugger;
      const [main_page_content, blocked_post] = show_deleted_post_message();
      main_page_content.parentElement.appendChild(blocked_post);

      const delete_status = document.querySelector("li[id*=delete_question]");
      delete_status.textContent = "Undelete";
      delete_status.classList.add("undelete");
    }
  })
})

posted_question.addEventListener("click", function(event) {
  const request = set_api_request(this.id);
  fetch(request).then((response) => {
    if (response.status === 204) {
      if (this.textContent === "Delete") {
        const main_page_content = document.querySelector(".main_topic");
        const main_page_content_dims = [
          main_page_content.clientHeight, main_page_content.clientWidth
        ];
        const blocked_post = document.createElement("div");
        blocked_post.style.height = main_page_content_dims[0];
        blocked_post.style.width = `490px`;
        blocked_post.setAttribute("id", "post_temp_blocked")
        blocked_post.classList.add("temp_removed")
        let deleted_warning = document.createElement("p");
        deleted_warning.textContent = "This post is temporaily deleted. Click \"Undelete\" to display post."
        blocked_post.appendChild(deleted_warning);
        main_page_content.parentElement.appendChild(blocked_post)
        this.textContent = "Undelete";
        this.classList.add("undelete");
      } else {
        const blocked_post = document.getElementById("post_temp_blocked");
        blocked_post.parentElement.removeChild(blocked_post);
        this.classList.remove("undelete");
        this.textContent = "Delete";
      }
    }
  })
})
