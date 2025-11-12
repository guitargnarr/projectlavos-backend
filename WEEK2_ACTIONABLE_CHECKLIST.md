# Week 2 Remaining Work - Actionable Checklist
**Generated:** November 7, 2025 @ 4:20 AM
**Purpose:** Clean, prioritized to-do list for execution
**Total Time Estimate:** 9 hours to Week 3 readiness

---

## 🔴 CRITICAL (Must Do Before Week 3)

### 1. End-to-End Testing Session
**Time:** 1 hour
**Priority:** HIGHEST - Validates everything works

- [ ] Open https://demos.projectlavos.com in Chrome
- [ ] Test Restaurant Analyzer: Select Jack Fry's → Click Analyze → Verify results display
- [ ] Test Restaurant Analyzer: Go offline → Trigger error → Verify retry button works
- [ ] Open https://demos.projectlavos.com in Safari
- [ ] Test Restaurant Analyzer in Safari (same flow)
- [ ] Open https://demos.projectlavos.com on iPhone (Chrome DevTools mobile emulator)
- [ ] Verify mobile layout: Grid stacks vertically, text readable, buttons tappable
- [ ] Open https://about.projectlavos.com in Chrome
- [ ] Verify 10-Hour Question displays prominently in hero
- [ ] Click "Try Free Demos" → Verify goes to demos.projectlavos.com
- [ ] Click "Let's Talk" → Verify opens email with subject "10-Hour Question"
- [ ] Document any broken functionality in GitHub issue

---

### 2. Build Sales Email Scorer
**Time:** 4 hours
**Priority:** HIGH - Core demo for Week 3 outreach

#### Backend (1.5 hours)
- [ ] Open `projectlavos-backend/main.py`
- [ ] Add POST /api/score-email endpoint (line ~800)
- [ ] Create EmailRequest model with subject + body fields
- [ ] Build Claude API prompt for email scoring
- [ ] Parse response into structured JSON (score, strengths, weaknesses, suggestions)
- [ ] Test endpoint with curl
- [ ] Commit: "feat(email-scorer): Add email scoring API endpoint"

#### Sample Data (30 minutes)
- [ ] Create directory: `projectlavos-backend/data/emails/`
- [ ] Create `good_email_1.json` (9/10 score example)
- [ ] Create `good_email_2.json` (8/10 score example)
- [ ] Create `bad_email_1.json` (4/10 score example)
- [ ] Create `bad_email_2.json` (3/10 score example)
- [ ] Add load sample data logic to API endpoint
- [ ] Commit: "feat(email-scorer): Add sample email data"

#### Frontend (1.5 hours)
- [ ] Open `projectlavos-monorepo/demos/src/App.jsx`
- [ ] Add EmailScorer component (after RestaurantAnalyzer, line ~710)
- [ ] Add subject input field
- [ ] Add body textarea (8 rows)
- [ ] Add "Good Example" and "Bad Example" buttons
- [ ] Add "Score Email" button with API integration
- [ ] Add score gauge display (0-10 with color coding)
- [ ] Add strengths/weaknesses/suggestions sections
- [ ] Update demos list to include EmailScorer (line ~136)
- [ ] Update stats counter: 4 → 5 demos (line ~88)
- [ ] Test build: `npm run build`
- [ ] Commit: "feat(email-scorer): Add email scorer frontend component"

#### Deploy (30 minutes)
- [ ] Backend: `git push` (Render auto-deploys)
- [ ] Wait 5 minutes for Render deployment
- [ ] Test backend: `curl -X POST https://projectlavos-backend.onrender.com/api/score-email -d '{"subject":"test","body":"test"}'`
- [ ] Frontend: `cd ~/Projects/projectlavos-monorepo/demos && vercel --prod --yes`
- [ ] Wait 30 seconds for Vercel deployment
- [ ] Test full flow: Open https://demos.projectlavos.com → Email Scorer → Good Example → Score
- [ ] Verify score displays and makes sense

---

### 3. Update LinkedIn Profile
**Time:** 30 minutes
**Priority:** HIGH - Required before LinkedIn posts

- [ ] Open linkedin.com/in/matthewdscott7 (or your URL)
- [ ] Click "Edit intro" → Update headline:
  - New: "I help Louisville businesses answer: 'What's taking 10+ hours per week?' • AI Consultant"
