
let page_url = new URL(document.location);

document.addEventListener("DOMContentLoaded", function(event) {
  const all_indexed_queries = Array.from(document.getElementsByClassName("query_box"));
  const page_url = new URL(this.location);
  let query_string = new URLSearchParams(page_url.search);
  if (page_url.pathname.includes("user")) {
    debugger;
    let select_menu_tabs = Array.from(document.querySelectorAll("option"));
    if (query_string.has("tab")) {
      const url_tab_selected = query_string.get("tab").toLowerCase();
      let current_tab_index = select_menu_tabs.findIndex((tab) => {
        const _tab = tab.textContent.toLowerCase();
        return _tab === url_tab_selected
      });
      let active_tab;
      if (current_tab_index !== -1) {
        active_tab = select_menu_tabs.at(current_tab_index);
      } else {
        active_tab = select_menu_tabs.at(0);
      }
      active_tab.setAttribute("selected", true);
    }
  }
  let index_query_tab = query_string.get("sort");
  if (all_indexed_queries.length !== 0) {
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
  }
})
let select_tab_menu = document.querySelector("select");
select_tab_menu.addEventListener("change", function(event) {
  const tab = event.target.value.toLowerCase();
  const user_id = document.location.href.match(/(?<=users\/)\d+/i).at(0);
  let query_string = new RegExp(`(?<=${user_id}).*`);
  const tab_url = page_url.href.replace(query_string, `?tab=${tab}`);
  document.location.href = tab_url;
})
