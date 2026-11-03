import { chromium } from 'playwright';

async function testThemeToggle() {
  console.log('--- Verifying Theme Toggle ---');
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true
  });

  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  try {
    // 1. Visit Welcome Page
    await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle' });
    
    // Check initial state
    let isDarkHtml = await page.evaluate(() => document.documentElement.classList.contains('dark'));
    console.log('1. Initial Welcome page is dark:', isDarkHtml);

    // Toggle on Welcome Page
    const welcomeToggle = page.locator('button:has-text("Mode")');
    await welcomeToggle.click();
    isDarkHtml = await page.evaluate(() => document.documentElement.classList.contains('dark'));
    console.log('2. After clicking toggle on Welcome page, is dark:', isDarkHtml);
    if (!isDarkHtml) throw new Error('Welcome page did not toggle to dark mode');

    // 2. Go to Faculty Dashboard
    await page.goto('http://127.0.0.1:5173/faculty/dashboard', { waitUntil: 'networkidle' });
    isDarkHtml = await page.evaluate(() => document.documentElement.classList.contains('dark'));
    console.log('3. Dashboard loaded with dark mode persisted:', isDarkHtml);

    // Verify background color of body
    const bodyBg = await page.evaluate(() => window.getComputedStyle(document.body).backgroundColor);
    console.log('4. Computed body background color:', bodyBg);

    // Toggle back to light mode in Top Header
    const headerToggle = page.locator('header button[title*="Mode"]');
    await headerToggle.click();
    isDarkHtml = await page.evaluate(() => document.documentElement.classList.contains('dark'));
    console.log('5. After clicking header toggle, is dark:', isDarkHtml);
    if (isDarkHtml) throw new Error('Header toggle failed to switch back to light mode');

    // Toggle back to dark
    await headerToggle.click();
    isDarkHtml = await page.evaluate(() => document.documentElement.classList.contains('dark'));
    console.log('6. After clicking header toggle again, is dark:', isDarkHtml);
    if (!isDarkHtml) throw new Error('Header toggle failed to switch to dark mode');

    console.log('\n[PASS] Dark / Light mode toggle is working flawlessly with full persistence!');
  } finally {
    await browser.close();
  }
}

testThemeToggle();
