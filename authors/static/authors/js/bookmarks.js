
const csrftoken = Cookies.get('csrftoken');

let profile_bookmarks = document.querySelectorAll("polygon[id*=bookmark_question]");

profile_bookmarks.forEach(function(bookmark) {
  bookmark.addEventListener("click", function(event) {
    const bookmark_id = this.id.match(/([0-9]*$)/ig)[0];
    const api_url = `http://${document.location.host}/api/v1/bookmarks/${bookmark_id}/`;
    const active_bookmark = this.getAttribute("fill");
    let http_method;
    if (active_bookmark === "gold") {
      http_method = "delete";
    } else {
      http_method = "post"
    }
    const request = new Request(
      api_url, {
        'method': http_method,
        'headers': {
          'Accept': "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken
        }
      }
    );
    fetch(request).then((response) => {
      if (response.status === 204) {
        this.setAttribute("fill", "white");
        this.setAttribute("stroke", "black");
      } else {
        this.removeAttribute("stroke");
        this.setAttribute("fill", "gold");
      }
    })
  })
})
