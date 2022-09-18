
let bookmark = document.querySelector("polygon[id*=bookmark]");
var csrftoken = Cookies.get("csrftoken");

bookmark.addEventListener("click", function(event) {
  let request_method;
  let bookmark = this.getAttribute("fill");
  if (bookmark === "white") {
    request_method = "post";
  } else {
    request_method = "delete";
  }
  const [post, id] = this.id.split("_");
  const request = new Request(
    `http://localhost:8000/api/v1/bookmarks/${id}/`, {
      'method': request_method,
      'headers': {
        "Content-Type": "application/json",
        "Accept": "application/json",
        'X-CSRFToken': csrftoken
      }
    }
  );
  fetch(request).then(response => {
    if (response.status === 201) {
      this.setAttribute("fill", "gold");
    } else {
      this.setAttribute("fill", "white");
    }
  })
})
