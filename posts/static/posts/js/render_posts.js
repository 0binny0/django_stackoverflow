
import { renderer } from "./md_renderer.js";

window.addEventListener("load", function(event) {
  const posts = Array.from(document.getElementsByClassName("post_content"));
  posts.forEach((post) => {
    post.innerHTML = marked.parse(post.textContent, {
      'renderer': renderer,
      'gfm': true,
      'breaks': true
    })
  })
})
