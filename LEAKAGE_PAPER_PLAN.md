# Paper 1 Plan: How much does data leakage inflate reported accuracy in SLE transcriptomic prediction studies?

**Decided (2026-10-01):**
- Target journal: ***Briefings in Bioinformatics***.
- **No contact with authors.** Reproducibility is judged from the published materials alone: the paper, its supplements, and any publicly linked code or data.

**How to read the markers:**
- **⚠ D#** marks a decision that needs your input. All of them are collected in [Section 8](#8-open-decisions).
- *(unverified)* marks a claim not confirmed from a primary source. GEO accessions and PMIDs cited here were checked against NCBI on 2026-10-01.

---

## Summary

Many published SLE "biomarker" papers report near-perfect accuracy from blood transcriptomes (AUC 0.95–1.0), usually with a pipeline of differential expression → WGCNA → machine-learning feature selection → ROC. Several such papers we read show forms of **data leakage** that are known to inflate accuracy:
- genes or modules chosen on the full dataset before cross-validation
- batch correction run on pooled training and test data
- repeated visits from the same patient counted as independent samples
- "external" validation sets that share samples with the training data

What isn't known is **how common these problems are in the SLE literature, or how much they inflate accuracy.**

**Design:**
1. **Prevalence:** a systematic review that codes each eligible paper for specific leakage types.
2. **Magnitude:** re-run a systematically chosen set of published pipelines, first **as published** and then **with the leaks removed**, and measure the change in performance.
   - Remove one leak at a time to see which leaks contribute most.
   - Run each pipeline on **permuted labels** to show what it scores when there's no signal at all.
   - Re-run papers with no apparent leakage as **controls**.
3. **Analysts:** two AI coding agents from different vendors (e.g. OpenAI Codex and Claude Code) each reconstruct every pipeline independently, from a methods packet with the **reported results removed**. A human audits every reconstruction, and a human independently reconstructs **5 papers** as a benchmark (Section 4.8).
4. **Resource:** a catalog of overlapping SLE GEO datasets, plus a reusable leakage-audit checklist and pipeline.

**Why it matters.** Leakage in general is well documented (Ambroise & McLachlan 2002; Kapoor & Narayanan 2023; Whalen 2022). But no study has measured it **by re-running published pipelines in this field**. The SLE transcriptomic biomarker literature is large and keeps growing, and its claims feed later studies and grant proposals.

**Expected size and effort:** a short paper; up to about 30 re-run pipelines (limited by human audit time); about 5–6 months.

---

## 1. Background

### 1.1 What leakage looks like in this literature

Examples from the literature review for this project. All are public-data studies. The PMIDs were verified; the methods details come from the review agent's reading of the full text.

| Paper | Reported performance | Leakage-relevant practice |
|---|---|---|
| Li W 2023 *Front Immunol* (PMID 37313407) | SVM 5-fold CV AUC **0.998**; external 0.943 | GSE61635 + GSE50772 merged with `sva`, then WGCNA and gene selection on the full training set **before** CV |
| Meng 2022 *Front Immunol* (PMID 36059547) | Single gene (MX2) AUC 0.958–0.976 | GSE121239 and GSE45291 used as if separate, with identical counts (20 HC / 292 SLE); both come from the same cohort and share arrays. WGCNA soft-threshold power **30**. |
| Zhao X 2023 *BMC Immunol* (PMID 37950194) | External single-gene AUC 0.694–0.898 | ComBat on merged training data; the external set counts GSE65391's 924 **samples**, which are repeat visits from 158 patients |
| Leventhal 2023 *iScience* (PMID 37860757) | Active vs inactive 0.842; LN 0.894 | ComBat on merged data, then a **random** 70/30 split; authors acknowledge no study-level validation |
| Kegerreis 2019 *Sci Rep* (PMID 31270349) | Module AUC 0.73–0.77 within studies, 0.55–0.75 across studies | Mostly sound (leave-one-study-out). Expression was z-scored within each dataset before CV, a mild leak. **Candidate control paper.** |

The general pattern was shown long ago for microarrays. Ambroise & McLachlan 2002 (*PNAS*, PMID 11983868) found that selecting genes before cross-validation can give near-zero estimated error even when there's no real signal.

### 1.2 Dataset overlaps already found

Treating overlapping datasets as independent "external validation" is a specific, under-recognized leak in this field. Overlaps confirmed during this project, from series-matrix sample annotations:

