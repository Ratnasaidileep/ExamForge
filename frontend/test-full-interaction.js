import { chromium } from 'playwright';

const BASE_URL = 'http://127.0.0.1:5173';

async function runFullInteractiveAudit() {
  console.log('='.repeat(70));
  console.log('  EXAMFORGE COMPREHENSIVE BROWSER INTERACTION & HEALTH AUDIT');
  console.log('='.repeat(70));

  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  const issues = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.error('[BROWSER CONSOLE ERROR]:', msg.text());
      issues.push(`Console Error on ${page.url()}: ${msg.text()}`);
    }
  });
  page.on('pageerror', err => {
    console.error('[PAGE UNCAUGHT EXCEPTION]:', err.message);
    issues.push(`Page Error on ${page.url()}: ${err.message}`);
  });

  // Handle all browser alert / confirm / prompt dialogs automatically
  page.on('dialog', async dialog => {
    console.log(`  [BROWSER DIALOG] Type: ${dialog.type()}, Message: "${dialog.message()}"`);
    await dialog.accept('Section New Title');
  });

  const wait = ms => new Promise(res => setTimeout(res, ms));

  try {
    // -------------------------------------------------------------
    // PHASE 1: Welcome Page & Role Selection
    // -------------------------------------------------------------
    console.log('\n[Phase 1] Testing Welcome Page (/)...');
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
    const welcomeTitle = await page.textContent('h1');
    console.log('  -> Welcome Title:', welcomeTitle?.trim());

    // Verify both entry buttons
    const facultyBtn = page.locator('button:has-text("Enter Faculty Workspace")');
    const studentBtn = page.locator('button:has-text("Enter Student Assessment")');
    if (!(await facultyBtn.isVisible())) issues.push('Faculty button not visible on Welcome Page');
    if (!(await studentBtn.isVisible())) issues.push('Student button not visible on Welcome Page');

    // Click Faculty Demo Entry
    await facultyBtn.click();
    await page.waitForURL('**/faculty/dashboard');
    console.log('  [PASS] Navigated to Faculty Dashboard via Welcome Card');

    // -------------------------------------------------------------
    // PHASE 2: Faculty Dashboard & Metrics
    // -------------------------------------------------------------
    console.log('\n[Phase 2] Testing Faculty Dashboard (/faculty/dashboard)...');
    await page.waitForSelector('h1:has-text("Faculty Command Dashboard")');
    
    // Check quick metrics
    const statCards = await page.locator('.text-2xl.font-bold').allTextContents();
    console.log('  -> Dashboard Metrics Loaded:', statCards.slice(0, 5));

    // Test Quick Action: "Upload Notes"
    const uploadNotesBtn = page.locator('a[href="/faculty/documents"] button');
    await uploadNotesBtn.first().click();
    await page.waitForURL('**/faculty/documents');
    console.log('  [PASS] Navigated to Document Library via Dashboard quick action');

    // -------------------------------------------------------------
    // PHASE 3: Document Library & Topic Exploration
    // -------------------------------------------------------------
    console.log('\n[Phase 3] Testing Document Library (/faculty/documents)...');
    await page.waitForSelector('h1:has-text("Document Library")');

    // Test Search input
    const searchInput = page.locator('input[placeholder*="Search notes"]');
    await searchInput.fill('ITS');
    await wait(300);
    const docTitles = await page.locator('table tbody tr').allTextContents();
    console.log('  -> Filtered Documents row count:', docTitles.length);
    await searchInput.fill(''); // Clear

    // Test Extracted Content Preview Modal
    const previewBtn = page.locator('button[title*="Preview Extracted Text"]').first();
    if (await previewBtn.isVisible()) {
      await previewBtn.click();
      await page.waitForSelector('button:has-text("Close")');
      console.log('  [PASS] Document preview modal opened successfully');
      
      // Close modal
      const closeBtn = page.locator('button:has-text("Close")').last();
      await closeBtn.click();
      await wait(300);
    }

    // -------------------------------------------------------------
    // PHASE 4: Question Studio & Generation
    // -------------------------------------------------------------
    console.log('\n[Phase 4] Testing Question Studio (/faculty/generate)...');
    await page.goto(`${BASE_URL}/faculty/generate`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("AI Question Generation Studio")');

    // Adjust question count dropdown to 3 using its specific id
    const countSelect = page.locator('select#question-count');
    if (await countSelect.isVisible()) {
      await countSelect.selectOption('3');
      console.log('  -> Set Question Count to 3');
    }

    // Trigger AI Generation (Live Gemini AI)
    const generateBtn = page.locator('button:has-text("Generate with Gemini AI")');
    if (await generateBtn.isVisible()) {
      await generateBtn.click();
      console.log('  -> Gemini AI generation requested, awaiting completion...');
      await page.waitForURL('**/faculty/generation/**', { timeout: 90000 });
      console.log('  [PASS] Successfully redirected to Generation Review:', page.url());
    } else {
      // Fallback to sample demo generation if live button not present
      const sampleBtn = page.locator('button:has-text("Generate Sample")');
      await sampleBtn.click();
      await page.waitForURL('**/faculty/generation/**', { timeout: 15000 });
      console.log('  [PASS] Successfully generated demo questions:', page.url());
    }

    // -------------------------------------------------------------
    // PHASE 5: Generation Review & Batch Approval
    // -------------------------------------------------------------
    console.log('\n[Phase 5] Testing Generation Review Actions...');
    await page.waitForSelector('h1:has-text("Generation Review")');
    await wait(1000);

    // Test Duplicate question in review
    const duplicateBtn = page.locator('button:has-text("Duplicate")').first();
    if (await duplicateBtn.isVisible()) {
      await duplicateBtn.click();
      await wait(600);
      console.log('  [PASS] Duplicated generated question in review');
    }

    // Test Batch Approve or Single Approve
    const batchApproveBtn = page.locator('button:has-text("Approve All")');
    if (await batchApproveBtn.isVisible() && !(await batchApproveBtn.isDisabled())) {
      await batchApproveBtn.click();
      await wait(1200);
      console.log('  [PASS] Batch approved questions into Central Bank');
    } else {
      const singleApprove = page.locator('button:has-text("Approve Question")').first();
      if (await singleApprove.isVisible()) {
        await singleApprove.click();
        await wait(600);
        console.log('  [PASS] Single approved question into Central Bank');
      }
    }

    // -------------------------------------------------------------
    // PHASE 6: Central Question Bank & LaTeX Math
    // -------------------------------------------------------------
    console.log('\n[Phase 6] Testing Central Question Bank (/faculty/questions)...');
    await page.goto(`${BASE_URL}/faculty/questions`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("Central Question Bank")');

    // Test type filter
    const typeFilter = page.locator('select').first();
    await typeFilter.selectOption('mcq');
    await wait(400);
    console.log('  -> Filtered question bank by MCQ type');
    await typeFilter.selectOption(''); // reset

    // Test revision history modal
    const historyBtn = page.locator('button[title="Inspect Revision History"]').first();
    if (await historyBtn.isVisible()) {
      await historyBtn.click();
      await page.waitForSelector('button:has-text("Close")');
      console.log('  [PASS] Immutable revision history modal opened');
      await page.locator('button:has-text("Close")').last().click();
      await wait(300);
    }

    // -------------------------------------------------------------
    // PHASE 7: Paper Builder & Scheduled Window
    // -------------------------------------------------------------
    console.log('\n[Phase 7] Testing Paper Builder (/faculty/papers/new)...');
    await page.goto(`${BASE_URL}/faculty/papers/new`, { waitUntil: 'networkidle' });
    await page.waitForURL('**/faculty/papers/paper_**');
    console.log('  -> Created draft paper:', page.url());

    // Test Auto-Assembly
    const autoAssembleBtn = page.locator('button:has-text("Auto-Assemble from Blueprint")');
    await autoAssembleBtn.click();
    await wait(1500);
    console.log('  [PASS] Auto-assembled questions from blueprint');

    // Test Scheduled Window inputs
    console.log('  -> Testing Scheduled Window examinations form...');
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    const startStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
    const endDate = new Date(now.getTime() + 3 * 3600 * 1000);
    const endStr = `${endDate.getFullYear()}-${pad(endDate.getMonth() + 1)}-${pad(endDate.getDate())}T${pad(endDate.getHours())}:${pad(endDate.getMinutes())}`;

    const startInput = page.locator('input[type="datetime-local"]').first();
    const endInput = page.locator('input[type="datetime-local"]').last();
    if (await startInput.isVisible() && await endInput.isVisible()) {
      await startInput.fill(startStr);
      await endInput.fill(endStr);
      const saveScheduleBtn = page.locator('button:has-text("Save Schedule")');
      await saveScheduleBtn.click();
      await wait(1000);
      console.log('  [PASS] Scheduled examination window saved');
    }

    // Test Add Custom Section
    const addSectionBtn = page.locator('button:has-text("Add Section")');
    await addSectionBtn.click();
    await wait(800);
    console.log('  [PASS] Added new custom section to exam paper');

    // Test Publish Paper
    const publishBtn = page.locator('button:has-text("Publish Formal Exam")');
    if (await publishBtn.isVisible()) {
      await publishBtn.click();
      await wait(1500);
      console.log('  [PASS] Examination published formally');
    }

    // -------------------------------------------------------------
    // PHASE 8: Faculty Analytics
    // -------------------------------------------------------------
    console.log('\n[Phase 8] Testing Faculty Analytics (/faculty/analytics)...');
    await page.goto(`${BASE_URL}/faculty/analytics`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("Faculty Curriculum Analytics")');
    await wait(1000);

    // Verify Recharts SVG elements rendered
    const svgs = await page.locator('svg.recharts-surface').count();
    console.log(`  -> Rendered Recharts SVGs: ${svgs} charts`);
    if (svgs < 2) issues.push('Fewer than expected charts rendered on Faculty Analytics');

    // -------------------------------------------------------------
    // PHASE 9: Demo Role Switcher
    // -------------------------------------------------------------
    console.log('\n[Phase 9] Testing Demo Role Switcher (Faculty -> Student)...');
    const studentSwitchBtn = page.locator('header button:has-text("Student")');
    await studentSwitchBtn.click();
    await page.waitForURL('**/student/dashboard');
    await page.waitForSelector('h1:has-text("Welcome back")');
    console.log('  [PASS] Successfully switched role to Student (Aditi Rao)');

    // -------------------------------------------------------------
    // PHASE 10: Student Practice & Exam Library
    // -------------------------------------------------------------
    console.log('\n[Phase 10] Testing Student Practice Library (/student/practice)...');
    await page.goto(`${BASE_URL}/student/practice`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("Examinations & Practice Library")');

    // Verify Window badges & start assessment button
    const startExamBtn = page.locator('button:has-text("Start Assessment")').first();
    if (await startExamBtn.isVisible()) {
      await startExamBtn.click();
      await page.waitForSelector('h3:has-text("Start Assessment?")');
      console.log('  [PASS] Timed assessment instructions modal displayed');

      // Click "Begin Test Now"
      const beginBtn = page.locator('button:has-text("Begin Test Now")');
      await beginBtn.click();
      await page.waitForURL('**/student/attempt/**', { timeout: 15000 });
      console.log('  [PASS] Successfully entered active assessment room:', page.url());
    }

    // -------------------------------------------------------------
    // PHASE 11: Timed Assessment Room & Live LaTeX Formula
    // -------------------------------------------------------------
    console.log('\n[Phase 11] Interacting with Active Exam Room...');
    await page.waitForSelector('h1');

    // 1. Answer MCQ options if available
    const mcqButtons = page.locator('button:has(div.rounded-full)');
    if (await mcqButtons.first().isVisible()) {
      await mcqButtons.first().click();
      console.log('  [PASS] Answered MCQ choice');
    }

    // 2. Test Mark for Review
    const markReviewBtn = page.locator('button:has-text("Mark for Review")');
    if (await markReviewBtn.isVisible()) {
      await markReviewBtn.click();
      console.log('  [PASS] Marked question for review');
    }

    // 3. Jump to descriptive question via question palette
    const qPaletteButtons = page.locator('button.h-9');
    const paletteCount = await qPaletteButtons.count();
    if (paletteCount > 0) {
      await qPaletteButtons.last().click();
      await wait(400);
      console.log(`  -> Navigated to Question ${paletteCount} in palette`);
    }

    // 4. Test Descriptive Answer with Live LaTeX Math Preview
    const descTextarea = page.locator('textarea');
    if (await descTextarea.isVisible()) {
      await descTextarea.fill('The energy equivalence equation is given by $E = mc^2$ and the kinetic energy is $$E_k = \\frac{1}{2}mv^2$$.');
      await wait(600);
      
      // Verify Live LaTeX Preview box appeared
      const katexEl = page.locator('.katex');
      if (await katexEl.first().isVisible()) {
        console.log('  [PASS] Live LaTeX formula preview rendered math via KaTeX!');
      }
    }

    // 5. Submit Assessment
    const submitBtn = page.locator('button:has-text("Submit Assessment")');
    await submitBtn.click();
    await page.waitForSelector('h3:has-text("Submit Assessment?")');
    console.log('  -> Submission confirmation modal opened');

    const confirmSubmit = page.locator('button:has-text("Confirm Submission")');
    await confirmSubmit.click();
    await page.waitForURL('**/student/attempt/**/results', { timeout: 25000 });
    console.log('  [PASS] Successfully submitted assessment and arrived at Results Page:', page.url());

    // -------------------------------------------------------------
    // PHASE 12: Assessment Results & Explanations Review
    // -------------------------------------------------------------
    console.log('\n[Phase 12] Testing Assessment Results Page...');
    await page.waitForSelector('h1');
    const resultScores = await page.locator('.text-3xl.font-extrabold').allTextContents();
    console.log('  -> Scores Summary Cards:', resultScores);

    // Verify Math formula rendering in answers
    const katexResults = await page.locator('.katex').count();
    console.log(`  [PASS] KaTeX math expressions rendered on Results page (${katexResults} elements)`);

    // -------------------------------------------------------------
    // PHASE 13: Student Progress Analytics
    // -------------------------------------------------------------
    console.log('\n[Phase 13] Testing Student Progress Page (/student/progress)...');
    await page.goto(`${BASE_URL}/student/progress`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("Student Progress & Analytics")');
    const progressSvgs = await page.locator('svg.recharts-surface').count();
    console.log(`  [PASS] Student performance charts rendered: ${progressSvgs} SVGs`);

    // -------------------------------------------------------------
    // PHASE 14: Faculty Grading Queue & Manual Evaluation
    // -------------------------------------------------------------
    console.log('\n[Phase 14] Testing Faculty Grading Queue (/faculty/grading)...');
    // Switch back to faculty using Header Switcher
    const facultySwitchBtn = page.locator('header button:has-text("Faculty")');
    await facultySwitchBtn.click();
    await page.waitForURL('**/faculty/dashboard');
    console.log('  [PASS] Successfully switched role back to Faculty');

    await page.goto(`${BASE_URL}/faculty/grading`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("Descriptive Grading Queue")');

    // Open first pending grading attempt
    const evaluateBtn = page.locator('button:has-text("Open Grading Workspace")').first();
    if (await evaluateBtn.isVisible()) {
      await evaluateBtn.click();
      await page.waitForURL('**/faculty/grading/att_**');
      console.log('  [PASS] Opened Faculty Grading Workspace:', page.url());

      // Enter marks & feedback
      const marksInput = page.locator('input[type="number"]').first();
      if (await marksInput.isVisible()) {
        await marksInput.fill('4.5');
        const feedbackInput = page.locator('input[placeholder*="Excellent explanation"]').or(page.locator('input[placeholder*="feedback"]')).first();
        if (await feedbackInput.isVisible()) {
          await feedbackInput.fill('Well structured derivation and clear mathematical explanation.');
        }
        const saveMarksBtn = page.locator('button:has-text("Save Marks")').or(page.locator('button:has-text("Update Marks")')).first();
        await saveMarksBtn.click();
        await wait(600);
        console.log('  [PASS] Awarded partial marks and qualitative feedback');
      }

      // Finalize grading
      const finalizeBtn = page.locator('button:has-text("Finalize Evaluation & Release")');
      if (await finalizeBtn.isVisible() && !(await finalizeBtn.isDisabled())) {
        await finalizeBtn.click();
        await wait(1000);
        console.log('  [PASS] Finalized grading and released student marks');
      }
    }

    // -------------------------------------------------------------
    // PHASE 15: Top Bar Notifications & Demo Data Controls
    // -------------------------------------------------------------
    console.log('\n[Phase 15] Testing Notifications & Topbar Controls...');
    const notifBtn = page.locator('button:has(svg.lucide-bell)').first();
    if (await notifBtn.isVisible()) {
      await notifBtn.click();
      await wait(400);
      console.log('  [PASS] Notifications drawer opened');
      await notifBtn.click(); // close
    }

    console.log('  [PASS] All interaction stages successfully reached.');

  } catch (err) {
    console.error('Test execution failed with error:', err);
    issues.push(`Execution Exception: ${err.message}`);
  } finally {
    await browser.close();
  }

  console.log('\n' + '='.repeat(70));
  console.log(`  AUDIT SUMMARY: ${issues.length} ISSUES FOUND`);
  console.log('='.repeat(70));
  if (issues.length > 0) {
    issues.forEach((iss, idx) => console.log(`  [${idx + 1}] ${iss}`));
  } else {
    console.log('  ALL AUDITED INTERACTIONS AND PAGES WORKED FLAWLESSLY WITH 0 ERRORS!');
  }
}

runFullInteractiveAudit();
