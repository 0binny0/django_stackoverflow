
import { renderer } from "./md_renderer.js";

let post_content_body = document.querySelector("#id_body");
let post_preview = document.querySelector("div[id*=post_preview]");
let text_input_fields = [post_content_body];
let markdown_options = Array.from(document.querySelector("#mkdown_options").children);

window.addEventListener("load", (event) => {
  let form = document.querySelector("#postform");
  let form_box = form.getBoundingClientRect();
  form.style.height = `${form_box.height + 75}px`;
})



markdown_options.forEach((mkd_option, i, array) => {
  mkd_option.addEventListener("click", function(event) {
    // display the selected menu
    const selected_menu_title = this.textContent.replace("\n", "").trim().toLowerCase();
    const markdown_menu = document.querySelector(`#mkd_${selected_menu_title}`);
    markdown_menu.classList.toggle("hide_mkd_block");
    // hide previously selected menus
    const menu_titles = array.map((menu_title) => menu_title.textContent.replace("\n", "").trim().toLowerCase());
    let other_mkd_menus = menu_titles.map((menu_title) => {
      if (menu_title !== selected_menu_title) {
        const mkd_menu = document.querySelector(`#mkd_${menu_title}`);
        return mkd_menu;
      };
    }).filter((menu) => menu !== undefined);
    const other_menus_open = other_mkd_menus.filter((menu) => {
      return !menu.classList.contains("hide_mkd_block");
    });
    if (other_menus_open) {
      other_menus_open.forEach((mk_menu) => mk_menu.classList.toggle("hide_mkd_block"));
    }
  })
})

text_input_fields.forEach((input_field) => {
  input_field.addEventListener("focus", function(event) {
    this.style.cssText = "box-shadow: 0px 0px 2px 3px lightblue; border: 1px solid blue";
  })

  input_field.addEventListener("blur", function(event) {
    this.style.cssText = "box-shadow: none; border: 1px solid lightgrey";
  })

})

post_content_body.addEventListener("keyup", (event) => {
  let post_content = post_content_body.value;
  console.log(post_content_body.value);
  post_preview.innerHTML = marked.parse(post_content, {'renderer': renderer});
})
