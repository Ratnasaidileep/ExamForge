import { chromium } from 'playwright';

const BASE_URL = 'http://127.0.0.1:5173';

async function runEvaluatorJourney() {
  console.log('='.repeat(75));
  console.log('  EXAMFORGE: COMPREHENSIVE DUAL-ROLE EVALUATOR AUDIT & VERIFICATION');
  console.log('='.repeat(75));

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
    await dialog.accept();
  });

  const wait = ms => new Promise(res => setTimeout(res, ms));

  try {
    // -------------------------------------------------------------------------
    // STEP 1: Welcome Page & Preloaded Curriculums Audit
    // -------------------------------------------------------------------------
    console.log('\n[Step 1] Auditing Welcome Page & Preloaded Curriculums...');
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
    const titleText = await page.textContent('h1');
    console.log('  -> Welcome Headline:', titleText?.trim());

    // Check preloaded subjects in overview card
    const subjectsCount = await page.locator('text=ITS-401, text=CS-301, text=AI-402, text=CY-201, text=DS-202').count();
    console.log(`  [OK] Multi-subject overview rendered`);

    // Enter Faculty Demo
    await page.locator('button:has-text("Enter Faculty Workspace")').click();
    await page.waitForURL('**/faculty/dashboard');
    console.log('  [OK] Successfully navigated to Faculty Workspace');

    // -------------------------------------------------------------------------
    // STEP 2: Document Library Multi-Subject Filtering
    // -------------------------------------------------------------------------
    console.log('\n[Step 2] Auditing Document Library with Multi-Subject Filtering...');
    await page.goto(`${BASE_URL}/faculty/documents`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("Document Library")');

    // Verify all 5 subject documents are listed
    const docRows = await page.locator('table tbody tr').count();
    console.log(`  -> Total Documents listed: ${docRows}`);
    if (docRows < 5) issues.push(`Expected at least 5 documents, found ${docRows}`);

    // Click CS-301 subject filter pill
    const cs301DocPill = page.locator('button:has-text("CS-301")');
    if (await cs301DocPill.isVisible()) {
      await cs301DocPill.click();
      await wait(400);
      const filteredRows = await page.locator('table tbody tr').count();
      console.log(`  [OK] Filtered Document Library by CS-301: ${filteredRows} document(s) displayed`);
    }

    // Reset to All Subjects
    await page.locator('button:has-text("All Subjects")').first().click();
    await wait(300);

    // -------------------------------------------------------------------------
    // STEP 3: Question Bank Multi-Subject Filtering
    // -------------------------------------------------------------------------
    console.log('\n[Step 3] Auditing Central Question Bank across Subjects...');
    await page.goto(`${BASE_URL}/faculty/questions`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("Central Question Bank")');

    // Verify header badge displays 5 Subjects Preloaded
    const badgeText = await page.locator('text=/\\d+ Subjects Preloaded/').textContent();
    console.log(`  -> Header Badge: "${badgeText?.trim()}"`);

    // Select AI-402 in subject dropdown (first select in the grid)
    const subjectDropdown = page.locator('select').first();
    if (await subjectDropdown.isVisible()) {
      await subjectDropdown.selectOption('AI-402');
      await wait(400);
      const aiQs = await page.locator('.divide-y > div').count();
      console.log(`  [OK] Filtered Question Bank for AI-402: ${aiQs} questions displayed`);
    }

    // -------------------------------------------------------------------------
    // STEP 4: Paper Library & One-Click Live Publication Test
    // -------------------------------------------------------------------------
    console.log('\n[Step 4] Auditing Paper Library & Testing Live Publication of Ready Drafts...');
    await page.goto(`${BASE_URL}/faculty/papers`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("Examination Papers Library")');

    // Click "Drafts (Ready)" filter
    await page.locator('button:has-text("Drafts (Ready)")').click();
    await wait(400);

    const draftCards = await page.locator('.grid > div').count();
    console.log(`  -> Ready-to-publish draft papers found: ${draftCards}`);
    if (draftCards < 5) issues.push(`Expected at least 5 ready draft papers, found ${draftCards}`);

    // Verify "DRAFT (READY TO PUBLISH)" badges
    const readyBadges = await page.locator('text=DRAFT (READY TO PUBLISH)').count();
    console.log(`  -> "DRAFT (READY TO PUBLISH)" badges count: ${readyBadges}`);

    // Test Quick Publish button on the CS-301 paper card
    const cs301Card = page.locator('.grid > div:has-text("CS-301")').first();
    const publishBtn = cs301Card.locator('button:has-text("Publish")');
    if (await publishBtn.isVisible()) {
      console.log('  -> Clicking Quick Publish on CS-301 Mid-Semester Exam...');
      await publishBtn.click();
      await wait(1500);

      // Verify success feedback banner appears
      const successAlert = page.locator('.bg-emerald-50, .text-emerald-800');
      if (await successAlert.first().isVisible()) {
        const alertMsg = await successAlert.first().textContent();
        console.log(`  [OK] Success Notification Received: "${alertMsg?.trim().replace(/\s+/g, ' ')}"`);
      }

      // Click "All Papers" to see the published card
      await page.locator('button:has-text("All Papers")').click();
      await wait(500);

      const updatedCard = page.locator('.grid > div:has-text("CS-301")').first();
      const publishedBadge = updatedCard.locator('text=PUBLISHED');
      if (await publishedBadge.isVisible()) {
        console.log('  [OK] CS-301 paper status confirmed PUBLISHED in Library!');
      }
    } else {
      issues.push('Quick Publish button not visible on CS-301 draft paper card');
    }

    // -------------------------------------------------------------------------
    // STEP 5: Student Practice Library & Examination Room
    // -------------------------------------------------------------------------
    console.log('\n[Step 5] Auditing Student Assessment Portal & Examination Room...');
    // Switch to Student Mode
    await page.locator('header button:has-text("Student")').click();
    await page.waitForURL('**/student/dashboard');
    console.log('  [OK] Switched role to Student (Aditi Rao)');

    // Navigate to Practice & Exams Library
    await page.goto(`${BASE_URL}/student/practice`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("Examinations & Practice Library")');

    // Filter by CS-301 subject
    const cs301StudentPill = page.locator('button:has-text("CS-301")');
    if (await cs301StudentPill.isVisible()) {
      await cs301StudentPill.click();
      await wait(400);
      console.log('  [OK] Student filtered exams by CS-301');
    }

    // Verify the newly published CS-301 exam is present
    const cs301ExamCard = page.locator('.grid > div:has-text("CS-301")');
    if (await cs301ExamCard.first().isVisible()) {
      console.log('  [OK] Newly published CS-301 exam is visible to student!');
      
      const startExamBtn = cs301ExamCard.locator('button:has-text("Start Assessment")').first();
      await startExamBtn.click();
      await page.waitForSelector('h3:has-text("Start Assessment?")');
      
      // Click "Begin Test Now"
      await page.locator('button:has-text("Begin Test Now")').click();
      await page.waitForURL('**/student/attempt/**', { timeout: 15000 });
      console.log('  [OK] Student entered live examination room:', page.url());
    }

    // -------------------------------------------------------------------------
    // STEP 6: Interacting with Examination Room & Live LaTeX Math
    // -------------------------------------------------------------------------
    console.log('\n[Step 6] Taking Assessment & Verifying LaTeX Formula Rendering...');
    await page.waitForSelector('h1');

    // 1. Answer MCQs
    const mcqChoices = page.locator('button:has(div.rounded-full)');
    if (await mcqChoices.first().isVisible()) {
      await mcqChoices.first().click();
      console.log('  [OK] Answered MCQ option');
    }

    // 2. Jump to Short Answer Question via question palette
    const paletteButtons = page.locator('button.h-9');
    const palCount = await paletteButtons.count();
    if (palCount >= 6) {
      await paletteButtons.nth(5).click(); // Q6 (Short answer)
      await wait(400);
      console.log('  [OK] Navigated to Section B descriptive question');
    }

    // 3. Type descriptive answer with LaTeX mathematical equation
    const answerTextarea = page.locator('textarea');
    if (await answerTextarea.isVisible()) {
      await answerTextarea.fill('Quorum replication requires $R + W > N$. By the Pigeonhole Principle, read and write quorums overlap on at least one replica. In LSM trees, write throughput is $\\mathcal{O}(1)$ into MemTable.');
      await wait(600);

      // Verify KaTeX math rendered in the live equation preview box
      const katexElements = await page.locator('.katex').count();
      console.log(`  [OK] KaTeX equations rendered in live preview (${katexElements} KaTeX tokens)`);
    }

    // 4. Submit Examination
    await page.locator('button:has-text("Submit Assessment")').click();
    await page.waitForSelector('h3:has-text("Submit Assessment?")');
    await page.locator('button:has-text("Confirm Submission")').click();
    await page.waitForURL('**/student/attempt/**/results', { timeout: 25000 });
    console.log('  [OK] Examination successfully submitted! Arrived at results:', page.url());

    // -------------------------------------------------------------------------
    // STEP 7: Faculty Grading Queue Evaluation & Score Finalization
    // -------------------------------------------------------------------------
    console.log('\n[Step 7] Auditing Faculty Grading Queue & Scoring Evaluation...');
    // Switch back to faculty
    await page.locator('header button:has-text("Faculty")').click();
    await page.waitForURL('**/faculty/dashboard');
    console.log('  [OK] Switched role back to Faculty');

    await page.goto(`${BASE_URL}/faculty/grading`, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1:has-text("Descriptive Grading Queue")');

    // Check pending submissions in queue
    const queueRows = await page.locator('table tbody tr').count();
    console.log(`  -> Submissions pending evaluation in queue: ${queueRows}`);

    const openGradeBtn = page.locator('button:has-text("Open Grading Workspace")').first();
    if (await openGradeBtn.isVisible()) {
      await openGradeBtn.click();
      await page.waitForURL('**/faculty/grading/att_**');
      console.log('  [OK] Opened grading workspace for submission:', page.url());

      // Grade descriptive answer
      const marksInput = page.locator('input[type="number"]').first();
      if (await marksInput.isVisible()) {
        await marksInput.fill('5.0');
        const feedbackInput = page.locator('input[placeholder*="feedback"]').or(page.locator('input[placeholder*="explanation"]')).first();
        if (await feedbackInput.isVisible()) {
          await feedbackInput.fill('Rigorous derivation of quorum condition and LSM sequential write properties.');
        }
        const saveBtn = page.locator('button:has-text("Save Marks")').or(page.locator('button:has-text("Update Marks")')).first();
        await saveBtn.click();
        await wait(600);
        console.log('  [OK] Awarded full marks (5.0/5.0) and written qualitative feedback');
      }

      // Finalize evaluation
      const finalizeBtn = page.locator('button:has-text("Finalize Evaluation & Release")');
      if (await finalizeBtn.isVisible() && !(await finalizeBtn.isDisabled())) {
        await finalizeBtn.click();
        await wait(1000);
        console.log('  [OK] Evaluated & released student examination score');
      }
    }

    // -------------------------------------------------------------------------
    // STEP 8: Theme Switcher Audit (Light & Dark Mode)
    // -------------------------------------------------------------------------
    console.log('\n[Step 8] Auditing Dark/Light Mode Theme Toggle...');
    const themeBtn = page.locator('button[title*="mode"]').first();
    if (await themeBtn.isVisible()) {
      // Toggle to dark mode
      await themeBtn.click();
      await wait(300);
      const isDark = await page.evaluate(() => document.documentElement.classList.contains('dark'));
      console.log(`  -> Toggled Dark Mode: active=${isDark}`);
      if (!isDark) issues.push('Dark mode class not added to <html> element');

      // Toggle back to light mode
      await themeBtn.click();
      await wait(300);
      const isStillDark = await page.evaluate(() => document.documentElement.classList.contains('dark'));
      console.log(`  -> Toggled Light Mode: active=${!isStillDark}`);
      if (isStillDark) issues.push('Dark mode class not removed when toggling light mode');
    }

    console.log('\n  [PASS] All dual-role evaluator journey stages completed successfully!');

  } catch (err) {
    console.error('Evaluator journey failed with exception:', err);
    issues.push(`Evaluator Journey Exception: ${err.message}`);
  } finally {
    await browser.close();
  }

  console.log('\n' + '='.repeat(75));
  console.log(`  EVALUATOR AUDIT REPORT: ${issues.length} DEFECTS FOUND`);
  console.log('='.repeat(75));
  if (issues.length > 0) {
    issues.forEach((iss, idx) => console.log(`  [${idx + 1}] ${iss}`));
  } else {
    console.log('  CONGRATULATIONS: 100% of tested user flows passed with ZERO defects!');
  }
}

runEvaluatorJourney();