- **GSE49454 is contained in GSE72326.** The same 157 SLE and 20 HC arrays were re-deposited under new sample IDs.
- **GSE45291, GSE121239 and GSE224705 share one cohort.** All have the same 20 HC arrays, 61 SLE CEL files are shared between GSE45291 and GSE121239, and 41 of GSE121239's 65 patients reappear in GSE224705.
- **GSE88884** holds the baseline samples of GSE88885 and GSE88886 (superseries GSE88887).
- **GSE81622** is a sub-series of GSE82221.
- **GSE65391** has 924 SLE arrays from only 158 patients (longitudinal); its controls include technical replicates.

### 1.3 Prior work and what's new here

| Prior work | What it established | Gap we fill |
|---|---|---|
| Ambroise & McLachlan 2002 *PNAS* (PMID 11983868) | Gene-selection bias in microarray classification | Not specific to current SLE pipelines (WGCNA, ComBat, hub genes) |
| Ioannidis et al. 2009 *Nat Genet* (PMID 19174838) | Of 18 published microarray analyses, 2 were reproduced in principle, 6 partially and 10 not at all, mostly because of unavailable data or under-specified processing | About reproducibility, not leakage. It is the precedent for judging reproducibility from published materials alone. |
| Kapoor & Narayanan 2023 *Patterns* (PMID 37720327) | Leakage found in 17 fields (294 papers); an 8-type taxonomy; "model info sheets"; a re-run of civil-war prediction studies showing complex ML no better than logistic regression once errors are fixed | **Precedent for the re-run-and-correct design**, but not in genomics. Our L1–L7 codes should map onto their 8 types. |
| **Khoo & Dhillon 2026 *Brief Bioinform*** (PMID 42184107) | Narrative review of 63 AI transcriptomic-biomarker studies in COVID-19. Notes "risk of data leakage or circular validation" qualitatively, and proposes a framework. | **Closest analogue, in our target journal.** It's qualitative: no re-runs, no measured inflation, no risk-of-bias tool, no dataset-overlap check. It also says the studies "lacked sufficient methodological detail… for reproducibility assessment". We measure what it could only flag. |
| Whalen et al. 2022 *Nat Rev Genet* (PMID 34837041) | Pitfalls of machine learning in genomics | A review, with no field-level measurement |
| PROBAST (Wolff 2019, PMID 30596876) and TRIPOD+AI (Collins 2024 *BMJ*, PMID 38626948) | Risk-of-bias and reporting standards for prediction models | Generic; not used for transcriptomic biomarker papers |

**New here:**
- (i) Prevalence of each leakage type in SLE transcriptomic prediction papers.
- (ii) **Measured** inflation, from re-running pipelines as published and corrected, attributed to individual leaks.
- (iii) Permuted-label demonstrations on real published pipelines.
- (iv) An overlap catalog of SLE GEO datasets.

### 1.4 Positioning and framing for *Briefings in Bioinformatics*

Two cautions, given that Khoo & Dhillon 2026 is in the same journal and that leakage frameworks already exist:

1. **Don't let it read as "another review".**
   - Title, abstract, key points and cover letter should lead with **measured inflation from re-running published pipelines** (Δ_leak, attribution by leakage type, shuffled-label results), not with "review".
   - Cite Khoo & Dhillon 2026 early, as the qualitative precursor. They flagged a "risk of data leakage" and couldn't assess reproducibility; we measure both.
   - The prevalence coding (O1) supports the re-runs (O2–O5); it shouldn't be presented as the main contribution.
2. **Don't propose yet another framework.**
   - Khoo & Dhillon already propose a workflow, and Kapoor & Narayanan 2023 have an 8-type leakage taxonomy with "model info sheets".
   - Map our L1–L7 codes explicitly onto Kapoor & Narayanan's 8 types (a mapping table in the paper).
   - Present our checklist as a **transcriptomics-specific version of model info sheets**, adding what's specific to GEO data: WGCNA and module selection, ComBat on pooled data, repeated visits, and overlapping GEO series. Present it as an extension, not a new framework.

---

## 2. Objectives and hypotheses

