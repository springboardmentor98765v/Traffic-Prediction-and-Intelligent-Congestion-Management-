// Syntax-check the inline <script> blocks in HTML pages (ESLint only lints .js files).
// A single syntax error stops the whole block from running, e.g. DEF-M3-023: a missing
// "}" in operator dashboard.html disabled every function in that block.
//
//   node QA/tools/check_inline_js.js front-end/Front-end/*.html
//
// Exits 1 if any block fails to parse.
const fs = require('fs');
const vm = require('vm');

let failed = 0;
for (const file of process.argv.slice(2)) {
  const html = fs.readFileSync(file, 'utf8');
  const re = /<script(?![^>]*\bsrc=)([^>]*)>([\s\S]*?)<\/script>/g;
  let match;
  let index = 0;
  while ((match = re.exec(html))) {
    index++;
    // Skip JSON / template blocks; only classic scripts and modules are JavaScript.
    if (/type="(?!text\/javascript|module)/.test(match[1])) continue;
    const line = html.slice(0, match.index).split('\n').length;
    try {
      new vm.Script(match[2], { filename: file });
    } catch (err) {
      failed++;
      console.log(`FAIL ${file}: inline script #${index} (starts line ${line}): ${err.message}`);
    }
  }
}
console.log(failed ? `${failed} inline script(s) failed to parse` : 'All inline scripts parse');
process.exit(failed ? 1 : 0);
