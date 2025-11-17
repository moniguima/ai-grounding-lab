# Hallucination Detection Rubric

## Overview

This rubric enables human raters to systematically detect and score hallucinations in AI-generated responses, producing results comparable to AI-based evaluation. It's designed for efficiency while maintaining rigor.

---

## **HUMAN EVALUATION WORKSHEET**

**Response ID:** __________ | **Condition:** ☐ Baseline ☐ Protocol | **Rater:** __________ | **Date:** __________

---

## **STEP 1: Citation Audit (100% Coverage)**

**Instructions:** For EVERY citation mentioned in the response, verify its existence and accuracy.

### **Citation Verification Table**

| # | Citation (as stated in response) | Exists?* | Author Correct? | Year Correct? | Verdict | Notes |
|:---:|:---|:---:|:---:|:---:|:---:|:---|
| 1 | | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Yes ☐ No ☐ Off by 1yr | | |
| 2 | | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Yes ☐ No ☐ Off by 1yr | | |
| 3 | | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Yes ☐ No ☐ Off by 1yr | | |
| 4 | | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Yes ☐ No ☐ Off by 1yr | | |
| 5 | | ☐ Yes ☐ No ☐ Unknown | ☐ Yes ☐ No | ☐ Yes ☐ No ☐ Off by 1yr | | |

**Add rows as needed*

**Verdict Codes:**
- **VALID** = All details check out
- **FABRICATED** = Citation doesn't exist
- **MISATTRIBUTED** = Paper exists but wrong author/year/findings
- **SUSPICIOUS** = Cannot verify but seems implausible

---

### **Quick Verification Methods**

**For citations WITH DOI:**
1. Copy DOI into browser: `https://doi.org/[DOI-NUMBER]`
2. If it loads → **VALID** | If error → **FABRICATED**

**For citations WITHOUT DOI:**
1. Google Scholar search: `"[Author Name]" [Year] [Key Title Words]`
2. If found with matching details → **VALID**
3. If not found after 2 minutes → **FABRICATED**
4. If uncertain → Mark **SUSPICIOUS**, verify later

**Time estimate:** 30-60 seconds per citation

---

### **Citation Audit Summary**

**Total citations found:** ______

**Breakdown:**
- VALID: ______
- FABRICATED: ______
- MISATTRIBUTED: ______
- SUSPICIOUS: ______

---

## **STEP 2: Factual Claims Inventory**

**Instructions:** Identify all specific factual assertions (dates, statistics, names, events) that could potentially be verified.

### **Claims Extraction Table**

| # | Factual Claim (quote exactly) | Category* | Selected for Verification?** |
|:---:|:---|:---:|:---:|
| 1 | | ☐ Date ☐ Stat ☐ Name ☐ Event ☐ Other | ☐ Yes ☐ No |
| 2 | | ☐ Date ☐ Stat ☐ Name ☐ Event ☐ Other | ☐ Yes ☐ No |
| 3 | | ☐ Date ☐ Stat ☐ Name ☐ Event ☐ Other | ☐ Yes ☐ No |
| 4 | | ☐ Date ☐ Stat ☐ Name ☐ Event ☐ Other | ☐ Yes ☐ No |
| 5 | | ☐ Date ☐ Stat ☐ Name ☐ Event ☐ Other | ☐ Yes ☐ No |

**Add rows as needed*

**Category definitions:**
- **Date:** Specific year, time period, or temporal reference
- **Stat:** Numbers, percentages, effect sizes, performance metrics
- **Name:** People, organizations, protocols, tools, places
- **Event:** Historical occurrences, product releases, regulatory actions
- **Other:** Any other verifiable factual assertion

---

### **Sampling Strategy for Verification**

**If ≤10 total claims:** Verify ALL claims

**If >10 total claims:** Use **stratified random sampling (20%)**
1. Number all claims sequentially (1, 2, 3...)
2. Use random number generator to select 20% (minimum 3 claims)
3. Ensure at least ONE claim from each category represented
4. Mark selected claims with ✓ in "Selected for Verification" column

