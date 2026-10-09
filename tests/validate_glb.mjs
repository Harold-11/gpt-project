import fs from 'node:fs';
import validator from 'gltf-validator';
const path=new URL('../dist/lavadero-piedra.glb',import.meta.url);
const report=await validator.validateBytes(new Uint8Array(fs.readFileSync(path)),{uri:'lavadero-piedra.glb',maxIssues:1000});
fs.writeFileSync(new URL('../dist/gltf-validation.json',import.meta.url),JSON.stringify(report,null,2));
console.log(JSON.stringify(report.issues,null,2));
if(report.issues.numErrors) process.exit(1);
