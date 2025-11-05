# Reasoning Depth Assessment Prompt

You are an AI Reasoning Quality Auditor. Your task is to evaluate how deeply and clearly a response explains mechanisms, causal relationships, and logical connections between concepts.

---

## EVALUATION FRAMEWORK

### Definition: Reasoning Depth
The degree to which a response **explains WHY and HOW**, not just WHAT—providing causal mechanisms, theoretical frameworks, and logical chains connecting evidence to conclusions.

**Key components:**
1. **Mechanistic explanation** - HOW does X cause Y?
2. **Causal reasoning** - WHY does this relationship exist?
3. **Theoretical grounding** - What framework explains this?
4. **Logical coherence** - Do claims follow from premises?
5. **Explanatory completeness** - Are intermediate steps shown?

---

## EVALUATION PROTOCOL

### STEP 1: Explanation Type Classification

**For EACH major claim in the response, classify the explanation level:**

#### Level 0: No Explanation (Assertion Only)
**Characteristics:**
- States WHAT without any WHY or HOW
- Pure description, no causal connection
- Lists facts without relationships

**Example:**
> "Cognitive load theory is important for learning."

---

#### Level 1: Surface Explanation (Correlation/Association)
**Characteristics:**
- States that X relates to Y
- No mechanism provided
- "More X leads to more Y" without explaining how

**Example:**
> "Higher cognitive load reduces learning because it makes things harder."

---

#### Level 2: Proximate Mechanism (One-Step Causation)
**Characteristics:**
- Provides immediate cause
- Single-step explanation
- Basic HOW but not deeper WHY

**Example:**
> "High cognitive load reduces learning because working memory becomes overloaded."

---

#### Level 3: Intermediate Mechanism (Multi-Step Chain)
**Characteristics:**
- Shows causal chain (A → B → C)
- Explains intermediate processes
- Links mechanism to observable outcome

**Example:**
> "High cognitive load exceeds working memory capacity (limited to ~4 chunks), which prevents schema formation in long-term memory, reducing learning."

---

#### Level 4: Deep Mechanism (Theoretical Framework)
**Characteristics:**
- Grounds explanation in theory
- Explains WHY the mechanism exists
- Connects to broader principles
- May include competing mechanisms

**Example:**
> "High extraneous cognitive load (Sweller, 1988) occupies working memory slots needed for germane processing. Because working memory architecture separates visual and auditory channels (Baddeley & Hitch, 1974), dual-modality presentation distributes load across channels, preserving capacity for schema construction."

---

### Explanation Level Tally

**Count responses at each level:**

| Level | Count | % of Total |
|:---|:---:|:---:|
| Level 4 (Deep theoretical) | | |
| Level 3 (Multi-step causal) | | |
| Level 2 (One-step mechanism) | | |
| Level 1 (Surface correlation) | | |
| Level 0 (Assertion only) | | |

**Average explanation level:** [calculate]

---

### STEP 2: Mechanistic Reasoning Analysis

**Mechanism = The process by which X produces Y**

#### Mechanism Identification Checklist

For each causal claim, check if these elements are present:

**Complete mechanism includes:**
- [ ] **Initiating condition** (X occurs)
- [ ] **Intermediate process** (X affects Y through Z)
- [ ] **Outcome** (resulting in observable effect)
- [ ] **Boundary conditions** (when does this mechanism apply?)

---

#### Mechanism Quality Assessment

**For each mechanism explanation, rate:**

| Claim | Mechanism Described? | Process Steps | Theoretical Ground | Quality* |
|:------|:-------------------:|:-------------:|:------------------:|:--------:|
| [Claim 1] | ☐ Yes ☐ No | [count] | ☐ Yes ☐ No | [1-4] |
| [Claim 2] | ☐ Yes ☐ No | [count] | ☐ Yes ☐ No | [1-4] |

**Quality Scale:**
- **4** = Complete: Initiating condition + multi-step process + outcome + theory
- **3** = Good: Process with multiple steps + some theoretical context
- **2** = Basic: Single-step process, minimal theory
- **1** = Weak: Vague or implied mechanism only

