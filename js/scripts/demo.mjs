// Write a workbook with modules from a local index.json: node demo.mjs <index.json> <out.xlsx> <id>...
import { readFileSync, writeFileSync } from "node:fs";
import { injectModules, createWorkbook, withDependencies, findModule } from "../src/index.js";

const [indexPath, out, ...ids] = process.argv.slice(2);
const index = JSON.parse(readFileSync(indexPath, "utf8"));
const mods = withDependencies(index, ids.map((id) => findModule(index, id)));
writeFileSync(out, injectModules(createWorkbook(), mods));
console.log(mods.map((m) => m.name).join(" "));
