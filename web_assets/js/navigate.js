

var search_widget = document.getElementById("id_q");
var search_icon = document.getElementById("search_icon");
var page_footer = document.querySelector(".page_footer");
console.log(search_icon);

window.addEventListener("load", function(event) {
  if (page_footer) {
    const page_footer_box_height = page_footer.getBoundingClientRect().height;
    page_footer.style.height = `${page_footer_box_height + 75}px`;
  }
})

search_widget.addEventListener("focus", function(event) {
  const search_tips = document.querySelector(".query_help_tips");
  search_tips.classList.toggle("hide");
})

search_widget.addEventListener("blur", function(event) {
  const search_tips = document.querySelector(".query_help_tips");
  search_tips.classList.toggle("hide");
})

search_widget.addEventListener("keyup", function(event) {
  if (event.key === "Enter" && this.value) {
    //pass
    // const search_query = new URLSearchParams({'q': search_widget.value}).toString();
    // let url = `${document.location.origin}questions/search?${search_query}`;
    // console.log(url);
    // document.location.assign(url);
  }
})

search_icon.addEventListener("click", function(event) {
  const search_query = new URLSearchParams({'q': search_widget.value}).toString();
  let url = `${document.location.origin}questions/search?${search_query}`;
  document.location.assign(url);
})

window.addEventListener("", function(event) {

})
