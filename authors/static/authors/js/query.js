
let query_post_types = document.getElementsByClassName("queried_post");


document.addEventListener("DOMContentLoaded", (e) => {
  const queried_page = new URL(window.location);
  let tabbed_post = new URLSearchParams(queried_page.search).get('tab');
  if (!tabbed_post) {
    tabbed_post = "summary";
  } else {
    tabbed_post = tabbed_post.toLowerCase();
    const tabs = ['summary', 'questions', 'answers', 'tags', 'bookmarks'];
    if (!tabs.includes(tabbed_post)) {
      tabbed_post = "summary";
    }
  }
  const previous_post_type = Array.prototype.find.call(
    query_post_types, (post_type) => {
      const post_attrs = post_type.classList;
      const name = post_type.textContent.toLowerCase()
      return post_attrs.contains("active") && name != tabbed_post;
    }
  );
  if (previous_post_type) {
    previous_post_type.classList.remove("active");
  }
  const active_post_type = Array.prototype.filter.call(query_post_types, (post_type) => {
    return post_type.textContent.toLowerCase() === tabbed_post
  })[0];
  active_post_type.classList.add("active");
})


Array.prototype.forEach.call(query_post_types, (post_type) => {
  post_type.addEventListener("click", function(event) {
    const other_query_index_links = Array.from(this.parentElement.children).filter((link) => {
      return link.textContent.toLowerCase() !== this.textContent.toLowerCase()
    });
    other_query_index_links.forEach((link) => {
      link.classList.remove("active");
    })
    this.classList.add("active");
  })
})