| # | Objective | Primary estimand |
|---|---|---|
| O1 | **Prevalence:** how common is each leakage type? | Proportion of eligible papers (95% CI) with each type rated *present*, *absent* or *unclear* |
| O2 | **Magnitude:** how much do leaks inflate performance? | Per paper: **Δ_leak = AUC(reproduced as published) − AUC(corrected)**. Pooled across papers with a random-effects model. |
| O3 | **Attribution:** which leaks matter most? | Δ for each leakage type from one-at-a-time correction |
| O4 | **Null behaviour:** what do leaky pipelines score with no signal? | Distribution of AUC on permuted labels, as published vs corrected |
| O5 | **Reproducibility:** can reported numbers be reproduced at all? | **Δ_repro = AUC(reported) − AUC(reproduced as published)**; proportion of papers reproducible within ±0.05 |
| O6 | **Resource** | Overlap catalog of SLE GEO datasets; audit checklist; open pipeline |
| O7 | **AI analysts:** can AI agents reconstruct published pipelines faithfully, and how close are they to a human? | AI–AI agreement (pipeline steps matched; \|ΔAUC\|); rate of silent corrections caught in audit; AI–human \|ΔAUC\| and Δ_leak difference on the 5 benchmark papers (descriptive) |

**Hypotheses:**
- **H1:** among papers with ≥1 leak rated *present*, the pooled Δ_leak is > 0.
- **H2:** Δ_leak in the control papers (no apparent leakage) is ≈ 0, and smaller than in the leaky papers.
- **H3:** with leaks left in, permuted-label AUC is substantially above 0.5; after correction it is ≈ 0.5.
- **Exploratory:** inflation is largest for gene or module selection on the full data, and for overlapping validation sets. It grows with the number of candidate genes and shrinks with sample size.

The earlier claim that "most published accuracy is inflated" is a **hypothesis this paper tests**, not an established fact. It was based on about a dozen papers.

---

## 3. Systematic review (O1)

### 3.1 Eligibility

- **Include:** primary research papers that:
  - use human SLE **bulk** transcriptomic data (microarray or RNA-seq; blood, or tissue ⚠ **D7**)
  - build a **diagnostic or prognostic classifier or biomarker panel**: SLE vs controls, disease activity, lupus nephritis (LN), flare, or treatment response
  - report a performance metric: AUC, accuracy, sensitivity/specificity, or C-index
- **Exclude:** single-cell-only studies; reviews; studies with no performance metric; studies using only non-public data. Non-public-data studies are excluded from the re-runs, but they're still coded for prevalence.
- **Dates:** 2015 to the search date ⚠ **D2**. **Scope:** SLE only, as a small paper ⚠ **D1**.

### 3.2 Search

- **Databases:** PubMed and Europe PMC (Embase if available). Search the GEO accession numbers of the major SLE datasets as well as keywords.
- **Draft PubMed query** (to be refined and piloted):
  - `("lupus erythematosus, systemic"[MeSH] OR "systemic lupus"[tiab] OR SLE[tiab] OR "lupus nephritis"[tiab]) AND (transcriptom*[tiab] OR microarray[tiab] OR "gene expression"[tiab] OR RNA-seq[tiab] OR GEO[tiab] OR WGCNA[tiab]) AND (diagnos*[tiab] OR biomarker*[tiab] OR "machine learning"[tiab] OR classifier[tiab] OR "ROC"[tiab] OR AUC[tiab] OR "hub gene*"[tiab] OR LASSO[tiab] OR "random forest"[tiab] OR SVM[tiab])`
- **Yield** (draft query, PubMed, 2015–2026, run 2026-10-01): **819 records**. A narrower query (lupus + hub gene/WGCNA/ML + GEO) returns **159**. The broad query will include many mechanistic papers, so screening precision will be known after the pilot.
- **Related reviews found so far:** the only systematic review of machine learning for SLE diagnosis that turned up has been **retracted** (*Comput Intell Neurosci* 2023, PMID 37829908). Prior-art searching continues as part of the systematic search.

### 3.3 Coding

- Two independent raters code every eligible paper using a piloted form. Disagreements go to a third rater. Report Cohen's κ for each item.
- **Leakage types** (adapted from Kapoor & Narayanan 2023, and specific to this literature):

