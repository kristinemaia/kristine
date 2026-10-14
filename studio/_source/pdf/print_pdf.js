// Transformă 5-minute-desk-stretch.html în PDF (A4, o pagină) cu Chromium.
// Rulare:  NODE_PATH=$(npm root -g) node print_pdf.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const html = path.join(__dirname, '5-minute-desk-stretch.html');
  const out = process.argv[2] || path.join(__dirname, '..', '..', '5-minute-desk-stretch.pdf');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
  if (process.argv[3]) {
    await page.setViewportSize({ width: 794, height: 1123 });
    await page.screenshot({ path: process.argv[3], fullPage: false });
  }
  await browser.close();
  console.log('PDF:', out);
})();