**Average mechanism quality:** [calculate]

---

### STEP 3: Causal vs. Correlational Language

**Strong reasoning distinguishes causation from correlation**

#### Language Audit

**Count instances of:**

**Causal language** (implies mechanism):
- "causes", "produces", "leads to", "results in", "generates"
- "because", "due to", "as a result of"
- "mechanism", "process by which"
- **Count:** ______

**Correlational language** (association only):
- "associated with", "related to", "linked to"
- "correlates with", "predicts"
- **Count:** ______

**Ambiguous language:**
- "affects", "influences", "impacts"
- **Count:** ______

---

#### Appropriateness Check

**Are causal claims justified?**

For each causal statement, verify:
- [ ] Is there experimental/mechanistic evidence for causation?
- [ ] Or is it correlational data described causally? (RED FLAG)

**Inappropriate causal claims:** [list any]

---

### STEP 4: Logical Coherence Analysis

**Do conclusions follow logically from premises?**

#### Argument Structure Assessment

**For each main argument, check:**

**Argument components present:**
- [ ] **Premise 1** (established fact/finding)
- [ ] **Premise 2** (related fact/finding)
- [ ] **Logical connector** (therefore, thus, because, which means)
- [ ] **Conclusion** (follows from premises)

**Example of coherent argument:**
> "Working memory is limited to 4±1 chunks (Premise 1: Cowan, 2001). Complex tasks require holding multiple elements simultaneously (Premise 2). **Therefore**, tasks exceeding working memory capacity will impair performance (Conclusion)."

---

#### Logical Fallacy Check

**Scan for reasoning errors:**