| Code | Leakage type | Examples in this literature |
|---|---|---|
| **L1** | Feature selection using test data | DEGs, WGCNA modules, trait-correlated modules or hub genes chosen on all samples, then CV or validation on the same samples |
| **L2** | Preprocessing fit on training + test together | ComBat or sva on merged discovery + validation data; normalization or z-scoring across pooled sets |
| **L3** | Non-independent samples across the split | Repeated visits or technical replicates of one person in both training and test |
| **L4** | Overlapping "external" validation | Validation dataset shares samples with the training data (Section 1.2) |
| **L5** | Model or hyperparameter selection on the test set | Choosing genes, models or cutoffs by test performance; reporting the best of many models |
| **L6** | No held-out evaluation | Resubstitution or training-set AUC reported as performance |
| **L7** | Cohort-dependent scores computed on pooled data | GSVA or ssGSEA run on train + test together |

- Each type is rated **present**, **absent** or **unclear**. *Unclear* is analysed as its own category, because reporting quality is itself a finding.
- **Also coded:**
  - datasets used (GEO IDs) and their roles
  - number of SLE and control samples and patients
  - number of candidate features
  - methods: WGCNA, LASSO, SVM-RFE, random forest, etc.
  - whether code is shared; software versions; random seeds
  - which performance metrics are reported
  - a PROBAST analysis-domain rating

---

## 4. Re-analysis of published pipelines (O2–O5)

### 4.1 Which papers to re-run

To avoid cherry-picking:
1. From the eligible set, identify **re-runnable** papers using pre-specified criteria:
   - all data public
   - samples identifiable
   - pipeline steps and key parameters described
2. Classify each re-runnable paper as **leaky** (≥1 of L1–L7 present) or **control** (none present).
3. Re-run **all** re-runnable papers if there are about 30 or fewer, the limit set by human audit time. Otherwise take a **pre-specified random sample**, stratified to include **at least 3 controls** ⚠ **D3**.
4. Report the funnel: eligible → re-runnable → re-run → reproduced.

The papers in Section 1.1 go into the pool like any others. They are not chosen by hand.

### 4.2 Three numbers per paper

| Number | Definition |
|---|---|
| **Reported** | The AUC (or other primary metric) stated in the paper |
| **Reproduced as published** | Their pipeline, reconstructed from the published materials by the AI analysts, then audited and adjudicated by a human (Section 4.8); run on the same data, leaks included |
| **Corrected** | The same pipeline with **only** the leaks fixed |

- **Δ_repro = reported − reproduced.** This measures reproducibility.
- **Δ_leak = reproduced − corrected.** This measures inflation from leakage.
- Measuring Δ_leak from our reproduction, not from the reported number, keeps reproduction error out of the leakage estimate.

### 4.3 Rules for the corrected pipeline

**Minimal change:** keep the paper's datasets, genes, models, hyperparameter grids and metrics. Change only what's needed to remove the leak:

| Leak | Correction |
|---|---|
| L1 | Move DEG, WGCNA and module/hub-gene selection **inside** each training fold. Test samples get projected module eigengenes or the selected genes from the training fold only. |
| L2 | Fit ComBat, sva and normalization on training data only, and apply them to test data. For external sets, process each cohort separately, without labels. |
| L3 | Split folds by patient; one visit per patient where the paper's design allows. |
| L4 | Remove overlapping samples. If nothing independent remains, validate on an independent cohort with the same outcome and tissue (documented), or report "no valid external test". |
| L5 | Nested CV for all selection and tuning. |
| L6 | Add nested CV. |
| L7 | Fit scoring parameters on training data only, or use a truly single-sample score (singscore). |

**One leak at a time:** fix each leak alone, then all of them together. That gives a Δ for each leakage type, and shows whether leaks interact.

### 4.4 Permuted labels (O4)

- Shuffle the outcome labels (within cohort, keeping class balance) and run the full pipeline both **as published** and **corrected**.
- 100–200 permutations per paper, as compute allows. Report the AUC distribution.
- **Expectation:** as published, AUC sits well above 0.5; corrected, it centres at 0.5.

### 4.5 Repeatability and ambiguity

- Random 70/30 splits and CV are repeated with **≥ 50 seeds**, and reported as distributions.
- Every gap in a methods section gets an **assumption log** entry: preprocessing, probe collapsing, thresholds, software versions. The AI analysts and the human benchmark analyst all apply the same registered default rules.
- Where an assumption could change results, run the plausible variants and report their range.
- **No contact with authors (decided).** Each paper is reproduced only from its published materials: main text, supplements, and code or data the paper links publicly. That matches the stance that a published analysis should be reproducible as it stands, and it makes O5 a direct measure of that.

### 4.6 Analysis