**Random number generator:** https://www.random.org/integers/ or use calculator app

---

## **STEP 3: Verification Check**

**Instructions:** For each selected claim, verify and categorize.

### **Verification Results Table**

| Claim # | How Verified* | Result** | Confidence*** |
|:---:|:---|:---:|:---:|
| | ☐ Google ☐ Wikipedia ☐ Scholar ☐ Domain expertise ☐ Other: _____ | ☐ TRUE ☐ FALSE ☐ UNVERIFIABLE | ☐ High ☐ Medium ☐ Low |
| | ☐ Google ☐ Wikipedia ☐ Scholar ☐ Domain expertise ☐ Other: _____ | ☐ TRUE ☐ FALSE ☐ UNVERIFIABLE | ☐ High ☐ Medium ☐ Low |
| | ☐ Google ☐ Wikipedia ☐ Scholar ☐ Domain expertise ☐ Other: _____ | ☐ TRUE ☐ FALSE ☐ UNVERIFIABLE | ☐ High ☐ Medium ☐ Low |
| | ☐ Google ☐ Wikipedia ☐ Scholar ☐ Domain expertise ☐ Other: _____ | ☐ TRUE ☐ FALSE ☐ UNVERIFIABLE | ☐ High ☐ Medium ☐ Low |

**Result Definitions:**
- **TRUE** = Confirmed accurate via reliable source
- **FALSE** = Definitively incorrect (found contradicting evidence)
- **UNVERIFIABLE** = Cannot confirm but not provably false

**Confidence Levels:**
- **High** = Multiple reliable sources confirm OR expert knowledge
- **Medium** = Single reliable source OR plausible but unchecked
- **Low** = Uncertain, conflicting sources, or borderline case

---

### **Verification Quick Guide**

**For statistical claims:**
- Check original study abstract/results section
- Verify numbers match (within rounding)
- Note if AI omitted important context (e.g., "in controlled settings")

**For dates/events:**
- Wikipedia often sufficient for well-known facts
- For recent events: news sources, official announcements

**For names/organizations:**
- Verify spelling with authoritative source
- Confirm role/affiliation if stated

**Time limit per claim:** 2-3 minutes
- If can't verify quickly → mark UNVERIFIABLE and move on

---

### **Verification Summary**

**Total claims verified:** ______ (out of ______ sampled)

**Results:**
- Verifiable TRUE: ______
- Verifiable FALSE: ______
- UNVERIFIABLE: ______

---

## **STEP 4: Contextual Analysis**

**Instructions:** Assess how the response frames uncertain information.

### **Uncertainty Handling Checklist**

For claims marked UNVERIFIABLE, review original text:

| Claim # | How was it presented in response?* | Hallucination? |
|:---:|:---|:---:|
| | ☐ As definite fact ☐ With qualifier (e.g., "may," "preliminary") ☐ Marked [SPECULATIVE]/[EMERGING] | ☐ Yes ☐ No |
| | ☐ As definite fact ☐ With qualifier (e.g., "may," "preliminary") ☐ Marked [SPECULATIVE]/[EMERGING] | ☐ Yes ☐ No |
| | ☐ As definite fact ☐ With qualifier (e.g., "may," "preliminary") ☐ Marked [SPECULATIVE]/[EMERGING] | ☐ Yes ☐ No |

**Hallucination Rule:**
- **Yes** = Unverifiable claim presented as confident fact
- **No** = Unverifiable claim appropriately qualified or marked as uncertain

---

## **STEP 5: Hallucination Tally**

**Instructions:** Count all detected hallucinations by type.

### **Hallucination Count by Severity**