- [ ] Click "Edit about" → Replace first paragraph:
```
Everyone asks "Should we use AI?" I ask "What's taking 10 hours/week?"

Most businesses aren't ready for AI. They're ready for solving specific problems.

I built free demos for Louisville restaurants, sales teams, and business owners to see if AI actually solves THEIR problems—not abstract "transformations."

Try them at projectlavos.com. No sales call. No commitment.

If you have a 10-hour problem, let's talk.
```
- [ ] Click "Add profile section" → Featured → Add link
  - Title: "The 10-Hour Question"
  - URL: https://about.projectlavos.com
- [ ] Click "Add profile section" → Featured → Add link
  - Title: "Free AI Demos for Louisville SMBs"
  - URL: https://demos.projectlavos.com
- [ ] Edit "Experience" → Update current role:
  - Title: "AI Consultant"
  - Company: "Independent (projectlavos.com)"
  - Description: "Helping Louisville restaurants, legal firms, and real estate agencies implement practical AI tools that save 10+ hours per week."
- [ ] Save all changes
- [ ] Preview profile to verify everything looks good

---

### 4. Compile Restaurant Outreach List
**Time:** 1 hour
**Priority:** HIGH - Unblocks Week 3 execution

- [ ] Create spreadsheet: `~/Desktop/1_PRIORITY_JOB_SEARCH/Resumes_Master_2025/job_search/louisville_restaurant_outreach.csv`
- [ ] Add columns: restaurant_name, owner_name, owner_email, google_rating, recent_theme, outreach_status, notes
- [ ] Google search: "Louisville Chamber of Commerce restaurant members"
- [ ] Visit louisville.com or similar directory
- [ ] For each restaurant (target 50):
  - [ ] Copy restaurant name
  - [ ] Search "{restaurant name} Louisville owner" on LinkedIn
  - [ ] Copy owner/manager name
  - [ ] Visit restaurant website → Find email (usually info@ or contact@)
  - [ ] Check Google Maps → Copy rating
  - [ ] Read 2-3 recent reviews → Note common theme (e.g., "service delays", "food quality")
  - [ ] Add row to spreadsheet