- **O1:** proportion of papers with each leakage type, with Wilson 95% CIs; also by year, journal type and method (WGCNA vs not).
- **O2:** Δ_leak per paper, with a bootstrap CI over seeds and folds. Pool with a random-effects meta-analysis on the logit-AUC scale; compare leaky vs control papers (H1, H2).
- **O3:** per-type Δ from one-at-a-time correction; waterfall plot per paper.
- **O4:** permuted-label AUC distributions, as published vs corrected (H3).
- **O5:** Δ_repro distribution; proportion of papers reproducible within ±0.05 AUC.
- **Exploratory:** meta-regression of Δ_leak on the number of candidate features, sample size and leakage type.

### 4.7 Pre-registration (OSF), in two stages

We register the **rules**, not the results of applying them. Choosing the papers and setting each one's configuration then become mechanical applications of rules fixed in advance.

| Stage | When | What is registered |
|---|---|---|
| **1. Protocol** | After piloting the coding form on about 10 papers; **before** full screening and coding and before any re-runs | Search strategy and eligibility; coding manual (L1–L7 decision rules); re-runnability criteria; sampling rule for re-runs, **including the random seed**; definition of control papers; default rules for resolving ambiguous methods (Section 4.5); minimal-correction rules (Section 4.3); estimands and analysis plan (Section 4.6); **AI-analyst protocol** (Section 4.8): tools and versions, prompts, packet redaction rules, sandbox rules, audit checklist, adjudication rules, and the seed for choosing the 5 human-benchmark papers |
| **2. Addendum** | After papers are selected and each paper's **as-published configuration** is written, audited and adjudicated; **before** running anything | List of selected papers; for each, the AI-A, AI-B and adjudicated configurations, assumption logs, audit logs and planned corrections; the human-benchmark configurations for the 5 papers |

- Pilot papers are re-coded under the registered manual, like every other paper.
- Each configuration is written from the paper alone, before any of its results (as published or corrected) are seen. Configuration files are committed to git as well; the OSF timestamp is the independent record.
- **Deviations** after stage 2 are allowed, and are reported with their reasons in the paper.
- The registration can stay private until publication.

### 4.8 AI analysts

Two AI coding agents act as independent analysts for **reconstructing pipelines**. Humans prepare the inputs, audit every output, adjudicate disagreements, and benchmark the AIs against a human reconstruction on 5 papers.

**Why this design:**
- **Blinding to reported results.** The agents work from packets with the results removed, so they can't drift toward a known target AUC. Human analysts can't easily be blinded this way.
- **A strict test of reproducibility from published materials alone.**
- **A full record:** prompts, transcripts, model versions and generated code.
- **Scale:** more papers can be re-run than a human team could manage.

**Roles:**

| Task | Done by | Human role |
|---|---|---|
| Prepare methods packets (Section 4.8.1) | Human **packet preparer** (has read the full papers; does no reconstruction) | — |
| As-published reconstruction | **AI-A** and **AI-B**, independently | Audit and adjudication |
| Corrected version (minimal-correction rules, Section 4.3) | Each AI, starting from its own as-published configuration | Audit: only leak-related steps may differ |
| Benchmark reconstruction of 5 papers | Human **benchmark analyst**, independently | — |
| Leakage coding for prevalence (L1–L7) | Human primary rater; AI second rater ⚠ **D10** | Adjudication |

#### 4.8.1 Inputs: blinded methods packets

- **Contents:** full text and supplements with reported performance **removed**: abstract numbers, AUC, accuracy, sensitivity and specificity values in the text, and performance tables, figures and ROC curves. Also the list of data accessions, and any code or data the paper links publicly.
- The redactions follow registered rules, and each packet keeps a log of what was removed.
- The packet preparer doesn't reconstruct, audit or adjudicate any paper.

#### 4.8.2 Instructions (identical for both agents; registered text)

The prompt will include:
- Reproduce the pipeline **exactly as described, including steps that may be methodologically flawed. Do not improve, correct or modernize anything.**
- Use only the packet. Don't search for the paper, its code or its results, and don't rely on recollection of the paper.
- Where the methods are ambiguous, apply the registered default rules. Record every assumption in the assumption log, citing the passage in the packet.
- Express the pipeline as a configuration of the shared pipeline (Section 6), adding paper-specific code only where no building block fits.
- Don't estimate or report expected performance.

#### 4.8.3 Environment

