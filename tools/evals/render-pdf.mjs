import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const args=process.argv.slice(2);
const option=(name,fallback)=>args.includes(name)?args[args.indexOf(name)+1]:fallback;
const inputArg=option('--input');
const outputArg=option('--output');
if(!inputArg || !outputArg)throw new Error('Usage: node render-pdf.mjs --input report.html --output report.pdf');
const source=path.resolve(inputArg);
const output=path.resolve(outputArg);
const {chromium}=await import('playwright');
const browser=await chromium.launch({headless:true});
try {
  const page=await browser.newPage({viewport:{width:1240,height:1000}});
  await page.goto(pathToFileURL(source).href);
  await page.evaluate(()=>document.fonts.ready);
  await page.emulateMedia({media:'print'});
  const overflow=await page.evaluate(()=>[...document.querySelectorAll('table,svg')].filter(e=>e.scrollWidth>e.clientWidth+2).length);
  if(overflow)throw new Error(`${overflow} table/chart overflowing horizontally`);
  fs.mkdirSync(path.dirname(output),{recursive:true});
  await page.pdf({path:output,preferCSSPageSize:true,printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#62736c"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
  console.log('Đã xuất PDF: '+output);
} finally {await browser.close();}
