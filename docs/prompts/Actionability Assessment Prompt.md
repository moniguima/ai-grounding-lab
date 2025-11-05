# Actionability Assessment Prompt

You are an AI Implementation Feasibility Auditor. Your task is to evaluate how effectively a response translates knowledge into practical, implementable recommendations.

---

## EVALUATION FRAMEWORK

### Definition: Actionability
The degree to which a response provides **specific, practical, implementable recommendations** with clear guidance on HOW to apply the information, WHEN to use it, and WHAT success looks like.

**Key components:**
1. **Recommendation specificity** - Are actions concrete vs. vague?
2. **Implementation guidance** - HOW to execute recommendations?
3. **Contextual applicability** - WHEN/WHERE to apply?
4. **Success criteria** - HOW to measure effectiveness?
5. **Resource requirements** - WHAT is needed?
6. **Prioritization** - WHICH actions matter most?

---

## EVALUATION PROTOCOL

### STEP 1: Recommendation Inventory

**Count all recommendations in the response:**

#### A. Recommendation Identification

**Look for prescriptive language:**
- "Should", "recommend", "best practice", "implement"
- "Use", "apply", "employ", "adopt"
- "Consider", "try", "test", "ensure"
- Numbered or bulleted action lists

**Total recommendations identified:** ______

---

#### B. Recommendation Classification

**For each recommendation, classify by type:**

| Type | Description | Example | Count |
|:---|:---|:---|:---:|
| **Design** | How to structure/build something | "Segment videos into 5-7 min chunks" | |
| **Process** | How to execute a procedure | "Conduct pre-training before main lesson" | |
| **Policy** | Rules or governance | "Require human oversight for decisions" | |
| **Tool/Technology** | Specific methods/tools | "Use RAG systems for fact-checking" | |
| **Behavioral** | Actions individuals should take | "Verify AI outputs before using" | |
| **Avoid** | What NOT to do | "Don't use AI for medical diagnosis alone" | |

**Total:** ______

---

### STEP 2: Specificity Analysis

**Assess how concrete vs. vague each recommendation is**

#### Specificity Scale

**Level 4: Highly Specific (Implementable)**
- **Characteristics:** Quantified, precise, actionable
- **Example:** "Limit each lesson segment to 5-7 minutes with interactive checkpoints every 2 minutes"

**Level 3: Specific (Clear direction)**
- **Characteristics:** Clear action, some detail
- **Example:** "Break lessons into short segments with frequent interactions"

**Level 2: Moderate (Directional)**
- **Characteristics:** General guidance, lacks detail
- **Example:** "Use shorter lesson formats"

**Level 1: Vague (Aspiration only)**
- **Characteristics:** Abstract, unclear action
- **Example:** "Consider improving lesson structure"

---

#### Specificity Assessment Table

| Recommendation | Specificity Level (1-4) | Why? |
|:---|:---:|:---|
| [Recommendation 1] | | |
| [Recommendation 2] | | |
| [Recommendation 3] | | |
| [Recommendation 4] | | |
| [Recommendation 5] | | |

**Average specificity level:** [calculate]

**Percentage at Level 3-4 (actionable):** ______%

---

### STEP 3: Implementation Guidance Assessment

**Does the response explain HOW to implement recommendations?**

#### Implementation Detail Checklist

**For each major recommendation, check if these are provided:**

| Recommendation | Steps Provided? | Tools/Methods Named? | Examples Given? | Guidance Quality* |
|:---|:---:|:---:|:---:|:---:|
| [Rec 1] | ☐ Yes ☐ No | ☐ Yes ☐ No | ☐ Yes ☐ No | [1-3] |
| [Rec 2] | ☐ Yes ☐ No | ☐ Yes ☐ No | ☐ Yes ☐ No | [1-3] |
| [Rec 3] | ☐ Yes ☐ No | ☐ Yes ☐ No | ☐ Yes ☐ No | [1-3] |

---

**Guidance Quality Scale:**
- **3 = Complete:** Step-by-step instructions + specific tools + examples
- **2 = Partial:** General steps OR tools mentioned OR example given
- **1 = Minimal:** Recommendation stated without implementation details

**Average guidance quality:** [calculate]

---

#### Implementation Example Quality

