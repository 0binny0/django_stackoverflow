
const csrf_token = Cookies.get('csrftoken');
const user_posted_answers = document.querySelectorAll("li[id*=delete_answer]");
console.log(user_posted_answers);

function set_api_request(id) {
  const [method, post, post_id] = id.split("_");
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


user_posted_answers.forEach((answer) => {
  answer.addEventListener("click", function(event) {
    const request = set_api_request(this.id);
    fetch(request).then((response) => {
      if (response.ok) {
        const [post_type, id] = this.id.split("_").slice(1);
        const post = document.querySelector(`#posted_${post_type}_${id}`);
        const post_answer_tally = document.getElementById("question_answer_count");
        const answers = document.querySelector(".total_answers");
        const new_answer_post_count = parseInt(post_answer_tally.textContent) - 1;
        if (new_answer_post_count === 1) {
          answers.textContent = `${new_answer_post_count} answer`;
        } else {
          answers.textContent = `${new_answer_post_count} answers`;
        }

        post.remove();
      }
    })
  })
})


window.addEventListener("DOMContentLoaded", function(event) {
  const page_url = window.location.href;
  const page_num_pattern = /(?<=questions\/)\d+/;
  const page_id = page_url.match(page_num_pattern)[0];
  const request = new Request(
    `http://localhost:8000/api/v1/posts/${page_id}`, {
      'method': "GET",
      'Content-Type': "application/json",
      "Accept": "application/json",
      "X-CSRFToken": csrf_token
    }
  );
  fetch(request).then(
    (response) => response.json()
  ).then((json) => {
    if (json['posted']) {
      var posted_question = document.querySelector("li[id*=delete_question]");
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
              blocked_post.setAttribute("id", "post_temp_blocked");
              blocked_post.classList.add("temp_removed");
              blocked_post.style.cssText = `min-height: ${main_page_content_dims[0]}px; width: ${main_page_content_dims[1]}px;`;
              main_page_content.insertAdjacentElement('afterend', blocked_post);
              this.textContent = "Undelete";
              this.classList.add("undelete");
              let deleted_warning = document.createElement("p");
              deleted_warning.textContent = "This post is temporaily deleted. Click \"Undelete\" to display post."
              // deleted_warning.classList.add("temp_removed");
              blocked_post.appendChild(deleted_warning);
            } else {
              const blocked_post = document.getElementById("post_temp_blocked");
              blocked_post.parentElement.removeChild(blocked_post);
              this.classList.remove("undelete");
              this.textContent = "Delete";
            }
          }
        })
      })


      const active_post = json['visible'];
      if (!active_post) {
        const deleted_message = document.querySelector("#post_temp_blocked");
        const delete_status = document.querySelector("li[id*=delete_question]");
        delete_status.textContent = "Undelete";
        delete_status.classList.add("undelete");

        // const content_width = deleted_message.previousElementSibling.clientWidth;
        const content_height = deleted_message.previousElementSibling.clientHeight;
        console.log(content_height);
        deleted_message.style.cssText = `height: ${content_height}px;`;
      }
    }
  })
})

window.addEventListener("resize", function(event) {
  let main_content = document.querySelector(".main_topic");
  let delete_warning = main_content.nextElementSibling;
  delete_warning.style.cssText = `width: ${main_content.clientWidth}px; height: ${main_content.clientHeight}px`;
})
