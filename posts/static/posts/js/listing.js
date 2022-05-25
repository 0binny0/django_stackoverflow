
let query_buttons = Array.from(document.querySelectorAll(".query_button"));
query_buttons.forEach((button) => {
  console.log(button.textContent)
})


document.addEventListener("DOMContentLoaded", function(event) {
  const url_query_string = new URLSearchParams(document.location.search);
  debugger;
  const page_tab_query = url_query_string.has("tab");
  if (!page_tab_query) {
    var sort_query = query_buttons[0].textContent.toLowerCase()
  } else {
    var sort_query = url_query_string.get("tab");
  }
  const query_types = query_buttons.map((query_button) => query_button.textContent.toLowerCase());
  if (!sort_query || !query_types.includes(sort_query)) {
    query_buttons[0].classList.add("active_query");
  } else {
    const button_index = query_buttons.findIndex(
      (query_button) => {
        return query_button.textContent.toLowerCase() === sort_query;
      }
    );
    const selected_query = query_buttons.splice(button_index, 1)[0];
    selected_query.classList.add("active_query");
    selected_query.setAttribute("id", "active")
    query_buttons.forEach((button) => {
      if (button.hasAttribute("id")) {
        button.removeAttribute("id");
      }
      button.classList.remove("active_query");
      button.style.cssText = "";
    })
  }
})