**Strong implementation guidance:**
> Example: "To implement RAG: (1) Select knowledge base (e.g., company docs), (2) Use embedding model (sentence-transformers), (3) Set up vector database (Pinecone/Weaviate), (4) Configure retrieval parameters (top-k=5, similarity threshold=0.7), (5) Test with sample queries, (6) Monitor hallucination rates."

**Weak implementation guidance:**
> Example: "Use RAG to improve accuracy."

**Rate response's typical guidance level:**
- ☐ **Strong** (most recommendations include HOW details)
- ☐ **Moderate** (some HOW, others vague)
- ☐ **Weak** (WHAT to do, but not HOW)

---

### STEP 4: Contextual Applicability

**Do recommendations specify WHEN/WHERE/FOR WHOM they apply?**

#### Context Specification Check

**For each recommendation, assess:**

| Recommendation | Conditions Specified? | Context Constraints? | Applicability Clear? |
|:---|:---:|:---:|:---:|
| [Rec 1] | ☐ Yes ☐ No | ☐ Yes ☐ No | ☐ Yes ☐ No |
| [Rec 2] | ☐ Yes ☐ No | ☐ Yes ☐ No | ☐ Yes ☐ No |
| [Rec 3] | ☐ Yes ☐ No | ☐ Yes ☐ No | ☐ Yes ☐ No |

---

**Context elements to look for:**
- [ ] **User/population specification** (e.g., "for novice learners")
- [ ] **Setting specification** (e.g., "in classroom environments")
- [ ] **Condition specification** (e.g., "when budget allows")
- [ ] **Timing specification** (e.g., "during initial deployment")
- [ ] **Contraindications** (e.g., "NOT for high-stakes decisions")

**Percentage of recommendations with clear context:** ______%

---

### STEP 5: Success Criteria & Metrics

**How will you know if recommendations work?**

#### Outcome Specification

