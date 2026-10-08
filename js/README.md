# lemmata (JavaScript)

Inject [Lemmata](https://github.com/ian-hickey/lemmata) modules into an `.xlsx` file and verify them. Pure JavaScript, no Excel required.

```js
import { fetchIndex, findModule, withDependencies, injectModules, createWorkbook, verifyWorkbook } from "lemmata";
import { readFileSync, writeFileSync } from "node:fs";

const index = await fetchIndex();                       // https://ian-hickey.github.io/lemmata/index.json
const mods = withDependencies(index, [findModule(index, "cagr"), findModule(index, "npv")]);
const bytes = injectModules(readFileSync("model.xlsx"), mods);   // or createWorkbook() for a new file
writeFileSync("model.xlsx", bytes);

const report = await verifyWorkbook(bytes, index);      // every LEMMA.* name must be "current"
```

The injector writes each module as a workbook-scoped defined name with the `_xlfn.` and `_xlpm.` prefixes the file format requires, and records `id@version sha256:<module_hash>` in the name's comment. Cells then call the module like any function: `=LEMMA.CAGR(A1, A2, A3)`.
