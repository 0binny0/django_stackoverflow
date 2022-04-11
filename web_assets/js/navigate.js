

let search_widget = document.getElementById("id_q");
let page_footer = document.querySelector(".page_footer");
console.log(page_footer);

window.addEventListener("load", function(event) {
  const page_footer_box_height = page_footer.getBoundingClientRect().height;
  page_footer.style.height = `${page_footer_box_height + 75}px`;

})

search_widget.addEventListener("focus", function(event) {
  const search_tips = document.querySelector(".query_help_tips");
  search_tips.classList.toggle("hide");
})

search_widget.addEventListener("blur", function(event) {
  const search_tips = document.querySelector(".query_help_tips");
  search_tips.classList.toggle("hide");
})
