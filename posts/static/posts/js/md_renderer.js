
const renderer = new marked.Renderer();

renderer.code = function(code, infostring) {
  return `<br/><pre><code class="block_code_snippet fill_block_width">${code}</code></pre><br/>`
}

renderer.codespan = function(code) {
  return `<code class="block_code_snippet">${code}</code>`
}

renderer.list = function(body, ordered, start) {
  var x = /(?<=<li>).+(?=<\/li>)/g;
  const matches = Array.from(body.matchAll(x));
  return matches.map(
    (content, i) => `<li class="mk_list_item">${content}</li>`
  ).join("");
}

export { renderer };