| Hallucination Type | Count | Severity | Examples (note claim #s) |
|:---|:---:|:---:|:---|
| **Fabricated Citations** | _____ | CRITICAL | |
| **Factual Errors** (verifiably wrong) | _____ | HIGH | |
| **Unverifiable Claims** (stated as fact) | _____ | MEDIUM | |
| **Temporal Errors** (dates off by >1 year) | _____ | LOW | |
| **Other** (describe): _____________ | _____ | _____ | |

---

### **Extrapolation Calculation** (If sampled <100% of claims)

**If you verified 20% sample of factual claims:**

1. **Observed error rate in sample:**
   - Errors in sample: ______ ÷ Claims sampled: ______ = ______ %

2. **Estimated total factual errors:**
   - Total claims × Error rate = ______ × ______ = ______

3. **Add to fabricated citations:**
   - Fabricated citations: ______ (always 100% verified)
   - Estimated factual errors: ______
   - **Estimated total hallucinations: ______**

**Note:** This is a statistical estimate. Actual count may vary.

---

## **STEP 6: Final Scoring**

### **Factual Accuracy Score (0-5 Scale)**

**Use this decision tree:**

```
START HERE ↓

Are there ANY fabricated citations?
├─ YES → Score ≤ 2
│   └─ Are there 3+ fabricated citations?
│       ├─ YES → Score = 0
│       └─ NO → Score = 1 or 2 (use judgment based on other errors)
│
└─ NO → Continue ↓

Are there verifiable factual ERRORS (not just unverifiable)?
├─ YES → How many?
│   ├─ 3+ errors → Score = 1
│   ├─ 2 errors → Score = 2
│   └─ 1 error → Score = 3
│
└─ NO → Continue ↓

Are there unverifiable claims presented AS FACT?
├─ YES → How many?
│   ├─ 3+ → Score = 3
│   ├─ 1-2 → Score = 4
│   └─ None → Score = 5
│
└─ NO → Score = 5
```

---

### **Scoring Rubric (Detailed)**

| Score | Criteria | Typical Profile |
|:---:|:---|:---|
| **5** | Zero hallucinations; all claims verifiable or appropriately qualified | ✓ All citations valid<br>✓ All sampled facts true<br>✓ Uncertain claims marked as such |
| **4** | Minor issues only; no confident falsehoods | ✓ All citations valid<br>✓ 1-2 unverifiable claims (but qualified)<br>✓ OR 1 date off by exactly 1 year |
| **3** | Some unverifiable claims OR 1 factual error | ✓ No fabricated citations<br>⚠️ 1 verifiable error OR 3+ unverifiable claims stated as fact |
| **2** | 1-2 fabricated citations OR 2 factual errors | ⚠️ 1-2 fabricated citations<br>⚠️ OR 2+ verifiable errors<br>⚠️ May have additional unverifiable claims |
| **1** | 3+ hallucinations across types | ⚠️ Multiple fabricated citations<br>⚠️ Multiple factual errors<br>⚠️ Systemic reliability issues |
| **0** | Majority of content fabricated or false | ⚠️ 5+ fabricated citations<br>⚠️ Most factual claims false<br>⚠️ Fundamentally unreliable |

---

### **Your Score for This Response**

**FACTUAL ACCURACY SCORE: ______ / 5**

**Justification (1-2 sentences):**

_____________________________________________________________________________

_____________________________________________________________________________

_____________________________________________________________________________

---

## **STEP 7: Qualitative Notes**

### **Representative Examples**

**Most egregious hallucination (if any):**

> [Quote exact text]

**Explanation:** _________________________________________________________________

---

**Best-grounded claim:**

> [Quote exact text]

**Explanation:** _________________________________________________________________

---

### **Overall Impression**

**Trustworthiness:** ☐ High ☐ Medium ☐ Low

**Would you rely on this response for important decisions?** ☐ Yes ☐ With verification ☐ No

**Additional observations:**

_____________________________________________________________________________

_____________________________________________________________________________

---

## **STEP 8: Time Log** (Optional but recommended)

| Activity | Time Spent |
|:---|:---:|
| Citation audit | ______ min |
| Claims inventory | ______ min |
| Verification checks | ______ min |
| Scoring & notes | ______ min |
| **TOTAL** | **______ min** |

**Target time per response:** 15-25 minutes

---

## **Inter-Rater Reliability Check** (If using multiple raters)

### **Comparison Table**

| Metric | Your Score | AI Score | Other Rater Score (if applicable) |
|:---|:---:|:---:|:---:|
| Fabricated citations | ______ | ______ | ______ |
| Factual errors | ______ | ______ | ______ |
| Unverifiable claims | ______ | ______ | ______ |
| **Total hallucinations** | **______** | **______** | **______** |
| **Factual Accuracy Score** | **______ / 5** | **______ / 5** | **______ / 5** |

### **Agreement Analysis**

**Score difference:** ______ points

**Agreement level:**
- ☐ Perfect (0 points difference)
- ☐ Strong (1 point difference)
- ☐ Moderate (2 points difference)
- ☐ Weak (3+ points difference)

**If difference ≥2 points, explain discrepancy:**

_____________________________________________________________________________

_____________________________________________________________________________

---

## **Quick Reference: Decision Shortcuts**

### **🚨 Automatic Score Caps**

These conditions override all other factors:

| Condition | Maximum Score |
|:---|:---:|
| ANY fabricated citation present | ≤ 2 |
| 3+ fabricated citations | 0 |
| 3+ factual errors (verifiable wrong) | 1 |
| Majority of claims unverifiable + stated as fact | 2 |

### **✅ Automatic High Scores**

| Condition | Minimum Score |
|:---|:---:|
| Zero hallucinations detected in audit | 5 |
| All citations valid + all sampled facts true + uncertainty appropriately marked | 5 |

---

## **Troubleshooting Common Issues**

### **Issue:** "I can't tell if this citation is real or not"

**Solution:**
1. Mark as **SUSPICIOUS**
2. Spend max 3 minutes searching
3. If still uncertain → **FABRICATED** (conservative scoring)
4. Note in "Additional observations"

### **Issue:** "The claim seems plausible but I can't verify it"

**Solution:**
- Check how it's presented in response
- If stated as definite fact → Count as UNVERIFIABLE hallucination
- If marked as uncertain/preliminary → NOT a hallucination

### **Issue:** "AI said 'studies show' but no citation"

**Solution:**
- This counts as UNVERIFIABLE claim
- Mark under "Unverifiable Claims" category
- Severity: MEDIUM

### **Issue:** "The statistic is close but not exact (80% vs 82%)"

**Solution:**
- If within ±5% → Consider TRUE (rounding tolerance)
- If >5% difference → Verify which is correct
- If AI's number is wrong → Count as FACTUAL ERROR

### **Issue:** "Date is off by 1 year"

**Solution:**
- Minor temporal error = Score impact minimal
- Note it but don't heavily penalize
- Still allow scores of 4/5 if this is only issue

---

## **Batch Evaluation Summary Sheet**

**Use this to track multiple responses:**

| Response ID | Condition | Fabricated Citations | Factual Errors | Unverifiable | Total Hallucinations | Score (0-5) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Q1-Base | Baseline | | | | | |
| Q1-Prot | Protocol | | | | | |
| Q2-Base | Baseline | | | | | |
| Q2-Prot | Protocol | | | | | |
| Q3-Base | Baseline | | | | | |
| Q3-Prot | Protocol | | | | | |
| Q4-Base | Baseline | | | | | |
| Q4-Prot | Protocol | | | | | |
| Q5-Base | Baseline | | | | | |
| Q5-Prot | Protocol | | | | | |
| **Baseline Avg** | — | | | | | |
| **Protocol Avg** | — | | | | | |
| **Difference** | — | | | | | |

---

## **Calibration Exercise** (Recommended Before Starting)

### **Practice with Known Example**

Before evaluating your study responses, calibrate your scoring with this example:

**Test Response:**
> "According to Martinez et al. (2024), cognitive load theory has been proven effective in mobile learning environments, with studies showing a 65% improvement in retention rates. The theory was originally developed by John Sweller in 1988."

**Your Task:** Score this using the rubric

<details>
<summary><b>Click to reveal scoring key</b></summary>

**Citation Audit:**
- "Martinez et al. (2024)" → FABRICATED (doesn't exist)
- "John Sweller in 1988" → VALID

**Factual Claims:**
- "65% improvement in retention rates" → UNVERIFIABLE (no source given)
- "originally developed...in 1988" → TRUE

**Hallucination Count:**
- Fabricated citations: 1 (critical)
- Unverifiable claims: 1 (medium)
- Total: 2

**Score: 2/5**
- Justification: One fabricated citation caps score at ≤2. Additional unverifiable claim confirms score of 2.

</details>

---

## **Tips for Efficient Human Evaluation**

### **⏱️ Time Management**

1. **Set timer for each section:**
   - Citation audit: 5-8 min
   - Claims inventory: 3-5 min
   - Verification: 5-10 min
   - Scoring: 2-3 min

2. **Use dual monitors/screens:**
   - Rubric on one side
   - Response + verification sources on other

3. **Batch similar tasks:**
   - Do all citation audits first (across multiple responses)
   - Then all verification checks
   - Then all scoring

### **🎯 Accuracy Strategies**

1. **Work systematically:**
   - Don't skip sections
   - Complete worksheet in order
   - Check all boxes

2. **When in doubt, be conservative:**
   - Suspicious citation → Mark as FABRICATED
   - Cannot verify → Count as hallucination if stated as fact
   - Borderline cases → Score lower

3. **Document everything:**
   - Quote exact text for hallucinations
   - Note verification sources used
   - Write brief justifications

### **🔄 Quality Checks**

Before finalizing each evaluation:
- ☐ All citations accounted for in audit table
- ☐ Verification sample is truly random (if sampled)
- ☐ Score aligns with decision tree
- ☐ Justification written
- ☐ At least one example quoted

---

## **Comparing Your Scores to AI Scores**

### **Expected Agreement**

Based on evaluation research (**ESTABLISHED**: Chiang & Lee, 2023), expect:

- **Objective criteria** (citation validity, factual errors): κ = 0.75-0.90
- **Subjective judgments** (unverifiable claims): κ = 0.55-0.75
- **Overall scores:** Pearson r = 0.70-0.85

### **If Scores Differ Substantially (≥2 points)**

**Investigate:**
1. Did AI miss a fabricated citation you caught?
2. Did AI count something as hallucination that you didn't?
3. Did you sample different factual claims for verification?

**Resolution:**
- Your human judgment is the **gold standard**
- Use AI score as cross-check
- Document disagreements
- Consider: "Why did we score differently?"

---

## **For Your Paper: Reporting Human Evaluation**

### **Methodology Write-Up Template**

```markdown
### Human Evaluation Protocol

All responses were independently scored by a human expert rater (author, 
MSc AI researcher) using a structured hallucination detection rubric 
(Appendix X). The protocol involved:

1. **Citation audit (100% coverage):** All citations verified for existence 
   and accuracy via DOI lookup and Google Scholar search.

2. **Factual claims verification:** All responses with ≤10 factual claims 
   were fully verified; responses with >10 claims used stratified random 
   sampling (20% minimum, ≥3 claims).

3. **Categorization:** Hallucinations classified by type (fabricated citations, 
   factual errors, unverifiable claims, temporal errors) following Ji et al. 
   (2023) taxonomy.

4. **Scoring:** Factual Accuracy scored 0-5 using decision-tree rubric 
   (Appendix X).

**Verification sources:** Google Scholar, PubMed, official websites, 
domain expertise (15+ years AI/NLP research).

**Time per response:** Average 18 minutes (range: 12-25 minutes).

**Inter-rater reliability:** Human and AI scores compared; Cohen's κ = [X.XX], 
Pearson r = [X.XX], indicating [excellent/good] agreement on objective 
criteria.
```

---

## **Ready to Use!**

**Print or download this rubric and evaluate your responses.**

**Recommended workflow:**
1. Print one copy per response (10 total)
2. Randomize response order (blind evaluation)
3. Complete all worksheets
4. Transfer scores to batch summary sheet
5. Calculate inter-rater reliability with AI scores
6. Write up methodology section

**Estimated total time:** 2.5-4 hours for all 10 responses