- Each agent runs in its **own sandbox**, with a separate repository or container, and never sees the other agent's outputs.
- Network access is limited to data and package sources (NCBI/GEO, CRAN, Bioconductor). No general web browsing; network calls are logged.
- Exact model names, versions and dates are recorded. All reconstructions are run within a short, fixed time window.
- Optional: run each agent a second time on the 5 benchmark papers to measure run-to-run variability.

#### 4.8.4 Human audit (every paper, both agents)

The audit happens **before anything is executed**. It checks the configurations against the packet, not against results. Checklist:
1. Every step described in the packet is implemented, in the stated order.
2. **No silent corrections.** No step appears that the packet doesn't describe: nested CV, selection inside folds, ComBat dropped, patient-level splits, added regularization.
3. Data and sample selection match the packet: series, groups, exclusions, visits.
4. Assumption-log entries follow the default rules and cite the packet.
5. The corrected configuration differs from the as-published one **only** in leak-related steps.

The auditor may change a configuration only to fix a breach of the instructions, and every change is logged. The rate of silent corrections and other breaches is reported (O7).

#### 4.8.5 Adjudication

- If AI-A and AI-B agree in substance, that configuration is used.
- If they differ, the adjudicator decides which one follows the packet and the default rules.
- If both are defensible readings of ambiguous text, both are kept as variants and their spread is reported as the ambiguity range (Section 4.5).
- **Primary analysis:** adjudicated configurations for all papers. **Reported alongside:** results from AI-A alone and AI-B alone.

#### 4.8.6 Human benchmark (5 papers)

- **Selection:** 5 papers drawn at random from the re-run set with a registered seed, including at least 1 control paper if any exist.
- **Blinding:** the benchmark analyst works from the **same redacted packet**, independently. They see neither the full paper nor any AI output for those papers until their reconstruction is frozen, and they don't audit those 5 papers.
- **Comparison:**
  - agreement step by step (data and samples, preprocessing, feature selection, model, validation)
  - |ΔAUC| for the as-published and corrected versions
  - the difference in Δ_leak

  Agreement means |ΔAUC| ≤ 0.05, the same threshold as O5. With n = 5, results are **reported paper by paper and descriptively**, with no formal test.
- **Sensitivity analysis:** replace the adjudicated AI configurations with the human ones for these 5 papers and re-estimate pooled Δ_leak.

#### 4.8.7 Disclosure and records

- Release all prompts, transcripts, model versions, sandbox specifications, generated code, audit logs and adjudication decisions.
- AI tools are disclosed in the Methods, and aren't authors.
- **To do:** check Oxford University Press's policy on AI use for *Briefings in Bioinformatics*.
- **Related work to check before citing:** emerging benchmarks of AI agents reproducing published analyses (e.g. CORE-Bench, PaperBench) *(unverified)*.

---

## 5. Overlap catalog of SLE GEO datasets (O6)

1. List all human SLE expression series on GEO through E-utilities, filtered for SLE and for expression data.
2. Detect shared samples in three ways:
   - (a) match GSM titles and characteristics
   - (b) match CEL file names and checksums (Affymetrix)
   - (c) array-level correlation > 0.99 across series on the same platform, using shared genes
3. Publish a table of overlap clusters and the safe-to-combine relationships between series.

This also serves paper 2.

---

## 6. Implementation

- **A shared, modular R pipeline:**
  - preprocessing: `GEOquery`, `limma`, `sva`
  - modules: `WGCNA`
  - selection and models: `glmnet` (LASSO), SVM-RFE (`e1071`/`caret`), `randomForest`/`ranger`, `Boruta`
  - scoring: `pROC`, `singscore`/`GSVA`
- Every step has a **fold-aware wrapper** that takes `train_idx` and `test_idx`. "As published" vs "corrected" is a configuration switch, not separate code.
- Evaluate `nestedcv` (Lewis et al. 2023 *Bioinform Adv*, PMID 37113250) as the engine for the corrected arm. It does nested CV with feature selection inside the folds, it's designed for transcriptomics, and it comes from a rheumatology group.
- **One configuration file per paper** (datasets, sample filters, steps, parameters), plus a short paper-specific script where needed, plus the assumption log.
- `targets` + `renv` for reproducibility; seeds recorded.
- **The shared pipeline is written and unit-tested by humans before the AI reconstructions start.** The AI analysts write configurations against it, which keeps reconstructions comparable and auditable. Their independence lies in how they read each paper, not in re-implementing basic steps.
- Separate sandboxes for AI-A and AI-B, with network access restricted and logged (Section 4.8.3).
- Release everything publicly, including a **leakage-audit checklist** based on L1–L7 that authors and reviewers can use.

