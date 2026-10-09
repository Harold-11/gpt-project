import fs from 'node:fs';
import {build} from 'esbuild';
const root=new URL('../',import.meta.url);
const glb=fs.readFileSync(new URL('dist/lavadero-piedra.glb',root));
const result=await build({entryPoints:[new URL('src/viewer.js',root).pathname],bundle:true,write:false,format:'iife',minify:true,legalComments:'inline',define:{MODEL_BASE64:JSON.stringify(glb.toString('base64'))}});
let html=fs.readFileSync(new URL('src/viewer.template.html',root),'utf8');
html=html.replace('/*__BUNDLE__*/',()=>result.outputFiles[0].text.replaceAll('</script','<\\/script'));
fs.writeFileSync(new URL('dist/lavadero-vista-3d.html',root),html);
console.log('Visor autónomo creado: '+Buffer.byteLength(html)+' bytes');