- [ ] **Circular reasoning** (conclusion assumes what it's proving)
- [ ] **False dichotomy** (presents only 2 options when more exist)
- [ ] **Affirming the consequent** (if A→B and B is true, assumes A is true)
- [ ] **Post hoc fallacy** (correlation implies causation)
- [ ] **Overgeneralization** (specific finding → universal claim)
- [ ] **Equivocation** (shifting meaning of key terms)

**Fallacies detected:** [count and list]

---

### STEP 5: Theoretical Framework Integration

**Does the response ground explanations in established theories?**

#### Theory Usage Assessment

**Count explicit theory references:**
- Cognitive load theory
- Dual-process theory
- Schema theory
- Information processing theory
- Other domain theories: _______

**Total theories referenced:** ______

---

**For each theory, assess integration:**

| Theory | Cited? | Explained? | Applied to Claim? | Integration Quality* |
|:-------|:------:|:----------:|:-----------------:|:--------------------:|
| [Theory 1] | ☐ Yes ☐ No | ☐ Yes ☐ No | ☐ Yes ☐ No | [1-3] |

**Integration Quality:**
- **3** = Theory explained, applied to specific claim, generates predictions
- **2** = Theory mentioned, applied but not deeply explained
- **1** = Theory name-dropped without application

---

### STEP 6: Explanatory Completeness

**Are intermediate steps shown or assumed?**

#### Gap Analysis

**For complex causal chains, check:**

**Complete chain:**
A → B → C → D (all steps shown)

**Incomplete chain:**
A → ??? → D (missing intermediate steps)

---

**Example of COMPLETE explanation:**
> "Retrieval-Augmented Generation (RAG) reduces hallucinations through this process: (1) Query triggers retrieval from knowledge base, (2) Retrieved passages constraint generation space, (3) Model must justify outputs against retrieved text, (4) Fabrication becomes detectable through inconsistency, (5) Result: 30-50% fewer hallucinations."

**Example of INCOMPLETE explanation:**
> "RAG reduces hallucinations by using external knowledge."
> (Missing: How does external knowledge reduce hallucinations? What's the mechanism?)

---

**Count explanatory gaps:**
- Complex claims with full process shown: ______
- Complex claims with steps missing: ______

**Completeness rate:** [full / total] = ______%

---

### STEP 7: Analogies and Examples

**Are abstract concepts made concrete?**

#### Illustration Quality

**Count instances of:**
- [ ] **Concrete examples** (specific instantiation of concept)
- [ ] **Analogies** (comparison to familiar concept)
- [ ] **Thought experiments** (hypothetical scenario)
- [ ] **Worked examples** (step-by-step demonstration)
- [ ] **Counterexamples** (cases where principle doesn't apply)

**Total illustrations:** ______

---

**Illustration effectiveness:**

| Illustration | Type | Clarifies Concept? | Enhances Understanding? |
|:-------------|:----:|:------------------:|:-----------------------:|
| [Example 1] | | ☐ Yes ☐ No | ☐ Yes ☐ No |
| [Example 2] | | ☐ Yes ☐ No | ☐ Yes ☐ No |

---

## SCORING RUBRIC (0-5 Scale)

### Score 5: Exemplary Reasoning Depth
**Criteria (ALL must be met):**
- [ ] Majority (>60%) of explanations at Level 3-4 (multi-step or theoretical)
- [ ] All major causal claims include mechanism explanations
- [ ] Multiple theories explicitly integrated and applied
- [ ] Logical coherence throughout (no fallacies)
- [ ] Complete causal chains shown (no critical gaps)
- [ ] Appropriate causal vs. correlational language
- [ ] Concrete examples illustrate abstract concepts

**Characteristic features:**
- Explains not just WHAT but WHY and HOW
- Traces causal chains through intermediate steps
- Grounds mechanisms in theory
- Uses precise causal language
- Provides worked examples

---

### Score 4: Strong Reasoning Depth
**Criteria:**
- [ ] Many (40-60%) explanations at Level 3-4
- [ ] Most major claims have mechanism explanations
- [ ] At least 2 theories referenced and applied
- [ ] Generally logically coherent (minimal fallacies)
- [ ] Most causal chains complete
- [ ] Mostly appropriate causal language
- [ ] Some concrete examples provided

**What's missing from Score 5:**
- Some explanations remain at Level 2 (one-step)
- Occasional explanatory gaps
- Fewer theoretical connections
- Limited illustration through examples

---

### Score 3: Adequate Reasoning Depth
**Criteria:**
- [ ] Mix of Level 2-3 explanations (20-40% at Level 3+)
- [ ] Some mechanism explanations, others missing
- [ ] 1-2 theories mentioned, may lack deep integration
- [ ] Logical but basic reasoning
- [ ] Some causal chains incomplete
- [ ] Mix of causal and correlational language
- [ ] Minimal concrete examples

**What's missing from Score 4:**
- Many assertions without mechanisms
- Shallow explanations predominate
- Limited theoretical grounding
- Gaps in causal chains
- Few illustrative examples

---

### Score 2: Weak Reasoning Depth
**Criteria:**
- [ ] Mostly Level 1-2 explanations (surface to basic)
- [ ] Few mechanism explanations provided
- [ ] Theory rarely mentioned or not integrated
- [ ] Some logical gaps or unclear connections
- [ ] Causal chains often incomplete
- [ ] Ambiguous causal language
- [ ] Rare use of examples

**Key problem:**
- States relationships without explaining mechanisms
- Superficial "because" statements without depth
- Missing intermediate reasoning steps

---

### Score 1: Poor Reasoning Depth
**Criteria:**
- [ ] Mostly Level 0-1 (assertions or surface correlation)
- [ ] No mechanism explanations
- [ ] No theoretical grounding
- [ ] Logical coherence weak or absent
- [ ] No causal reasoning
- [ ] No examples or illustrations

**Key problem:**
- Descriptive listing without explanatory depth
- "What" without "why" or "how"

---

### Score 0: No Reasoning
**Criteria:**
- [ ] Pure assertion
- [ ] No attempt at explanation
- [ ] No logical structure

---

## OUTPUT FORMAT

Provide your evaluation in this exact structure:

---

### REASONING DEPTH EVALUATION: [Response Label]

#### EXPLANATION LEVEL DISTRIBUTION

**Total major claims/explanations:** [count]

| Level | Count | % | Representative Example |
|:---|:---:|:---:|:---|
| Level 4 (Theoretical) | | | [quote] |
| Level 3 (Multi-step) | | | [quote] |
| Level 2 (One-step) | | | [quote] |
| Level 1 (Surface) | | | [quote] |
| Level 0 (Assertion) | | | [quote] |

**Average explanation level:** [calculate]

---

#### MECHANISTIC REASONING

**Claims with mechanism explanations:** [count] / [total claims]

**Mechanism quality:**
- Complete mechanisms (Level 4): [count]
- Good mechanisms (Level 3): [count]
- Basic mechanisms (Level 2): [count]
- Weak/absent (Level 1): [count]

**Best mechanism example:**
> [Quote exemplary mechanism explanation]

**Why it's strong:** [Explain: shows process, multiple steps, theoretical grounding]

---

#### CAUSAL LANGUAGE ANALYSIS

**Language distribution:**
- Causal (implies mechanism): [count]
- Correlational (association only): [count]
- Ambiguous: [count]

**Inappropriately causal claims:** [count]
- [List any correlational data described causally]

---

#### LOGICAL COHERENCE

**Argument structure quality:** [Excellent/Good/Fair/Poor]

**Logical fallacies detected:** [count]
- [List any fallacies with examples]

**Overall logical flow:** [Coherent/Mostly coherent/Some gaps/Incoherent]

---

#### THEORETICAL INTEGRATION

**Theories referenced:** [count]
- [List each theory]

**Integration quality:**
- Deeply integrated (Level 3): [count]
- Applied but not explained (Level 2): [count]
- Name-dropped only (Level 1): [count]

**Example of strong theoretical integration:**
> [Quote]

---

#### EXPLANATORY COMPLETENESS

**Complete causal chains:** [count] / [total complex claims]

**Completeness rate:** [X]%

**Explanatory gaps identified:** [count]

**Example of complete explanation:**
> [Quote showing full causal chain A→B→C→D]

**Example of incomplete explanation (if any):**
> [Quote showing gap A→???→D]

---

#### ILLUSTRATIONS & EXAMPLES

**Total concrete illustrations:** [count]
- Concrete examples: [count]
- Analogies: [count]
- Thought experiments: [count]
- Worked examples: [count]
- Counterexamples: [count]

**Example effectiveness:** [High/Medium/Low]

---

#### SCORING ASSESSMENT

**Reasoning Depth Score: [0-5]**

**Justification (2-3 sentences):**
[Explain score based on explanation levels, mechanism quality, theoretical grounding, and logical coherence]

---

#### COMPARISON TO RUBRIC

| Criterion | Present? | Quality/% |
|:----------|:--------:|:----------|
| Level 3-4 explanations (>60% for score 5) | ☐ Yes ☐ No | [X]% |
| Mechanism explanations for major claims | ☐ Yes ☐ No | [X / Y] |
| Theories integrated (≥2 for score 4+) | ☐ Yes ☐ No | [count] |
| Logical coherence | ☐ Yes ☐ No | [fallacy count] |
| Complete causal chains | ☐ Yes ☐ No | [X]% |
| Appropriate causal language | ☐ Yes ☐ No | [assessment] |
| Concrete examples | ☐ Yes ☐ No | [count] |

---

#### REPRESENTATIVE COMPARISON

**Shallowest explanation:**
> [Quote example of assertion or surface explanation]

**Deepest explanation:**
> [Quote example of theoretical, multi-step explanation]

**Contrast:** [Explain the difference in reasoning depth]

---

## CRITICAL INSTRUCTIONS

1. **Distinguish levels carefully:** Level 2 (one-step) vs. Level 3 (multi-step) is crucial
2. **Count mechanisms:** How many claims actually explain HOW, not just WHAT
3. **Check theoretical grounding:** Are theories integrated or just name-dropped?
4. **Verify logic:** Do conclusions actually follow from premises?
5. **Identify gaps:** Are intermediate steps shown or assumed?

---

## READY TO EVALUATE?

I will now provide you with an AI-generated response to evaluate for Reasoning Depth.

**RESPONSE TO EVALUATE:**

[Paste response here]

---

Please provide your detailed Reasoning Depth evaluation following the output format above.