---

## 7. Expected outputs

| Item | Content |
|---|---|
| Fig. 1 | PRISMA flow diagram |
| Fig. 2 | Prevalence of each leakage type (present / unclear / absent), with CIs |
| Fig. 3 | **Main figure:** dumbbell plot per paper, reported → reproduced → corrected AUC; leaky vs control papers |
| Fig. 4 | Inflation by leakage type (one-at-a-time correction) |
| Fig. 5 | Permuted-label AUC distributions, as published vs corrected |
| Fig. 6 | AI analysts: AI-A vs AI-B agreement across all papers; AI vs human on the 5 benchmark papers; silent corrections caught in audit |
| Table 1 | Coding results for all eligible papers (supplement) |
| Table 2 | Overlap catalog of SLE GEO datasets |
| Supplement | Per-paper configurations, assumption logs, code, leakage-audit checklist |

---

## 8. Open decisions

| # | Decision | Options | Recommendation |
|---|---|---|---|
| **D1** | Scope | SLE only / all autoimmune; all ML methods / WGCNA-based only | SLE only, all transcriptomic ML methods; report WGCNA papers as a subgroup |
| **D2** | Date range | 2015–present / 2010–present | 2015–present (the GEO + ML era) |
| **D3** | Number of re-runs and how to sample them | All re-runnable / random sample | With AI analysts, the limit is human audit time (about 1 day per paper). Re-run all re-runnable papers up to about 30; above that, a stratified random sample with ≥ 3 controls. |
| ~~D4~~ | Contact authors? | — | **Decided: no.** Reproducibility judged from published materials only |
| **D5** | Name papers in the main text? | Named / supplement only | Named in the supplement table; aggregate results in the main text; neutral tone, no claims about intent |
| ~~D6~~ | Venue | — | **Decided: *Briefings in Bioinformatics*.** To do: confirm article type and length limits in the author guidelines. Fallback: *Lupus Science & Medicine*. |
| **D7** | Include kidney-tissue studies? | Blood only / blood + tissue | Blood + tissue for prevalence; re-runs may focus on blood |
| **D8** | Primary metric | AUC only / AUC + accuracy | AUC primary; accuracy when it's the only metric a paper reports |
| **D9** | Human roles | Packet preparer; auditor/adjudicator; benchmark analyst (5 papers); leakage-coding rater(s) | Packet preparer = PI (has read the full papers). Auditor/adjudicator = student. Benchmark analyst = a second trainee, who is neither preparer nor auditor for those 5 papers. |
| **D10** | AI role in leakage coding (prevalence) | Human primary + AI second rater / two AIs + human adjudication / humans only | Human primary + AI second rater, with every disagreement adjudicated by a human. Report human–AI agreement (κ). |
| **D11** | AI tools | Which agents and versions | Two vendors (e.g. OpenAI Codex, Claude Code), versions fixed at Stage 1 |
| ~~D12~~ | Human benchmark | — | **Decided: a human independently reconstructs 5 papers** (Section 4.8.6) |

---

## 9. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Few papers are re-runnable (vague methods, non-public data) | That's a reportable finding (O5). Lower the target to ≥ 8 re-runs, and keep the prevalence arm as the main result. |
| Can't reproduce the reported numbers even as published | Δ_leak is measured from our reproduction, so it's still valid. Report Δ_repro separately. |
| Accusations of cherry-picking | Pre-specified selection; random sampling; control papers; analysis plan registered on OSF before re-runs begin |
| Corrections change more than the leak | Minimal-change rules (Section 4.3); diffs per configuration published |
| Re-runs take longer than expected | Shared modular pipeline; most papers reuse the same 4–5 steps; AI analysts do the reconstruction; budget about 1 day of human audit per paper |
| Professional sensitivity | Neutral wording; aggregate reporting; focus on practices, not people; every per-paper result backed by released code and an assumption log |
| Editors see it as "another review" like Khoo 2026 | Title, abstract and cover letter lead with *measured* inflation from re-running pipelines, not with "review". Cite Khoo directly as the qualitative precursor. Prevalence coding is secondary to the re-runs. |
| AI agents silently "fix" leaks, shrinking the measured inflation | Explicit instruction to reproduce flaws (Section 4.8.2); audit item 2 checks for silent corrections; correction rate reported |
| AI agents recall papers, code or results from training | Blinded packets; no web access; instruction not to rely on recollection; audit checks that every step traces to the packet |
| The two AIs aren't truly independent (shared training data, same prompt) | Report AI–AI agreement rather than claiming independence; human benchmark on 5 papers; human audit of all |
| Reviewers distrust AI analysts | Human audit of every reconstruction; human benchmark; full transcripts released; sensitivity analysis with the human configurations |
| Model updates or non-determinism | Versions and dates recorded; the frozen, audited **code** is the artifact, and runs deterministically |
| Journal AI policy | Check OUP's policy before Stage 1; disclose in Methods |
| Inflation turns out small | Still publishable. "Leakage is common but its impact is modest" is useful and reassuring. |
| Studies of other fields make the same point | The SLE-specific measurement and the overlap catalog are new; cite and build on Kapoor & Narayanan |