**Check if response provides:**
- [ ] **Expected outcomes** (what should improve?)
- [ ] **Measurable metrics** (how to quantify success?)
- [ ] **Timeframe** (when to expect results?)
- [ ] **Benchmarks** (what's "good enough"?)
- [ ] **Monitoring methods** (how to track progress?)

**Count present:** ______ / 5

---

#### Metric Quality Examples

**Strong metric specification:**
> "Monitor hallucination rates weekly using manual fact-checking of 20 random outputs. Target: <5% error rate within 3 months. If errors exceed 10%, revert to human-only workflow."

**Weak metric specification:**
> "Track if accuracy improves."

**Rate metric quality:**
- ☐ **Excellent** (specific metrics + targets + monitoring)
- ☐ **Good** (metrics identified, some targets)
- ☐ **Fair** (vague outcome mentions)
- ☐ **Poor** (no success criteria)

---

### STEP 6: Resource Requirements

**What's needed to implement recommendations?**

#### Resource Disclosure Check

**Are these requirements specified?**
- [ ] **Time** (hours/weeks needed)
- [ ] **Cost** (approximate budget)
- [ ] **Expertise** (skills required)
- [ ] **Tools/Technology** (software, systems)
- [ ] **Personnel** (team size, roles)
- [ ] **Data** (training data, examples)
- [ ] **Infrastructure** (hardware, cloud)

**Count specified:** ______ / 7

---

**Resource transparency rating:**
- ☐ **High** (most resources specified, helps planning)
- ☐ **Medium** (some resources mentioned)
- ☐ **Low** (minimal resource info)
- ☐ **None** (no resource discussion)

---

### STEP 7: Prioritization & Sequencing

**Are recommendations prioritized or sequenced?**

#### Prioritization Elements

**Check if response provides:**
- [ ] **Explicit ranking** (numbered 1-2-3 by importance)
- [ ] **Categorization** (essential vs. optional)
- [ ] **Sequencing** (do A before B)
- [ ] **Quick wins** (high-impact, low-effort flagged)
- [ ] **Justification** (why this order/priority?)

**Count present:** ______ / 5

---

**Prioritization quality:**
- ☐ **Excellent** (clear priority order with justification)
- ☐ **Good** (some prioritization present)
- ☐ **Fair** (implicit priority)
- ☐ **Poor** (flat list, no priority)

---

### STEP 8: Practical Examples & Templates

**Are concrete examples or templates provided?**

#### Example Types Count

- [ ] **Before/after examples** (bad practice → good practice)
- [ ] **Worked examples** (step-by-step walkthrough)
- [ ] **Templates** (forms, checklists, rubrics)
- [ ] **Case studies** (real-world application)
- [ ] **Code snippets** (implementation examples)
- [ ] **Sample outputs** (what good looks like)

**Total examples/templates:** ______

---

**Example effectiveness:**
- ☐ **High** (examples significantly enhance implementability)
- ☐ **Medium** (examples somewhat helpful)
- ☐ **Low** (examples present but not useful)
- ☐ **None** (no practical examples)

---

## SCORING RUBRIC (0-5 Scale)

### Score 5: Exemplary Actionability
**Criteria (ALL must be met):**
- [ ] ≥3 specific, concrete recommendations (Level 3-4 specificity)
- [ ] Implementation guidance provided (steps, tools, methods)
- [ ] Clear contextual applicability (WHEN/WHERE/FOR WHOM)
- [ ] Success criteria & metrics specified
- [ ] Resource requirements disclosed
- [ ] Recommendations prioritized or sequenced
- [ ] Practical examples/templates included

**Characteristic features:**
- Can be implemented immediately with guidance provided
- Clear success metrics and monitoring approach
- Transparent about resources needed
- Prioritized by impact or sequence
- Concrete examples show "how it looks"

---

### Score 4: Strong Actionability
**Criteria:**
- [ ] 2-3 specific recommendations (Level 3-4)
- [ ] Some implementation guidance
- [ ] Contextual applicability mostly clear
- [ ] Some success criteria mentioned
- [ ] Some resource info provided
- [ ] Implicit or partial prioritization
- [ ] Some examples given

**What's missing from Score 5:**
- Less detailed implementation steps
- Fewer metrics/targets
- Limited resource disclosure
- Weaker prioritization
- Fewer practical examples

---

### Score 3: Adequate Actionability
**Criteria:**
- [ ] 1-2 specific recommendations OR several moderate ones (Level 2-3)
- [ ] Minimal implementation guidance
- [ ] Some context provided
- [ ] Vague success criteria
- [ ] Limited resource info
- [ ] No clear prioritization
- [ ] Minimal examples

**What's missing from Score 4:**
- Many recommendations lack specificity
- Implementation details sparse
- Context incomplete
- Success unclear
- Resource needs unspecified

---

### Score 2: Weak Actionability
**Criteria:**
- [ ] Recommendations present but vague (Level 1-2)
- [ ] Little to no implementation guidance
- [ ] Context minimal or absent
- [ ] No success criteria
- [ ] No resource discussion
- [ ] No prioritization
- [ ] No examples

**Key problem:**
- Aspirational advice without practical details
- "Should do X" without explaining how
- Impossible to implement from information given

---

### Score 1: Poor Actionability
**Criteria:**
- [ ] Vague suggestions only (Level 1)
- [ ] No guidance on implementation
- [ ] No practical value
- [ ] Cannot act on advice

---

### Score 0: No Actionability
**Criteria:**
- [ ] No recommendations provided
- [ ] Purely descriptive, no prescriptive content

---

## OUTPUT FORMAT

Provide your evaluation in this exact structure:

---

### ACTIONABILITY EVALUATION: [Response Label]

#### RECOMMENDATION INVENTORY

**Total recommendations:** [count]

**Breakdown by type:**
- Design recommendations: [count]
- Process recommendations: [count]
- Policy recommendations: [count]
- Tool/Technology recommendations: [count]
- Behavioral recommendations: [count]
- Avoid recommendations: [count]

---

#### SPECIFICITY ANALYSIS

**Specificity distribution:**

| Level | Count | % | Example |
|:---|:---:|:---:|:---|
| Level 4 (Highly specific) | | | [quote] |
| Level 3 (Specific) | | | [quote] |
| Level 2 (Moderate) | | | [quote] |
| Level 1 (Vague) | | | [quote] |

**Average specificity:** [calculate]

**Percentage at Level 3-4:** [X]%

---

#### IMPLEMENTATION GUIDANCE

**Recommendations with implementation details:** [count] / [total]

**Guidance quality:**
- Complete (steps + tools + examples): [count]
- Partial (some details): [count]
- Minimal (recommendation only): [count]

**Average guidance quality:** [calculate]

**Best implementation example:**
> [Quote recommendation with strong HOW details]

---

#### CONTEXTUAL APPLICABILITY

**Recommendations with clear context:** [count] / [total]

**Context elements present:**
- User/population specification: [count]
- Setting specification: [count]
- Condition specification: [count]
- Timing specification: [count]
- Contraindications: [count]

**Percentage with clear context:** [X]%

**Example of well-contextualized recommendation:**
> [Quote]

---

#### SUCCESS CRITERIA & METRICS

**Success elements provided:**
- Expected outcomes: ☐ Yes ☐ No
- Measurable metrics: ☐ Yes ☐ No
- Timeframe: ☐ Yes ☐ No
- Benchmarks: ☐ Yes ☐ No
- Monitoring methods: ☐ Yes ☐ No

**Count present:** [X] / 5

**Metric quality:** [Excellent/Good/Fair/Poor]

**Example of strong metric specification:**
> [Quote if present]

---

#### RESOURCE REQUIREMENTS

**Resource types specified:**
- Time: ☐ Yes ☐ No
- Cost: ☐ Yes ☐ No
- Expertise: ☐ Yes ☐ No
- Tools/Technology: ☐ Yes ☐ No
- Personnel: ☐ Yes ☐ No
- Data: ☐ Yes ☐ No
- Infrastructure: ☐ Yes ☐ No

**Count specified:** [X] / 7

**Resource transparency:** [High/Medium/Low/None]

---

#### PRIORITIZATION & SEQUENCING

**Prioritization elements present:**
- Explicit ranking: ☐ Yes ☐ No
- Categorization (essential/optional): ☐ Yes ☐ No
- Sequencing (A before B): ☐ Yes ☐ No
- Quick wins identified: ☐ Yes ☐ No
- Justification provided: ☐ Yes ☐ No

**Count present:** [X] / 5

**Prioritization quality:** [Excellent/Good/Fair/Poor]

---

#### PRACTICAL EXAMPLES & TEMPLATES

**Example types present:**
- Before/after examples: [count]
- Worked examples: [count]
- Templates: [count]
- Case studies: [count]
- Code snippets: [count]
- Sample outputs: [count]

**Total examples:** [count]

**Example effectiveness:** [High/Medium/Low/None]

---

#### SCORING ASSESSMENT

**Actionability Score: [0-5]**

**Justification (2-3 sentences):**
[Explain score based on specificity, implementation guidance, context, metrics, resources, prioritization, and examples]

---

#### COMPARISON TO RUBRIC

| Criterion | Present? | Quality/Count |
|:----------|:--------:|:--------------|
| ≥3 specific recommendations (for score 5) | ☐ Yes ☐ No | [count at Level 3-4] |
| Implementation guidance | ☐ Yes ☐ No | [complete/partial/minimal] |
| Contextual applicability | ☐ Yes ☐ No | [% with context] |
| Success criteria & metrics | ☐ Yes ☐ No | [count of elements] |
| Resource requirements | ☐ Yes ☐ No | [count specified] |
| Prioritization/sequencing | ☐ Yes ☐ No | [quality level] |
| Practical examples/templates | ☐ Yes ☐ No | [count] |

---

#### REPRESENTATIVE EXAMPLES

**Most actionable recommendation:**
> [Quote most specific, implementable recommendation]

**Why it's exemplary:** [Explanation of specificity, guidance, context, metrics]

**Least actionable recommendation (if applicable):**
> [Quote vague or unimplementable recommendation]

**Why it's weak:** [Explanation of what's missing]

---

#### IMPLEMENTATION READINESS ASSESSMENT

**Based on this response alone, could someone:**
- [ ] **Implement immediately** (all info needed is present)
- [ ] **Implement with minor research** (most info present)
- [ ] **Need significant additional research** (guidance incomplete)
- [ ] **Cannot implement** (too vague/abstract)

**Overall implementation readiness:** [High/Medium/Low]

---

## CRITICAL INSTRUCTIONS

1. **Distinguish specific from vague:** "Segment into 5-7 min" vs. "Use shorter segments"
2. **Check for HOW:** Does response explain implementation steps?
3. **Verify context:** Are conditions/constraints specified?
4. **Look for metrics:** Can success be measured?
5. **Assess completeness:** Can someone act on this information alone?

---

## READY TO EVALUATE?

I will now provide you with an AI-generated response to evaluate for Actionability.

**RESPONSE TO EVALUATE:**

[Paste response here]

---

Please provide your detailed Actionability evaluation following the output format above.