- [ ] Aim for mix:
  - 20 upscale restaurants (Jack Fry's tier)
  - 20 mid-tier restaurants (local favorites)
  - 10 fast-casual restaurants (high volume)
- [ ] Save CSV
- [ ] Backup to Google Sheets (optional but recommended)

**Quick Win:** Start with these 10 known restaurants:
1. Jack Fry's
2. Proof on Main
3. Hammerheads
4. Bourbon Raw
5. Milkwood
6. Doc Crow's
7. Sidebar at Whiskey Row
8. Volare
9. Decca
10. Gralehaus

---

## 🟡 HIGH PRIORITY (Strongly Recommended)

### 5. Create Demo GIFs for Marketing
**Time:** 1 hour
**Priority:** HIGH - 3x LinkedIn engagement

**Setup:**
- [ ] Download Gifski (brew install gifski) if not installed
- [ ] Create folder: `~/Desktop/3_CONSULTING_BUSINESS/Marketing_Assets/Demo_GIFs/`

**Record Each Demo:**
- [ ] Open Chrome, resize window to 1280×720
- [ ] Navigate to https://demos.projectlavos.com
- [ ] QuickTime: File → New Screen Recording
- [ ] Select area (just the demo card)

**Restaurant Analyzer GIF (15 seconds):**
- [ ] Start recording
- [ ] Click "Hammerheads" restaurant
- [ ] Click "Analyze Reviews"
- [ ] Wait for results to display
- [ ] Show scroll through results
- [ ] Stop recording
- [ ] Save as `restaurant_analyzer_raw.mov`
- [ ] Convert: `gifski --fps 30 --quality 90 restaurant_analyzer_raw.mov -o restaurant_analyzer.gif`

**Repeat for:**
- [ ] Email Scorer (good vs bad comparison)
- [ ] Sentiment Analysis (Louisville restaurant review)
- [ ] Lead Scoring (tech startup example)
- [ ] Phishing Detection (Jobot scam example)

**Optimize:**
- [ ] Run for each GIF: `gifsicle -O3 --lossy=80 -o {filename}_optimized.gif {filename}.gif`
- [ ] Verify file size <5 MB each
- [ ] Test upload to LinkedIn (check preview)

---

### 6. Improve Loading & Error States
**Time:** 1.5 hours
**Priority:** MEDIUM - Better UX

**Loading States (1 hour):**
- [ ] Open `projectlavos-monorepo/demos/src/App.jsx`
- [ ] Find RestaurantAnalyzer loading state (line ~610)
- [ ] Replace "Analyzing Reviews..." with skeleton screen:
```jsx
{loading && (
  <div className="space-y-4 animate-pulse">
    <div className="h-32 bg-gray-200 border-3 border-lavos-black"></div>
    <div className="h-24 bg-gray-200 border-3 border-lavos-black"></div>
    <div className="h-24 bg-gray-200 border-3 border-lavos-black"></div>
  </div>
)}
```
- [ ] Apply same pattern to:
  - [ ] EmailScorer
  - [ ] SentimentDemo (line ~208)
  - [ ] LeadScoringDemo (line ~?)
  - [ ] PhishingDemo (line ~?)

**Error States (30 minutes):**
- [ ] Update error messages to be specific:
  - Cold start: "Demo server waking up (30 seconds)..."
  - Network: "Connection failed. Check your internet."
  - API error: "Something went wrong. Try again?"
- [ ] Add auto-retry for cold starts (setTimeout 30 seconds)
- [ ] Test by going offline and triggering errors
- [ ] Commit: "feat(demos): Improve loading and error states"
- [ ] Deploy: `vercel --prod --yes`

---

### 7. Draft LinkedIn Posts
**Time:** 45 minutes
**Priority:** HIGH - Ready for Week 3

**Post 1: Restaurant Analyzer (Monday, Nov 18)**
- [ ] Open Notes app or Google Docs
- [ ] Write caption:
```
Louisville restaurant owners: What do your customers ACTUALLY say in reviews?

I built a free AI tool that analyzes your reviews in 2 minutes:
• What customers love
• What frustrates them
• Specific improvements

Try it: demos.projectlavos.com

#LouisvilleKY #RestaurantMarketing #AIForBusiness
```
- [ ] Save as `linkedin_post_1_restaurant.txt`
- [ ] Mark GIF needed: restaurant_analyzer.gif

**Post 2: Email Scorer (Wednesday, Nov 20)**
- [ ] Write caption:
```
Sales teams: Is your email scoring 9/10 or 3/10?

Most fail because:
• Too long (300+ words)
• Not personalized
• No clear CTA

Free AI scorer: demos.projectlavos.com

#SalesStrategy #EmailMarketing #LouisvilleKY
```
- [ ] Save as `linkedin_post_2_email.txt`
- [ ] Mark GIF needed: email_scorer.gif

**Post 3: Sentiment Analysis (Friday, Nov 22)**
- [ ] Write caption:
```
Louisville businesses: Stop guessing what customers think.

Free sentiment analyzer shows:
• Positive vs negative themes
- Key pain points
• Trending feedback

Try: demos.projectlavos.com

#CustomerExperience #LouisvilleKY
```
- [ ] Save as `linkedin_post_3_sentiment.txt`
- [ ] Mark GIF needed: sentiment_analysis.gif

---

### 8. Performance Audit
**Time:** 30 minutes
**Priority:** MEDIUM - Ensure fast load times

- [ ] Open Chrome
- [ ] Navigate to https://demos.projectlavos.com
- [ ] Open DevTools (Cmd+Option+I)
- [ ] Click "Lighthouse" tab
- [ ] Select "Mobile" + "Performance" + "Accessibility" + "Best Practices" + "SEO"
- [ ] Click "Generate report"
- [ ] Review scores (target: 90+ on all)
- [ ] Note any issues (images too large, fonts not preloaded, etc.)
- [ ] Repeat for https://about.projectlavos.com
- [ ] If scores <90, fix critical issues:
  - Convert images to WebP
  - Add font-display: swap to CSS
  - Preload critical assets
- [ ] Re-run Lighthouse to verify improvements
- [ ] Save reports: `lighthouse_demos_{date}.html` and `lighthouse_about_{date}.html`

---

## 🟢 MEDIUM PRIORITY (Nice to Have)

### 9. Configure GitHub Actions Secrets
**Time:** 15 minutes
**Priority:** LOW - Manual deployment works fine

- [ ] Open https://vercel.com/dashboard
- [ ] Click Settings → Tokens → Create Token
- [ ] Copy VERCEL_TOKEN
- [ ] Copy VERCEL_ORG_ID (from Settings → General)
- [ ] For each project (main-site, demos, about, services):
  - [ ] Click project → Settings → General
  - [ ] Copy Project ID
- [ ] Open https://github.com/guitargnarr/projectlavos-monorepo/settings/secrets/actions
- [ ] Click "New repository secret" for each:
  - [ ] VERCEL_TOKEN
  - [ ] VERCEL_ORG_ID
  - [ ] VERCEL_PROJECT_ID_MAIN
  - [ ] VERCEL_PROJECT_ID_DEMOS
  - [ ] VERCEL_PROJECT_ID_ABOUT
  - [ ] VERCEL_PROJECT_ID_SERVICES
- [ ] Test: Make dummy commit to trigger workflow
- [ ] Check Actions tab for success

---

### 10. Add Google Analytics
**Time:** 30 minutes
**Priority:** MEDIUM - Can add Week 4

- [ ] Open analytics.google.com
- [ ] Create new GA4 property: "Project Lavos"
- [ ] Copy Measurement ID (G-XXXXXXXXXX)
- [ ] Open `projectlavos-monorepo/demos/index.html`
- [ ] Add Google Analytics script to <head>:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```
- [ ] Repeat for about, main-site, services
- [ ] Deploy all sites
- [ ] Verify in GA real-time view
- [ ] Set up custom events:
  - demo_used (event_category: "engagement", event_label: "{demo_name}")
  - cta_click (event_category: "conversion", event_label: "{cta_name}")

---

## ⚪ LOW PRIORITY (Future Enhancements)

### 11. SEO Optimization
**Time:** 30 minutes
**Priority:** LOW - Traffic validation first

- [ ] Update meta descriptions (150-160 chars)
- [ ] Add OG images (1200×630 PNG)
- [ ] Test social sharing previews
- [ ] Add JSON-LD structured data

---

### 12. Define Pricing Structure
**Time:** 30 minutes
**Priority:** MEDIUM - Good to have ready

- [ ] Research Louisville consulting rates (Google, LinkedIn)
- [ ] Define 3 tiers:
  - **Starter:** $3K one-time (1 AI tool implementation)
  - **Growth:** $5K one-time + $500/month (2-3 tools + support)
  - **Enterprise:** Custom (full AI strategy + ongoing)
- [ ] Create simple pricing page
- [ ] OR prepare pricing response email template

---

## 📊 Progress Tracking

**Completed:** 8 hours (Session 1)
**Remaining:** 9 hours (Sessions 2-4)
**Total Week 2:** 17 hours

**Critical Path to Week 3:**
1. ✅ Restaurant Analyzer (Session 1)
2. ✅ 10-Hour Question Positioning (Session 1)
3. ⏳ End-to-End Testing (1 hour)
4. ⏳ Sales Email Scorer (4 hours)
5. ⏳ LinkedIn Profile Update (30 minutes)
6. ⏳ Restaurant Outreach List (1 hour)
7. ⏳ Demo GIFs (1 hour)

**Week 3 Ready:** When items 3-7 complete (7.5 hours remaining)

---

## 💡 Quick Wins (If Short on Time)

If you only have 3 hours before Week 3:

1. **End-to-End Testing (1 hour)** - Validate core functionality
2. **LinkedIn Profile Update (30 minutes)** - Positioning live
3. **Restaurant Outreach List (1 hour)** - Unblock outreach
4. **Email Templates Ready (30 minutes)** - Copy from CLAIM_PAGE_ULTRATHINK.md

This gets you to Week 3 with 4 demos (skip Email Scorer for now) and lets you start outreach.

---

## ✅ Definition of Done

**Week 2 Complete When:**
- [ ] All demos tested in Chrome + Safari + Mobile
- [ ] 5 demos deployed and functional
- [ ] LinkedIn profile reflects 10-Hour Question positioning
- [ ] 50 restaurants in outreach list with emails
- [ ] 3 LinkedIn posts drafted with GIFs
- [ ] No critical bugs blocking user flow

**Ready for Week 3 Outreach ✅**

---

**Last Updated:** November 7, 2025 @ 4:20 AM
**Status:** 8/17 hours complete (47%)
**Next Action:** End-to-end testing session
