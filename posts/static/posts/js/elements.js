

let post_title = document.querySelector("#id_title");
let post_content_body = document.querySelector("#id_body");
let post_tag_inputs = Array.from(document.querySelectorAll("input[id*=id_tags]"));
let text_input_fields = [post_title, post_content_body, ...post_tag_inputs];
let post_preview = document.querySelector("div[id*=post_preview]");
let form = document.querySelector("#id_questionform");
const optional_input_fields = post_tag_inputs.slice(1, );

let markdown_options = document.querySelector("#mkdown_options");


export {
   post_title, post_tag_inputs, text_input_fields, post_content_body,
   post_preview, form, optional_input_fields
};