---

## 10. Timeline (proposed, about 5–6 months)

| Month | Work |
|---|---|
| 1 | Finalize the query; pilot the coding form on 10 papers; **OSF stage 1** (protocol); build the overlap catalog |
| 1–2 | Screening and double coding (O1); identify re-runnable papers and sample them with the registered seed (D3); **build and unit-test the shared pipeline**; set up the AI sandboxes |
| 2–3 | Prepare redacted packets; AI-A and AI-B reconstructions; human benchmark reconstructions of 5 papers (about 3–4 weeks, in parallel); audit and adjudication; **OSF stage 2** (addendum) |
| 3–4 | Run as published and corrected; one-at-a-time corrections; permutations |
| 4–5 | Analysis, figures, writing |
| 5–6 | Submit; release the code and checklist |

---

## 11. References (PMIDs verified 2026-10-01)

- Ambroise C, McLachlan GJ. Selection bias in gene extraction on the basis of microarray gene-expression data. *PNAS* 2002. PMID 11983868. doi:10.1073/pnas.102102699
- Collins GS et al. TRIPOD+AI statement. *BMJ* 2024. PMID 38626948. doi:10.1136/bmj-2023-078378
- Ioannidis JPA et al. Repeatability of published microarray gene expression analyses. *Nat Genet* 2009. PMID 19174838. doi:10.1038/ng.295
- Kapoor S, Narayanan A. Leakage and the reproducibility crisis in machine-learning-based science. *Patterns* 2023. PMID 37720327. doi:10.1016/j.patter.2023.100804
- Kegerreis B et al. Machine learning approaches to predict lupus disease activity from gene expression data. *Sci Rep* 2019. PMID 31270349. doi:10.1038/s41598-019-45989-0
- Khoo LY, Dhillon SK. Comparative review of artificial intelligence for transcriptomic biomarker discovery in COVID-19. *Brief Bioinform* 2026. PMID 42184107. doi:10.1093/bib/bbag249 (full text read, PMC13200535)
- Lewis MJ et al. nestedcv: an R package for fast implementation of nested cross-validation with embedded feature selection. *Bioinform Adv* 2023. PMID 37113250. doi:10.1093/bioadv/vbad048
- Leventhal EL et al. An interpretable machine learning pipeline based on transcriptomics predicts phenotypes of lupus patients. *iScience* 2023. PMID 37860757. doi:10.1016/j.isci.2023.108042
- Li W et al. Cuproptosis-related gene identification and immune infiltration analysis in SLE. *Front Immunol* 2023. PMID 37313407. doi:10.3389/fimmu.2023.1157196
- Meng XW et al. MX2: identification and systematic mechanistic analysis of a novel immune-related biomarker for SLE. *Front Immunol* 2022. PMID 36059547. doi:10.3389/fimmu.2022.978851
- Whalen S et al. Navigating the pitfalls of applying machine learning in genomics. *Nat Rev Genet* 2022. PMID 34837041. doi:10.1038/s41576-021-00434-9
- Wolff RF et al. PROBAST: a tool to assess the risk of bias and applicability of prediction model studies. *Ann Intern Med* 2019. PMID 30596876. doi:10.7326/M18-1376
- Zhao X et al. Exploration of biomarkers for SLE by machine-learning analysis. *BMC Immunol* 2023. PMID 37950194. doi:10.1186/s12865-023-00581-0
