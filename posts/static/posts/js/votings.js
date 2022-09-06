
var post_voting_buttons = Array.from(document.querySelectorAll("polygon"));

function json_response(response) {
  const content_type = response.headers.get("content-type");
  if (content_type === "application/json") {
    return response.json().then((json) => {
      if (json) {
        Object.defineProperty(json, 'status', {value: response.status});
      }
      return json
    })
  }
  return {'status': response.status}
}

function send_api_request(button) {
  var [vote_type, post, id] = button.id.split("_");
  const current_vote_buttons = Array.from(document.querySelectorAll(`polygon[id*=${post}_${id}]`));
  const csrftoken = Cookies.get('csrftoken');
  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-CSRFToken": csrftoken
  };
  var request_method;
  var user_voted = current_vote_buttons.find((button) => button.classList.contains("voted"));
  if (user_voted && user_voted === button) {
    request_method = "delete";
    // this.classList.replace("voted", "not_voted");
  } else if (user_voted && user_voted != button) {
    request_method = "put";
    // this.classList.replace("not_voted", "voted");
    // user_voted.classList.replace("voted", "not_voted");
  } else {
    request_method = "post";
    // this.classList.replace("not_voted", "voted");
  }
  var request = new Request(`http://localhost:8000/api/v1/votes/${id}/`, {
            'method': request_method,
            'headers': headers,
            'body': JSON.stringify({"type": vote_type, "post": post})
          });
  return request
}

//Returns the state of voting on a given question/answer
window.addEventListener("DOMContentLoaded", (e) => {
  var question_target = document.querySelector("h2[id*=question]");
  const id = question_target.id.split("_")[1];
  const request = fetch(`http://localhost:8000/api/v1/votes/${id}`, {
    'method': "GET"
  });
  debugger;
  request.then(json_response).then((json) => {
    console.log(json);
    const question_voted_on = document.querySelector(`svg > polygon[id=${json.vote}_question_${id}]`);
    if (question_voted_on) {
      question_voted_on.classList.add("voted");
    }
    let answers = json.answers;
    if (answers) {
      for (let obj of answers) {
        let answer_voted_on = document.querySelector(`svg > polygon[id=${obj.vote}_answer_${obj.id}]`);
        if (answer_voted_on) {
          answer_voted_on.classList.add("voted");
        }
      }
    }
  })
})

post_voting_buttons.forEach((button) => {
  button.addEventListener('mouseover', (event) => {
    const request = send_api_request(button);
    fetch(request).then(json_response).then(
      (json) => {

      }
    )
  })
})




post_voting_buttons.forEach((button) => {
  button.addEventListener("click", function(event) {
    const request = send_api_request(button);
    fetch(request).then(json_response).then(
      (json) => {
        let new_post_score;
        const target_post = button.id.match(/question_\d+|answer_\d+/)[0];
        const [post, id] = target_post.split("_");
        var all_post_voting_buttons = Array.from(document.querySelectorAll(`svg > polygon[id*=${target_post}]`));
        // var post_voting_buttons = Array.from(document.querySelectorAll(`svg > polygon[id*=${post}_${id}]`));
        var post_score = document.querySelector(`#${post}_${id}_score`);
        // Find whether a User has voted on the post
        // var request_method;
        // var user_voted = all_post_voting_buttons.find((button) => button.classList.contains("voted"));
        // if (user_voted && user_voted === this) {
        //   request_method = "delete";
        //   // this.classList.replace("voted", "not_voted");
        // } else if (user_voted && user_voted != this) {
        //   request_method = "put";
        //   // this.classList.replace("not_voted", "voted");
        //   // user_voted.classList.replace("voted", "not_voted");
        // } else {
        //   request_method = "post";
        //   // this.classList.replace("not_voted", "voted");
        // }
        switch(json.status) {
          case 201:
            this.classList.replace("not_voted", "voted");
            if (vote_type === "like") {
              new_post_score = `${parseInt(post_score.textContent) + 1}`
            } else {
              new_post_score = `${parseInt(post_score.textContent) - 1}`
            }
            post_score.textContent = new_post_score;
            break;
          case 204:
            const current_score = parseInt(post_score.textContent);
            if (request.method === "DELETE") {
              this.classList.replace("voted", "not_voted");
              if (vote_type === "like") {
                post_score.textContent = `${current_score - 1}`;
              } else {
                post_score.textContent = `${current_score + 1}`;
              }
            } else {
              this.classList.replace("not_voted", "voted");
              user_voted.classList.replace("voted", "not_voted");
              if (vote_type === "like") {
                new_post_score = `${current_score + 2}`
              } else {
                new_post_score = `${current_score - 2}`
              }
              post_score.textContent = new_post_score;
            }
            break;
          case 400:
              const vote_error_present = document.querySelector(".user_vote_error");
              if (!vote_error_present) {
                const user_vote_error = document.createElement("p");
                user_vote_error.setAttribute("class", "user_vote_error");
                user_vote_error.textContent = json['profile'];
                const question_title = document.querySelector(".question_title");
                question_title.insertAdjacentElement('beforebegin', user_vote_error);
              }
          }
      }
    )
  })
})

post_voting_buttons.forEach((button) => {
  button.addEventListener("mouseout", function(event) {
    const voting_error_message = document.querySelector(".user_vote_error");
    if (voting_error_message) {
      voting_error_message.parentElement.removeChild(voting_error_message);
    }
  })
})
