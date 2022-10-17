
document.addEventListener("DOMContentLoaded", function(event) {
  const all_indexed_queries = Array.from(document.getElementsByClassName("query_box"));
  const page_url = new URL(this.location);
  let query_string = new URLSearchParams(page_url.search);
  let index_query_tab = query_string.get("sort");
  all_indexed_queries.forEach((query) => {
    query.classList.remove("selected_index");
  })
  if (index_query_tab) {
    index_query_tab = index_query_tab.toLowerCase();
  } else {
    index_query_tab = all_indexed_queries.at(0).textContent.toLowerCase();
  }
  let query_tab_match = all_indexed_queries.find((query) => {
    return query.textContent.toLowerCase() === index_query_tab;
  });
  if (query_tab_match === undefined) {
    const selected_query_index = all_indexed_queries.at(0);
    selected_query_index.classList.add("selected_index");
  } else {
    query_tab_match.classList.add("selected_index");
  }
})
