# Initial critique of `LEAKAGE_PAPER_PLAN.md`

**Date:** 2026-10-06
**Reviewer:** Claude (AI assistant), at Pascal's request
**Reviewed version:** `LEAKAGE_PAPER_PLAN.md` at commit `7d8e586`
**Purpose:** help Pascal understand the plan well enough to refine it, and to decide (with Tyler) whether this should be the main paper.

---

## How to read this review

- Sections 1–8 follow the order Pascal asked for. Section 0 is a one-page summary.
- **"Reviewer"** with a small r means the journal's peer reviewers. "I" means me, the author of this critique.
- Jargon is defined the first time it appears, in *italics* or with a short gloss in brackets.
- *(unverified)* means I could not check the claim against a primary source. Please read the note on verification just below.

### What I could and couldn't verify

The network in this cloud session **blocked** direct access to NCBI (PubMed, PMC, E-utilities), Europe PMC, arXiv, bioRxiv, medRxiv and JMIR. I could only use a general web search, which returns titles and short snippets. That means:

- I **did not** re-check the PMIDs in the plan against NCBI. The plan says they were checked on 2026-10-01; I have no reason to doubt that, but this review adds no new confirmation.
- For **new** papers I cite below, I give the DOI or URL that the search returned. Where I only saw a title and abstract snippet, not the full text, I say so. **None of the new PMIDs here should be copied into the plan until someone checks them on NCBI**, as `CLAUDE.md` requires.
- If you want me to do this properly next time, the environment's network settings need to allow `eutils.ncbi.nlm.nih.gov`, `pubmed.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`, `arxiv.org`, `www.biorxiv.org` and `www.medrxiv.org`. You can change this under the cloud environment's settings (Network access → add allowed domains): <https://code.claude.com/docs/en/cloud-environments#network-access>.

---

## 0. Summary (one page)

**What the plan is.** A study that asks "how much does *data leakage* inflate accuracy in published SLE gene-expression prediction papers?" It counts how often leakage happens (a systematic review), then re-runs a sample of published pipelines twice, once exactly as published and once with the leaks fixed, and measures the drop in AUC. Two AI coding agents do the reconstruction work, with humans checking everything.

**My overall view.** The core idea is good and the plan is unusually careful. The three-number design (reported → reproduced → corrected) is the plan's best idea, and the GEO overlap catalog is genuinely useful and partly done already. Tyler is right that it is the hardest of the two candidates. The difficulty comes mostly from **three things stacked on top of each other**:

1. Reconstructing heterogeneous, poorly described pipelines from text alone.
2. Defining a "corrected" version of each pipeline that reviewers will accept as fair.
3. The AI-analyst layer, which is effectively a second research question (O7) with its own methods, controls and reviewers.

Any one of these is a solid student project. All three together, plus a systematic review and a catalog, is much more than 5–6 months for one student.

**Novelty is narrower than the plan says.** Since the plan was written, or not yet in it, there are close precedents: a 2026 preprint that audited the code of 32 published cancer drug-response methods and re-ran them leak-free (Asiaee et al.); a September 2026 preprint arguing that protein-panel biomarker performance is inflated across many studies (An et al.); a 2024 *Briefings in Bioinformatics* paper that re-ran published protein-interaction models and showed their accuracy came from leakage (Bernett et al.); and an August 2026 benchmark of AI agents reconstructing published computational-biology analyses, mostly transcriptomic (BixBench3). There is also now a non-retracted 2026 meta-analysis of ML for SLE diagnosis (Wang et al., *JMIR*). The SLE-specific measurement and the overlap catalog are still new, but "no one has re-run published pipelines to measure leakage in genomics" is no longer a safe sentence.

**Biggest methodological problems** (details in Section 5):

- **H2 is true by construction.** For a paper with no leaks, the "corrected" pipeline is the same as the as-published one, so Δ_leak = 0 automatically. The control comparison needs redesigning.
- **What "corrected" measures is subtle.** Moving gene selection inside the CV folds no longer evaluates the paper's gene panel. It evaluates the *procedure* that found it. That is a legitimate thing to measure, but the paper must say so clearly, or reviewers will say you didn't test their biomarker.
- **The uncertainty and pooling plan needs work.** Variation across random seeds is not sampling uncertainty. Pooling on the logit-AUC scale behaves badly when AUCs are near 1, which is exactly where these papers sit. Several papers reuse the same GEO datasets, so the papers aren't independent.
- **Permuted labels can miss L3 and L4** unless labels are permuted per patient and kept consistent across overlapping datasets.
- **The AI prompt may bias the result upward**: telling agents to "reproduce flaws" may push them to read ambiguous text as leaky.

**My top recommendation:** cut the scope to a **core paper** (Section 6, "Option A"): prevalence coding, the overlap catalog, and about 10–15 re-runs done by a human with AI as an assistant, not as a formally evaluated analyst. Move the AI-analyst comparison (O7) to a follow-up paper or a small supplement. That keeps everything that makes the paper new and drops most of the risk.

---

## 1. Plain-language explanation

### 1.1 The problem in one paragraph

Hundreds of papers take public gene-expression data from lupus (SLE) patients and healthy people, usually from GEO (the NCBI *Gene Expression Omnibus*, a public archive of expression datasets), and build a "biomarker": a small set of genes that supposedly tells SLE patients apart from controls, or active from inactive disease. They usually report an AUC of 0.95–1.0. An AUC (*area under the ROC curve*) of 1.0 means the genes perfectly rank every patient above every control; 0.5 means no better than a coin flip. The worry is that many of these numbers are too good to be true because of **data leakage**.

### 1.2 What is data leakage?

To estimate how well a model will work on **new** patients, you must test it on data it has never seen in any way. *Leakage* is when information from the test data sneaks into the model-building process, so the test is no longer a fair exam. It's like a teacher writing the exam after seeing the students' answers: the scores look great but say nothing about real ability.

A key point: leakage doesn't have to involve fitting the final model on test data. **Any** decision that used the test samples counts, such as which genes to keep, how to normalise, or which model to pick.

### 1.3 The seven leakage types (L1–L7), with examples

| Code | Plain explanation | Example from this literature | Why it inflates accuracy |
|---|---|---|---|
| **L1** Feature selection on test data | Genes were chosen using all samples, including the ones later used to test. | Run differential expression (DE) or WGCNA on all 100 samples, keep the 10 genes most different between SLE and controls, then do 5-fold CV with those 10 genes. | The genes were picked *because* they separate the groups in exactly these samples, test samples included. Even in pure noise, the top 10 of 20,000 genes will look predictive. That is the Ambroise & McLachlan (2002) result. |
| **L2** Preprocessing fit on train + test together | A data-cleaning step learned its settings from the pooled data. | ComBat batch correction run on the merged training and validation datasets. Worse if it's told the SLE/control labels as a "covariate to protect". | If ComBat is told the labels, it actively pushes the groups apart (Nygaard et al. 2016, below). Label-free pooled normalisation usually leaks much less. |
| **L3** Non-independent samples | The same person appears in both training and test. | GSE65391 has 924 arrays from 158 patients; random splits put visit 1 in training and visit 2 in testing. | The model recognises *the person*, not the disease. |
| **L4** Overlapping "external" validation | The "independent" validation dataset contains the same samples as the training dataset. | GSE49454 is contained in GSE72326; GSE121239 and GSE45291 share arrays. | The "external" test is partly a re-test on training data. |
| **L5** Model or tuning choices made on the test set | Picking the model, genes or cutoff that score best on the test data, or reporting the best of many tries. | Try LASSO, SVM, RF and XGBoost, then report the one with the highest validation AUC. | The best of many noisy scores is biased upward (a "winner's curse"). |
| **L6** No held-out test at all | Performance measured on the same data used to build the model. | "The 5-gene model had AUC 0.99 in the training set." | This is memory, not prediction. |
| **L7** Cohort-dependent scores on pooled data | Score methods whose output for one sample depends on the other samples were run on train + test together. | GSVA or ssGSEA run once on all samples. | A sample's score depends on who else is in the batch, so test samples influence the scale. Usually mild. |

Terms used above:
- **WGCNA** (*weighted gene co-expression network analysis*) groups genes into "modules" that rise and fall together, then finds modules correlated with the trait (e.g. SLE vs control). "Hub genes" are the most connected genes in the best module.
- **Differential expression (DE)**: a gene-by-gene test (often with the `limma` package) of whether expression differs between groups.
- **ComBat / sva**: methods that remove *batch effects*, technical differences between datasets or lab runs.
- **LASSO, SVM-RFE, random forest, Boruta**: common ways to pick a small gene panel from many candidates.

### 1.4 Δ_repro and Δ_leak: the three numbers per paper

For each re-run paper the plan records three AUCs:

1. **Reported**: what the paper says.
2. **Reproduced as published**: what you get when you rebuild their pipeline, leaks included, and run it on the same data.
3. **Corrected**: the same pipeline with *only* the leaks fixed.

Then:
- **Δ_repro = reported − reproduced.** "Can we even get their number?" This is about reproducibility. It mixes up vague methods, software versions, typos and random seeds.
- **Δ_leak = reproduced − corrected.** "How much of the performance came from leakage?" This is the main quantity.

**Why split it this way?** If you compared *reported* to *corrected* directly, a big gap could come from leakage or from your failure to reproduce their pipeline, and you couldn't tell which. Comparing two pipelines that *you* ran, which differ only in the leaks, isolates the leakage effect. This is the cleverest part of the plan.

### 1.5 Permuted labels

Take the dataset and randomly shuffle the SLE/control labels. Now there is, by construction, **no real signal**, so any honest pipeline should give AUC ≈ 0.5. Run the published pipeline on shuffled labels 100–200 times. If it still reports AUC ≈ 0.85, that is direct, visual proof that the pipeline manufactures accuracy out of nothing. This is very persuasive to readers who don't follow the technical argument. (Section 5.6 explains one way this can go wrong.)

### 1.6 Nested cross-validation

Normal *k*-fold *cross-validation (CV)*: split the data into *k* parts; train on *k−1*, test on the one left out; repeat so each part is tested once. That is honest **only if every decision is made inside the training part**.

*Nested CV* adds an inner loop. Inside each outer training set you run another CV to choose genes, tune hyperparameters, or pick the model. The outer test fold is touched exactly once, at the end. It is the standard fix for L1 and L5. The plan suggests the `nestedcv` R package (Lewis et al. 2023), which does this for transcriptomic data.

### 1.7 Pre-registration

*Pre-registration* means writing down your methods and analysis plan, with a timestamp, on a public registry (here OSF, the Open Science Framework) **before** you see the results. It stops you, consciously or not, from tweaking choices until you get the answer you expected. Reviewers can then check your paper against what you promised.

The plan registers in two stages:
- **Stage 1 (protocol):** the rules: how papers are found, coded, sampled, reconstructed and corrected.
- **Stage 2 (addendum):** for each selected paper, the exact configuration of the as-published and corrected pipelines, written and checked **before** anything is run.

This matters a lot here, because you are criticising other people's work. If you could adjust the "correction" after seeing the AUC drop, a hostile reviewer could argue you made the drop as big as possible.

### 1.8 The AI-analyst design

Instead of a human rebuilding each pipeline, two AI coding agents from different companies (e.g. OpenAI Codex and Claude Code) each rebuild it independently from a **methods packet**: the paper with all the results blacked out. The reasons given are:
- **Blinding:** the agent can't steer toward the reported AUC because it never sees it.
- **Scale:** more papers can be done.
- **Record:** every prompt and line of code is saved.

A human then **audits** each reconstruction before it is run. The audit checks that every step in the paper is there, that the agent hasn't silently "fixed" anything, and that the samples match. A human **adjudicates** when the two agents disagree. On 5 papers, a separate human rebuilds the pipeline from the same packet, as a benchmark to see how close the AIs get to a person.

---

## 2. Motivation and novelty

### 2.1 Is the problem real?

**Yes.** The examples in plan Section 1.1 are convincing, and the general phenomenon is old and well documented:

- Ambroise & McLachlan 2002 (*PNAS*): selecting genes before CV gives near-zero error estimates even with no signal.
- **Dupuy & Simon 2007** (*JNCI*), not in the plan: reviewed 90 microarray cancer-outcome studies; of the 28 supervised-prediction studies, **12 used biased accuracy estimates** (source: news coverage and a hosted copy of the paper found by search; *full text not read here*). This is a prevalence precedent from genomics, nearly 20 years old.
- **Castaldi, Dahabreh & Ioannidis 2011** (*Briefings in Bioinformatics*), not in the plan: 35 molecular-classifier studies with external validation. Median sensitivity/specificity were **94%/98% in cross-validation but 88%/81% in independent validation**, and most CV practices were likely to overestimate performance (abstract via search; PMID 21300697 shown in a search snippet, *not checked on NCBI*). **This is in your target journal and is the closest classic precedent.** It should be cited prominently.
- **Nygaard, Rødland & Hovig 2016** (*Biostatistics* 17(1)), not in the plan: shows that ComBat with the group variable as a covariate, in unbalanced designs, *creates* group differences. Their example went from >1,000 DE probesets to 11. **This is the key reference for L2** and should be cited for it.

**The SLE-specific gap is real.** I found no study that has systematically coded leakage in SLE transcriptomic prediction papers or measured its effect. The literature keeps growing: searches return many 2025–2026 SLE "WGCNA + machine learning" papers. There are also several **retracted** SLE machine-learning and bioinformatics papers, which suggests paper-mill activity in this niche:
- the 2023 *Comput Intell Neurosci* systematic review (confirmed retracted for "systematic manipulation of the publication process", PMC10567382)
- "Identification of Diagnostic Gene Markers and Immune Infiltration in Systemic Lupus" (retracted; PMC10719036)
- a childhood-onset SLE ML biomarker paper (retracted; PMC12540918)

These matter for eligibility: you need a rule for retracted papers (see Section 5.11).

### 2.2 How novel is the re-run-and-correct design? Closer than the plan says

The plan says no study has measured leakage "by re-running published pipelines in this field". "This field" (SLE) is still true. But reviewers at *Briefings* will know the following, and the plan should cite and position against them:

| Work | What it did | How close to us | How we still differ |
|---|---|---|---|
| **Asiaee, Strauch, Azinfar, Pal, Pua, Long & Coombes 2026**, bioRxiv, "Widespread data leakage inflates accuracy and corrupts biomarker discovery in cancer drug response prediction" (doi:10.64898/2026.02.05.704016; *abstract only seen*) | Shows that supervised feature screening before CV leaks: across 265 drugs × 1,462 cell lines, leak-free CV raised error by 16.6%. Leaky and corrected pipelines chose almost different genes (mean Jaccard 0.18). **Code-level audit of 32 published methods (2017–2024): leakage confirmed in 23 (72%).** Provides a leakage taxonomy, audit guide and reference implementation. | **Very close.** Same leak (L1), same kind of data (expression features), audit of published methods, measured inflation, and an audit guide. | Cell lines, not patients; regression, not diagnosis; they audit *code*, we reconstruct from *text*; no dataset-overlap (L4) or repeated-visit (L3) issues; not SLE. Their "biomarkers are corrupted, not just accuracy" finding is a point we should also measure (gene-list overlap between leaky and corrected runs). |
| **An, Finney, Shvetcov & Vogel 2026**, medRxiv, "Performance of protein panels is inflated across many biomarker studies" (doi:10.64898/2026.09.02.26362037, posted 2 Sept 2026; *only title, authors and a short summary seen*) | Argues that typical proteomic biomarker pipelines are broadly susceptible to leakage. Reports inflated performance across many studies, and introduces two tools to detect leakage at the code and manuscript level. | **Close, and very recent.** Same framing ("inflated across many biomarker studies"), and a manuscript-level detection tool overlaps with our coding form and checklist. | Proteomics/neurodegeneration, not transcriptomics/SLE. *(unverified: I don't know whether they re-ran published pipelines or used simulation and re-analysis of their own data. Someone needs to read the full text before we position against it.)* |
| **Bernett, Blumenthal & List 2024**, *Briefings in Bioinformatics*, "Cracking the black box of deep sequence-based protein–protein interaction prediction" | Re-ran published deep-learning PPI models. With train/test overlap removed, performance fell **to random**. | Re-runs of published models with leakage removed, **in our target journal**. | Different domain and leak type (sequence similarity). It is still a direct precedent the editor may know. |
| **Rosenblatt et al. 2024**, *Nature Communications*, "Data leakage inflates prediction performance in connectome-based machine learning models" (doi:10.1038/s41467-024-46150-w) | Five leak types, four neuroimaging datasets. **Feature-selection leakage and repeated subjects inflated performance drastically; leaky site/batch correction had only minor effects; small datasets made leakage worse.** | Same per-leak-type attribution as our O3, done by injecting leaks into the authors' own pipeline (not re-running others' papers). | Not genomics. Their result is a useful **prior**: expect L1 and L3 to matter most, L2 (label-free) and L7 little. |
| Kapoor & Narayanan 2023 (*Patterns*) | Already in the plan. | — | — |
| **Korkmaz 2026**, `bioLeak` R package (CRAN; arXiv 2604.10965) | Leakage-safe splitting, guarded preprocessing, "permutation-gap auditing", duplicate detection, for genomic and clinical data. | Overlaps with our "open pipeline and checklist" resource (O6). | Should be evaluated alongside `nestedcv`; reuse rather than rebuild where possible. |

**Bottom line on novelty.** Still novel:
- (i) the **SLE-specific** prevalence and magnitude;
- (ii) reconstruction from **published text alone**, which measures reproducibility (O5) in a way code audits can't;
- (iii) **L3 and L4 in real public data**: repeated visits and overlapping GEO series;
- (iv) **the overlap catalog**, the most clearly new and reusable piece;
- (v) the three-number decomposition separating reproducibility from leakage.

"First to re-run published pipelines and measure leakage in biomarker research" is no longer a claim we can make. The *Briefings* framing should shift from "nobody has measured this" to "this has now been shown in cell-line drug response, proteomics, PPI and neuroimaging; here is the first measurement in patient transcriptomic biomarker studies, where dataset re-use and repeated visits add leak types those studies don't have."

### 2.3 Is the "only systematic review was retracted" claim still true?

**No, it's out of date.** **Wang, Wang, Liu & Ge 2026**, *J Med Internet Res* 28:e90209 (doi:10.2196/90209), "Diagnostic Performance of Machine Learning for Systemic Lupus Erythematosus: Systematic Review and Meta-Analysis", searched up to April 2026 and included 26 studies, for SLE diagnosis, LN diagnosis and NPSLE (*abstract snippet only; I don't know whether they assessed leakage or PROBAST risk of bias*).

This actually **helps** our motivation. If that meta-analysis pooled *reported* accuracies from studies with leaks, its pooled estimate is itself inflated. That is a concrete, citable example of why measuring leakage matters downstream. Someone should read it and check which studies it pooled.

### 2.4 AI agents reproducing published analyses: verifying the plan's *(unverified)* item

The plan's Section 4.8.7 lists CORE-Bench and PaperBench as *(unverified)*. Both exist:

- **CORE-Bench**: Siegel, Kapoor, Nadgir, Stroebl & Narayanan 2024, *Transactions on Machine Learning Research*; arXiv 2409.11363. 270 tasks from 90 papers (computer science, social science, medicine). Agents must reproduce results **using the authors' own code and data**. The best agent reached 21% on the hardest level. *(Verified from the arXiv listing and TMLR entry via search.)* Note: same Princeton group as Kapoor & Narayanan's leakage work.
- **PaperBench**: Starace et al. 2025, *ICML* (PMLR vol. 267); arXiv 2504.01848. Agents replicate 20 ICML 2024 papers **from scratch**, graded against 8,316 rubric items co-written with the papers' authors. The best agent scored 21%, below ML PhD students. *(Verified from PMLR and OpenAI listings.)*

Additional work the plan should know about:

- **BixBench3**: Koch, Wassie et al. (Edison Scientific), August 2026; arXiv 2608.25286. "Evaluates whether an AI agent can reconstruct the analysis of a published computational-biology study from raw data." 20 tasks; **16 involve transcriptomics**. Scores ranged 0.00–0.48 across 13 frontier models. Agents did worse on larger datasets and longer analyses (*abstract and summary only*). **This is the closest AI precedent to our design**, so the AI part is less novel than it might look.
- **BixBench** (the original): 2025, arXiv 2503.00096 *(authors not checked)*. Open-ended bioinformatics analysis questions; early frontier models scored about 17%.
- **Brodeur et al. 2025**, accepted in *PNAS* (IZA discussion paper 17645): 288 researchers in 103 teams were randomised to human-only, AI-assisted or "AI-led" reproduction of published social-science papers. **Human-only and AI-assisted teams did about equally well, and AI-led teams were far worse** (57 percentage points lower success). Humans found more major errors. **This is the most important piece of evidence for our design decision:** it suggests "AI as assistant to a human" works, and "AI as the analyst, human as checker" doesn't yet. (See Section 5.8.)
- **Bertran, Fogliato & Wu 2026**, arXiv 2602.18710, "Many AI Analysts, One Dataset": autonomous LLM analysts given the same data and hypothesis produced widely different results. The outcomes were **steerable** by changing the model or the analyst "persona" in the prompt. That means AI-A vs AI-B disagreement is expected, and prompt wording can shift results (Section 5.8).

**Verdict on the AI part:** using AI agents to reproduce published analyses is now an active research area with benchmarks. Our design (blinded packets, two vendors, human audit, human benchmark) is more careful than most, but with **n = 5** human-benchmark papers, it can't produce a strong scientific claim about AI ability. Its main value to *this* paper is labour, not knowledge.

---

## 3. Strengths and weaknesses

### 3.1 Strengths

1. **The three-number decomposition** (Section 1.4 above). Clean, easy to explain, and it pre-empts the obvious objection "maybe you just failed to reproduce them".
2. **Pre-registering rules rather than results**, in two stages. This is the right defence against "you cherry-picked" and "you designed the correction to maximise the drop".
3. **Minimal-change correction.** Keeping the paper's own data, genes, model and metric makes Δ_leak attributable to leakage alone, at least in principle (but see Section 5.1).
4. **Concrete, verified examples** (Section 1.1) and **already-confirmed dataset overlaps** (Section 1.2). These show the problem is real in this literature, not hypothetical.
5. **The overlap catalog.** Immediately useful to anyone working with SLE GEO data, including the sister paper. It is also the part with the lowest risk.
6. **Permuted-label demonstrations.** The most persuasive single figure for non-specialist readers.
7. **Honest framing.** It says "most published accuracy is inflated" is a *hypothesis*, plans to report a small effect as a real result, and judges reproducibility without contacting authors, which makes O5 meaningful.
8. **Good positioning thinking** for *Briefings* (Section 1.4 of the plan): don't read as "another review", don't invent "another framework", map onto Kapoor & Narayanan.
9. **A thoughtful risk table.** Most of the risks I raise below are at least named there.

### 3.2 Weaknesses: what reviewers will attack first

In rough order of how likely and how damaging each is:

1. **"Your 'corrected' pipeline is a different method, not their method fixed."** The biggest attack. When you move WGCNA and gene selection inside CV folds, each fold picks different genes, so you no longer evaluate the authors' 5-gene panel. Authors will say "you didn't test our biomarker." The answer is that you tested the *procedure* that produced it, which is what their CV AUC claimed to estimate. The paper must make that argument explicitly and early (Section 5.1).
2. **"H2 is circular."** Control papers have nothing to correct, so Δ_leak = 0 by definition (Section 5.4).
3. **"Not novel: Asiaee 2026, An 2026, Bernett 2024, Rosenblatt 2024, Castaldi 2011."** Partly fair (Section 2.2). Fixable by citing them and repositioning.
4. **"Too few papers for the statistics, and they aren't independent."** About 10–30 re-runs, many reusing the same 5–10 GEO datasets, with a random-effects meta-analysis on logit-AUC, plus meta-regression on three covariates (Sections 5.2, 5.3, 5.9).
5. **"Why should I trust AI agents to reconstruct pipelines?"** Brodeur 2025 suggests AI-led reproduction is much worse than human. With n = 5 for the human benchmark, you can't show the AIs are good enough. Reviewers from the AI side will say the evaluation of the agents is too thin; reviewers from the bioinformatics side will say the AI layer is a distraction (Section 5.8).
6. **"Your reconstructions involved so many assumptions that 'as published' is your invention."** These papers are often vague. The assumption-log and variant approach is right, but if every paper needs 6–10 assumptions, the "as published" pipeline is partly yours.
7. **"SLE vs healthy control is easy anyway."** The interferon signature separates many SLE patients from healthy people. The true AUC may be about 0.9, so leakage may add only a little for SLE vs HC, and most papers are SLE vs HC. If Δ_leak is small, the headline is weak. Disease activity, LN and flare tasks are where leakage should matter most, but those papers are fewer. Also, SLE vs *healthy* is not a real clinical diagnostic problem; clinicians need SLE vs *other conditions that look like SLE*. That is spectrum bias, not leakage, but reviewers will raise it (Section 5.10).
8. **"Professional sensitivity / naming and shaming."** With per-paper dumbbell plots and released code, papers are effectively named. Handle this carefully (D5).
9. **Scope and length mismatch.** The plan calls this "a short paper", but it has 7 objectives, 6 main figures, a systematic review, a reanalysis, an AI evaluation and a resource. That is a long paper, possibly two.

---

## 4. Feasibility

All numbers below are **my rough estimates**, not measured. Treat them as a starting point to argue with, not facts.

### 4.1 How many eligible and re-runnable papers?

- The broad query gave 819 PubMed records and the narrow one 159. My guess is **100–250 eligible papers** after screening. Many of the 819 will be mechanistic, single-cell, or have no performance metric.
- **Re-runnable** needs public data (nearly all GEO-based papers have this), identifiable samples (usually yes), and pipeline steps and key parameters described (often **no**). My guess is that **30–60%** pass lenient criteria and **10–30%** pass strict ones. Either way, there are probably more than 30 candidates, so the binding limit is **human time**, as the plan says.
- **Control papers** (no leak present) may be very rare: perhaps 0–5% of the re-runnable set, i.e. **0–5 papers**. The "≥ 3 controls" rule might be impossible to meet.

### 4.2 Human time per stage

Assuming about 35 working hours a week:

| Stage | Rough hours | Notes |
|---|---|---|
| Screening (titles/abstracts, then full texts) | 50–80 | 819 titles at ~1 min each, plus full text for ~250 |
| Leakage coding (one human rater, full text + supplements, 7 items + PROBAST + extras) | 150–250 | ~1 h per paper; double if a second human codes everything |
| Overlap catalog (E-utilities, title matching, CEL checksums, cross-series correlation, write-up) | 60–120 | Part already done; correlation across platforms is fiddly |
| **Shared fold-aware R pipeline + unit tests** | **200–350** | The hardest engineering task (Section 4.4) |
| AI sandboxes, prompts, packet templates, registration documents | 80–120 | |
| Packet preparation (redaction) | 60–90 | ~2–3 h per paper × 30; plan assigns this to Tyler |
| **Audit + adjudication, 2 agents, as-published + corrected configs** | **12–20 per paper** | The plan's "about 1 day per paper" (≈8 h) looks optimistic: two configurations from two agents, checked against a long methods section and supplements, plus adjudication and corrected-config diffs |
| Running, debugging, permutations | 100–200 | Debugging failed runs on heterogeneous datasets takes longer than expected |
| Analysis, figures, writing | 150–250 | |

**Full plan with 30 re-runs:** about 1,200–1,800 hours, i.e. **8–12 months of full-time work** for one student, and longer if the student is also working on the sister project or coursework.
**With 12 re-runs:** about 900–1,300 hours, i.e. **6–9 months**.
**Option A in Section 6 (no formal AI comparison, 10–15 re-runs):** roughly 700–1,000 hours, i.e. **5–7 months**.

So **the 5–6 month timeline fits a reduced version, not the full plan.** The timeline in plan Section 10 also has the pipeline being built in month 1–2 *in parallel* with screening and coding. For one student that is in practice sequential.

### 4.3 Compute

The plan asks for ≥ 50 seeds × (as published + corrected + one-at-a-time variants) × 100–200 permutations per paper. Illustrative arithmetic, assuming a corrected pipeline with WGCNA inside 5-fold CV takes about 10 minutes per run (*a guess; it depends heavily on gene count and sample size*):

- 50 seeds × 10 min ≈ **8 hours per configuration per paper**.
- 200 permutations × 50 seeds × 10 min ≈ **1,600 hours per paper per arm**. Not feasible.
- 200 permutations × **1 seed each** × 10 min ≈ 33 hours per paper per arm, ≈ 1,000 CPU-hours for 15 papers × 2 arms. Feasible **on a cluster**, not on a laptop.

**Fix:** register that permutation runs use one seed each (the seed variation is absorbed into the permutation distribution), and 100 permutations. Ask Tyler what compute (an HPC cluster?) is available.

### 4.4 Which parts are hardest, and why

1. **The shared, fold-aware pipeline (hardest engineering).** Every step (probe-to-gene mapping, merging datasets, ComBat, DE, WGCNA with soft-threshold choice, module–trait selection, LASSO ∩ SVM-RFE ∩ RF intersection, GSVA, immune-infiltration scores, nomograms) needs a version that can be fit on training indices and *applied* to test indices. Some steps have no natural "apply to new data" version. For example, the WGCNA module structure differs per fold, so how do you match "the turquoise module" across folds? Published pipelines also contain idiosyncratic steps (cuproptosis gene lists, CIBERSORT, qPCR) that don't fit building blocks. This is where a learning student will spend most of their time.
2. **Defining "corrected" for each leak in a way reviewers accept** (Section 5.1). This is conceptual, not technical, and needs Tyler's statistical judgement.
3. **Reconstruction from vague text.** These papers frequently omit probe collapsing, normalisation, thresholds, soft-power choice, seeds and versions. Whoever reconstructs, human or AI, needs many assumptions, and the variants multiply.
4. **Audit labour.** This is the real rate limit, and it falls on the student.
5. **Coordination of independent roles.** The design needs a packet preparer, two AI agents, an auditor/adjudicator, a benchmark analyst who sees neither, and two coders. With two people (Pascal and Tyler), keeping roles independent is hard (D9).

### 4.5 What one student plus a supervisor can realistically do

- **Realistic in 5–6 months:** the systematic search and single-human coding with an AI or partial second rater; the overlap catalog; a pipeline covering the 4–5 commonest steps; **10–15 re-runs**, human-led and AI-assisted; permutation demonstrations on 5–10 of them; a modest-length paper.
- **Not realistic in 5–6 months:** 30 re-runs with dual independent AI reconstructions, full adjudication, a human benchmark by a second trainee, one-at-a-time attribution for every leak, and 200 permutations × 50 seeds.

---

## 5. Methodological issues

### 5.1 Is "minimal correction" well defined?

Partly. It is well defined for some leaks and genuinely ambiguous for others.

| Leak | How well defined? | Issue | Suggestion |
|---|---|---|---|
| L1 | **Ambiguous** | Moving selection inside folds changes *what* is evaluated: from a fixed gene panel to a gene-finding procedure. WGCNA "module eigengenes projected to test samples" needs a rule for matching modules across folds, and for choosing soft-threshold power inside each fold. Intersections ("genes chosen by LASSO ∩ SVM-RFE ∩ RF") can be empty in some folds. | State the estimand explicitly: *"the expected performance on new patients of the published procedure, as the paper's CV claimed to estimate."* Pre-register rules for empty intersections (e.g. fall back to the union, or top-*k* by LASSO), module matching, and in-fold soft-power choice. **Also report the Jaccard overlap** between the paper's genes and the genes each corrected fold selects (as Asiaee 2026 did). This is a second, very interpretable outcome: "the published biomarker is not even stable". |
| L2 | **Needs splitting** | ComBat *with labels as a covariate* (strongly leaky, Nygaard 2016) is very different from label-free pooled normalisation (usually a small effect; Rosenblatt 2024 found leaky site correction had minor effects). | Split into **L2a (label-using)** and **L2b (label-free pooled)**. Code and report them separately. |
| L3 | Mostly clear | "One visit per patient" changes the sample size, which changes the AUC for reasons other than leakage. | Prefer **patient-grouped CV** (all visits of a patient in the same fold), which keeps n. Use one-visit-per-patient as a sensitivity analysis. |
| L4 | **Not minimal** | "Validate on another independent cohort" replaces the test population, which mixes leakage with *transportability* (cohort shift). That isn't a minimal change. | Primary: drop the overlapping samples and evaluate on what's left, if n is adequate (pre-register a minimum, e.g. ≥ 10 per class). Otherwise record **"no valid external test"** as a result, not a missing value. Using another cohort should be a separate, clearly labelled analysis. |
| L5 | Fairly clear | Nested CV is the right fix. "Reporting the best of many models" may only be detectable when the paper reports several. | Fine. |
| L6 | Clear | Adding nested CV goes from "no estimate" to "an estimate". That's a big change, but it's the only possible correction. | Report L6 papers separately: their Δ_leak is really "training AUC minus honest AUC", which is a different quantity. |
| L7 | Clear | — | Fine; likely a small effect. |

**Interactions and order.** Plan Section 4.3 says "fix each leak alone, then all together". With 2+ leaks, "fixing L1 alone" and "fixing L1 after L2 is fixed" can give different answers. The leaks are not additive. **Suggestion:** report both "remove one from the fully leaky pipeline" and "add one back to the fully corrected pipeline". If a paper has ≤ 3 leaks, you can average over all orders (a *Shapley-value* decomposition, which splits a total effect fairly among interacting causes). With 3 leaks that is only 8 configurations.

**Papers coded "unclear".** The plan doesn't say what happens in the re-runs when a leak is *unclear*, e.g. the paper doesn't say whether genes were chosen before or after splitting. This will be common. **Suggestion:** pre-register a rule. My recommendation: run both readings as registered variants, classify the paper as "leaky-uncertain", and analyse it as its own stratum.

### 5.2 Does the meta-analysis on the logit-AUC scale make sense?

**The idea is reasonable but it behaves badly exactly where these papers sit.**

- logit(AUC) = log(AUC / (1 − AUC)). It turns the 0–1 range into −∞ to +∞, so standard meta-analysis maths works better.
- **Near 1, it explodes.** logit(0.998) = 6.2 and logit(0.95) = 2.9, a drop of 3.3 logit units. logit(0.80) = 1.4 and logit(0.70) = 0.85, a drop of 0.5 units. A raw drop of 0.05 near the ceiling looks 6–7× bigger on the logit scale than a raw drop of 0.10 in the middle. **A reported AUC of exactly 1.0 has an infinite logit**, and some papers will report 1.0.
- **Weights go wrong.** Random-effects meta-analysis weights papers by 1/variance. The variance of an AUC shrinks as AUC approaches 1, so papers near the ceiling get large weights.
- **The SE in the plan is the wrong kind.** The plan computes a "bootstrap CI over seeds and folds". Variation across random seeds measures how *unstable the CV split* is, not how *uncertain the AUC is as an estimate* of performance on new patients. The latter depends mainly on sample size. Seed-based CIs will be too narrow.
- **The two AUCs in Δ_leak are paired** (same samples). Their difference needs a paired standard error, not two separate ones combined.
- **Papers share datasets.** If 8 of 15 re-run papers use GSE61635 or GSE65391, their Δ_leaks are correlated, and a standard random-effects model treats them as independent.

**Suggestions:**
1. **Primary analysis on the raw AUC-difference scale**, which is what readers understand ("leakage added 0.12 AUC on average"). Use the logit scale as a sensitivity analysis, with AUC capped at, e.g., 0.995 before transforming.
2. Given ~10–15 papers, make the **primary pooled summary simple and robust**: the median Δ_leak with a bootstrap-over-papers CI, plus a sign test or Wilcoxon signed-rank test for H1. Keep the random-effects model as secondary.
3. For per-paper uncertainty, use a **bootstrap over patients** (resample patients, re-run both arms on the same resample, take the difference). This is expensive, so maybe 100–200 resamples on the cheaper pipelines. Alternatively, report seed variation honestly as "split instability", not as a CI.
4. Account for dataset sharing, either with a **multilevel model** (papers nested in datasets) or by reporting the analysis restricted to one paper per primary dataset as a sensitivity check.

### 5.3 Sample size and power for H1–H3

- **H1 (pooled Δ_leak > 0 among leaky papers): well powered**, almost trivially. If L1 is present, theory and prior work (Ambroise 2002; Asiaee 2026; Rosenblatt 2024) say Δ_leak will be positive. With 12 leaky papers all showing positive Δ_leak, a sign test gives p ≈ 0.0002. **Problem:** reviewers may say H1 is so expected that testing it adds little. The real scientific content is **how big** and **for which leak types**. Reframe O2 as *estimation* (how much, with what spread), and keep H1 as a formality.
- **H2 (control Δ_leak ≈ 0 and smaller than leaky): circular as written** (Section 5.4), and with 0–3 controls it has **no power** for an equivalence claim anyway. To claim "≈ 0" you need an *equivalence test* with a pre-set margin (e.g. |Δ| < 0.02), and 3 papers can't support that.
- **H3 (permuted-label AUC > 0.5 as published, ≈ 0.5 corrected): well powered per paper.** Each paper gets 100+ permutations, so this is a within-paper test. The formal statement "≈ 0.5" again needs an equivalence margin.
- **Exploratory meta-regression** (Δ_leak on number of candidate genes, sample size and leak type) with 10–30 papers and 3+ covariates: **badly underpowered**, and leak type is confounded with paper. Keep it, but label it as descriptive and avoid p-values, or replace it with a designed experiment (Section 6, Option B).

### 5.4 Are the controls a fair comparison? (H2 is circular)

As written:
- Control paper = no leak present.
- Corrected pipeline = as-published with *only the leaks* fixed.
- So for a control, **corrected = as-published, and Δ_leak = 0 by construction** (apart from seed noise). H2 can't fail.

Secondary problems:
- Controls will be very few, and they differ systematically from leaky papers: more methodologically careful groups (e.g. Kegerreis 2019 is from a dedicated lupus bioinformatics group), different tasks (often activity rather than SLE vs HC), larger samples. So "leaky vs control" compares different kinds of study, not just different leakage.

**What a control should actually do here.** Ask what the control is for: to show that **your re-run-and-correct machinery doesn't itself lower AUC** when nothing is wrong. Options:

1. **Run the full "correction template" on controls anyway.** Apply the standard audit template (nested CV, patient-grouped splits, per-cohort processing) to every paper. For a truly clean paper this should change nothing beyond noise. If it does change the AUC, either your coding missed a leak or your template has side effects. Either way H2 becomes testable, and it doubles as a check on the coding instrument.
2. **Placebo corrections on leaky papers.** Make a change that is *not* leak-related (e.g. a different but equally valid fold assignment, or swapping LASSO's λ selection rule between two equivalent choices) and show it changes AUC much less than the leak correction. This uses the leaky papers themselves, so no extra papers are needed.
3. **Permuted labels are already the strongest negative control** (H3), and they don't depend on finding control papers at all.

My recommendation: **reframe H2 as a "machinery check"** using options 1 and 2, report controls descriptively, and drop the "≥ 3 controls" requirement from the sampling rule. You may simply not find three.

### 5.5 How could the AI-analyst design fail?

See Section 5.8 for the full list. The single most important point is here because it threatens the main estimate:

**The prompt may bias Δ_leak upward.** The registered instruction says "reproduce the pipeline exactly as described, **including steps that may be methodologically flawed**." When the text is ambiguous (e.g. "we selected DEGs and then built an SVM with 5-fold CV": were DEGs selected on all data or within folds?), an agent primed to "keep the flaws" will tend to choose the leaky reading. That inflates the as-published AUC and hence Δ_leak. Bertran et al. 2026 showed that LLM analysts' results shift with prompt framing.

**Fix:** the default rules for ambiguity must be **neutral and pre-registered**. For example: "if the text doesn't state whether selection was inside CV, code L1 as *unclear* and run both readings". The prompt should not push toward either reading. Report how often the as-published configuration relied on an ambiguity resolved toward leakage.

### 5.6 Permuted labels can miss L3 and L4

The plan permutes "within cohort, keeping class balance". Consider:

- **L3 (repeated visits):** if visit 1 and visit 2 of the same patient get *different* shuffled labels, the model can no longer exploit "same person = same label". The permutation then hides exactly the leak you wanted to show. **Fix:** permute labels **at the patient level**, so all visits of a patient share the same shuffled label.
- **L4 (overlap across datasets):** if a sample appears in both training series and "external" series, permuting each series independently gives the duplicate different labels in each, which again hides the leak. **Fix:** use the overlap catalog to give **the same shuffled label to the same physical sample** in every dataset where it appears.
- **L2a (ComBat with labels):** fine. The shuffled labels go into ComBat as the covariate, so the leak is preserved, as it should be.

This is a subtle but important design detail. Without it, the permutation figure will understate L3 and L4.

### 5.7 Uncertainty about what is a "leak" at the boundaries

- The plan calls Kegerreis 2019's "z-scored within each dataset before CV" a *mild leak*. Under **leave-one-study-out** validation, standardising each study using only its own data, without labels, is often considered legitimate: at deployment you'd standardise a new cohort the same way. Within-study CV is more debatable. This is the label-free, unsupervised pre-processing case. Moscovich & Rosset showed that such leakage can bias CV, usually only slightly (arXiv 1901.08974; *journal version unverified*). The L2a/L2b split (Section 5.1) handles this.
- **Case-control batch confounding** (all SLE samples run in one batch, all controls in another) inflates AUC but **isn't leakage**, and no correction in the plan fixes it. It's worth coding as an extra item, because reviewers will ask why the corrected AUC is still 0.99.
- **Mapping onto Kapoor & Narayanan's 8 types.** From memory *(check against the paper)*, their types are: no train–test split; preprocessing on train+test; feature selection on train+test; duplicates; illegitimate features; temporal leakage; non-independence between train and test; sampling bias in the test distribution. Our L5 (tuning on the test set) has no clean match. Their "illegitimate features" (e.g. treatment-induced genes such as glucocorticoid-response genes that mark "being a treated patient") and "temporal leakage" (relevant to flare prediction from longitudinal data) have no L-code in our scheme. Decide whether to add them or explain why they're out of scope.

### 5.8 AI-analyst design: other ways it could fail

1. **Training-data contamination.** Most target papers (2019–2025) are probably in the agents' training data. The packet removes the *numbers*, but the paper's text is still there, so a model might recognise the paper and recall the reported AUC or the authors' code. "Don't rely on recollection" can't be enforced. **Mitigations:** (a) after each reconstruction, ask the agent in a *separate* session to state the paper's reported AUC and genes, and record its recall rate; (b) include some papers published after the agents' training cutoffs, and compare.
2. **Silent corrections.** LLMs are trained on "best practice" and will tend to add nested CV, patient-level splits and so on. The audit is designed to catch this. The plan handles it well.
3. **Over-literal "flaw insertion".** The opposite failure, from priming (Section 5.5).
4. **The two AIs are not independent.** They share much training data, the same prompt and the same packet. Agreement between them doesn't show correctness. The plan already says this, which is good.
5. **The auditor isn't blind.** The auditor/adjudicator is the student, who has read the full papers including results for coding, built the pipeline, and is the primary leakage rater. So audit and adjudication decisions are made by someone who knows the reported AUCs. That weakens the "blinding" argument, which is the main stated reason for using AI. **Mitigation:** acknowledge it, and keep the audit strictly to "does the configuration match the packet text", with every change logged and justified by a packet quote.
6. **The blinding argument cuts both ways.** Plan Section 4.8 says humans "can't easily be blinded". But the plan's own benchmark analyst *is* a blinded human working from the same redacted packet. So blinding doesn't require AI; it requires a person who hasn't read the paper. The AI's real advantage is **labour**, and Brodeur 2025 suggests AI-led reproduction loses a lot of quality compared with AI-assisted human reproduction.
7. **Product drift.** "Claude Code" and "OpenAI Codex" are products whose underlying models and tools change frequently, sometimes silently. "Versions fixed at Stage 1" may be impossible for the products. **Mitigation:** use **pinned API model snapshots** inside **one shared, open-source agent harness** (the same tools and scaffold for both). This is more reproducible, and differences between AI-A and AI-B then reflect the models, not the products' different scaffolding.
8. **The audit may cost as much as doing it yourself.** If agents produce configurations that need substantial fixing (and the benchmarks above suggest they often will), auditing two agents' work may take longer than a human reconstructing once with AI help.
9. **Reviewer mismatch.** A bioinformatics reviewer may see O7 as a distraction. An AI-evaluation reviewer will see n = 5 as too thin. You risk satisfying neither.

### 5.9 Non-independence of papers

Already covered in Section 5.2, but worth stating on its own: in this literature, a handful of GEO datasets (GSE61635, GSE50772, GSE65391, GSE81622, GSE72326, GSE121239, …) are reused over and over. Papers using the same training dataset share the same "noise", so their Δ_leaks are correlated. This affects every pooled estimate and CI. **Report the dataset-to-paper map** (the overlap catalog makes this easy) and either model it or run a one-paper-per-dataset sensitivity analysis.

### 5.10 Ceiling effects and task heterogeneity

- SLE vs HC, active vs inactive, LN vs non-LN, flare, and treatment response are very different problems with very different "true" AUCs. Pooling Δ_leak across them mixes things. **Stratify by task**, at least descriptively.
- If true AUC for SLE vs HC is about 0.9 and reported is 0.99, the maximum possible Δ_leak is about 0.1. For activity or flare, where the true AUC may be about 0.65, leakage can add much more. **Expect the biggest inflation in the hardest tasks.** That is worth stating as an exploratory hypothesis, and it may affect which papers to sample: consider stratifying the re-run sample by task, not only by leaky/control.

### 5.11 Smaller points

- **Retracted papers:** pre-register whether they're included. I'd include them in prevalence, flagged, and exclude them from re-runs.
- **Eligibility vs the excluded "non-public data" studies:** fine as written. They're coded for prevalence but not re-run.
- **κ per item with a "present/absent/unclear" scale:** fine, but report **prevalence-adjusted** agreement or raw percent agreement too, because κ is unstable when one category dominates (e.g. L1 "present" in 80% of papers).
- **"Reproducible within ±0.05"**: reasonable, but justify the threshold, and consider also reporting a relative measure, since 0.05 near 1.0 is a large change in error rate.
- **"Short paper"**: as noted in Section 3.2, this isn't a short paper in its current form. Check *Briefings*' article types and limits *(unverified; the plan already lists this as a to-do)*.
- **OUP AI policy:** a search found OUP guidance requiring a detailed AI-use statement at submission (tool, version, where and how used, how outputs were validated), and that ISCB's LLM policy applies to OUP's *Bioinformatics* and *Bioinformatics Advances* (*from secondary summaries; check OUP's and Briefings' own author guidelines*). This is compatible with the plan's disclosure approach. Using AI *as the analyst* is unusual enough that it would be worth asking the editor before submission.

---

## 6. Simplification options

Here are three smaller versions, from "keep most of it" to "smallest solid paper". In all of them, **keep**: pre-registration, the three-number decomposition (where re-runs happen), the overlap catalog, and permuted labels.

### Option A (recommended): the core paper, with AI as assistant

- **Keep:** systematic search and leakage coding (O1); overlap catalog (O6); **10–15 re-runs** (O2, O5), as published vs fully corrected; permuted labels on 5–10 of them (O4); Jaccard overlap of selected genes.
- **Change:** the reconstruction is done by **Pascal, with an AI coding assistant**, from a **redacted packet** prepared by Tyler. Blinding is kept, because Pascal works from the packet before reading the results. All prompts and transcripts are saved and released. Using AI as an assistant is then a disclosed tool, not an object of study.
- **Cut or defer:** O7 (formal AI-A vs AI-B vs human comparison), so there's no second vendor, no adjudication of two agents, and no second trainee needed; one-at-a-time attribution for every leak (keep it only for papers with exactly 2–3 leaks, or only for L1 and L3/L4, which are expected to matter most); the exploratory meta-regression (describe instead).
- **Why:** it keeps everything that is new (SLE prevalence, measured inflation, L3/L4 in real data, the catalog) and cuts the riskiest, most labour-heavy layer. It fits about 5–7 months.
- **The AI work isn't lost:** O7 can become a separate follow-up paper using the same packets and adjudicated configurations as ground truth. It is a nice second paper.

### Option B: a designed experiment instead of exact reconstructions

Most of these papers follow nearly the same template: DE → WGCNA → LASSO/SVM-RFE/RF intersection → ROC, often with ComBat-merged GEO sets. Instead of reconstructing each paper exactly:

- Build **one canonical template pipeline** with switches for each leak (L1 on/off, L2a on/off, L3 on/off, L4 on/off).
- Run a **full factorial** (every combination of switches) on **every major SLE GEO dataset or dataset pairing used in the literature**.
- This gives clean per-leak attribution, including interactions, without reconstruction ambiguity, much as Rosenblatt 2024 did for neuroimaging.
- Add **3–5 exact reconstructions** of real papers to show the template behaves like real pipelines, plus the prevalence coding to show the template is representative.
- **Pros:** much cleaner statistics (designed, not observational); no AI layer needed; very feasible.
- **Cons:** weaker answer to "how much were *these published numbers* inflated"; you measure the *template*, not each paper. O5 (reproducibility) mostly disappears.

### Option C: the smallest solid paper

- **Prevalence coding** (O1) + **overlap catalog** (O6) + **external re-validation** of published gene panels: take each eligible paper's final gene panel, refit its classifier on its own training data only, and test it on a **truly independent, non-overlapping SLE cohort** identified by the catalog. Compare with the paper's reported external AUC.
- Plus a **permutation demonstration** on 3–5 typical pipelines.
- **Pros:** very feasible (perhaps 3–4 months); the catalog plus "how many published panels hold up in a genuinely independent cohort" is a clear, useful result; easy to explain.
- **Cons:** doesn't separate leakage from overfitting or cohort shift; a weaker fit for the "measured inflation by leak type" framing; more like Castaldi 2011.

### What I'd cut first if time runs short, in order

1. The second AI vendor and AI–AI adjudication.
2. The human benchmark by a second trainee (only needed if O7 stays).
3. One-at-a-time attribution beyond L1 and L3/L4.
4. 200 → 100 permutations, 50 → 10–20 seeds.
5. Kidney-tissue studies in the prevalence arm (D7).
6. The full-scale double human coding (code a random 25% subset twice, for κ).

---

## 7. Open decisions (D1–D11): recommendations

| # | Decision | Plan's recommendation | My recommendation | Reasoning |
|---|---|---|---|---|
| **D1** | Scope | SLE only; all transcriptomic ML methods; WGCNA as subgroup | **Agree.** | Expanding to all autoimmune diseases would multiply the workload with little gain. SLE has the dataset-overlap story that makes L4 interesting. WGCNA-only would shrink the pool and make the paper look narrower. **Also stratify by task** (SLE vs HC; activity; LN; flare/response), because true AUCs differ a lot (Section 5.10). |
| **D2** | Date range | 2015–present | **Agree** (2015–present). | Covers the GEO + ML boom. Earlier papers are few and use different methods. If the eligible set is larger than ~200, a fallback is 2018–present, but the trend over time is itself interesting. |
| **D3** | Number of re-runs and sampling | All up to ~30; else stratified random with ≥ 3 controls | **Target 12–15, minimum 8, stratified by task. Drop the "≥ 3 controls" rule; include all controls found.** | Audit time is about 1.5–2.5 days per paper, not 1 (Section 4.2). Controls may number 0–3, so a rule requiring 3 may be impossible. H2 needs redesign anyway (Section 5.4). Stratifying by task protects against an all-"SLE vs HC" sample, where the ceiling limits Δ_leak. |
| **D5** | Name papers? | Named in supplement table; aggregate in main text | **Name them openly (supplement table and figure labels), neutral tone, with full code per paper.** | Releasing per-paper configurations and code names the papers in practice. Pretending otherwise looks evasive. Being transparent is the more defensible position, as Kapoor & Narayanan and Bernett et al. did. Describe practices, never motives. Check that every per-paper statement is backed by a quote from the paper. Flag retracted papers. Run the wording past Tyler, and possibly a journal editor. |
| **D7** | Kidney-tissue studies | Blood + tissue for prevalence; re-runs blood only | **Agree**, but be ready to drop tissue from prevalence if screening load is high. | Tissue (kidney biopsy) studies are few and small, and LN tasks are clinically important. Re-runs focus on blood, where the overlapping-GEO story lives. |
| **D8** | Primary metric | AUC primary; accuracy if it's the only metric | **AUC primary. Accuracy-only papers: include in prevalence, but exclude from pooled Δ_leak** (report them separately). | AUC and accuracy aren't on the same scale and can't be pooled. Accuracy also depends on the cutoff and class balance. |
| **D9** | Human roles | PI = packet preparer; student = auditor/adjudicator; second trainee = benchmark analyst | **Under Option A: Tyler = packet preparer (if he has ~2–3 h per paper); Pascal = reconstructor (AI-assisted) and primary coder; a second person codes a random 25% subset for κ.** If O7 is kept, the plan's roles are fine, **but only if the second trainee actually exists and is committed.** | The plan's role design needs three people who stay independent. If there are only two, the design can't be carried out as written. Packet preparation by the PI is a real time cost (60–90 h for 30 papers) that should be agreed explicitly. |
| **D10** | AI role in leakage coding | Human primary + AI second rater | **Human primary + AI second rater on all papers, *plus* a second human on a random 20–30% subset.** | Reviewers expect human–human reliability for risk-of-bias coding (as with PROBAST). Human–AI κ alone may not satisfy them. A human subset gives the standard κ, and the AI covers the rest cheaply. Report human–human and human–AI κ side by side. That's also a small, interesting result in itself. |
| **D11** | AI tools | Two vendors, versions fixed at Stage 1 | **If O7 stays: two vendors' *pinned API model snapshots* in one shared open-source agent harness. If Option A: one assistant, any good one, with model ID and dates recorded.** | Products such as Claude Code and Codex update continuously and can't really be "frozen". A shared harness also means AI-A vs AI-B differences reflect the models, not the tools around them (Section 5.8, point 7). |

Decided items (D4, D6, D12): no comments beyond those above. One note on **D6** (venue): *Briefings in Bioinformatics* is a good fit, especially given Castaldi 2011 and Bernett 2024 published there. The fallback (*Lupus Science & Medicine*) suits Option A or C better than the AI-heavy version.

---

## 8. Questions to ask Tyler

**About the decision between the two papers:**
1. When you said this is "the strongest but most difficult", which part did you mean as most difficult: the reconstructions, the corrections, the AI layer, or the time? Would a reduced version (Option A or B) still be "the strongest" in your view?
2. What is the real deadline, and is it driven by something (thesis chapter, funding, conference)? Is 5–6 months a hard limit?
3. How much of my time is this, given the sister LIONESS project? Full time?

**About roles and resources:**
4. Do you have about 2–3 hours per paper to prepare redacted packets (60–90 hours for 30 papers)? If not, who can?
5. Is there really a second trainee for the human benchmark and/or second coding? Who, and how many hours?
6. What compute do we have (HPC cluster, cloud credits)? The permutation analyses need roughly 1,000 CPU-hours even in the reduced form.
7. Do we have budget for two AI vendors' API use?

**About the science:**
8. Do you agree that the "corrected" pipeline evaluates the *procedure* rather than the *published gene panel*? How would you phrase that for authors who object?
9. How should we handle the circular H2? Are you happy to reframe controls as a "machinery check" (Section 5.4)?
10. For pooling: raw AUC difference with a robust summary, or a random-effects model on the logit scale? How should we handle papers sharing datasets?
11. Should we split L2 into label-using (ComBat with labels) and label-free?
12. Should we stratify re-runs by task (SLE vs HC vs activity/LN/flare) rather than only leaky vs control?
13. Have you seen Asiaee et al. 2026 (Coombes group, drug response) and An et al. 2026 (protein panels)? Do they change how novel you think this is?

**About the AI part:**
14. Is the AI-analyst design central to why you like this paper, or is it a means to an end? Would you be comfortable moving O7 to a follow-up paper?
15. Given Brodeur et al. 2025 (AI-led reproduction much worse than human; AI-assisted about equal), should the AI be the analyst or the assistant?

**About publication and ethics:**
16. Are you comfortable naming papers explicitly? Should we sound out the *Briefings* editor (or a colleague who has published critiques) first?
17. Should we contact the editor about using AI as an analyst before we invest in that design?

---

## Appendix: the 3–5 changes I'd prioritise

1. **Decide on scope first, ideally Option A** (Section 6): human-led, AI-assisted reconstruction of 12–15 papers, with O7 deferred. Everything else depends on this.
2. **Fix the control logic (H2)** and add a placebo correction (Section 5.4).
3. **Rewrite the "corrected pipeline" rules** (Section 5.1): state the estimand (procedure, not panel); split L2 into L2a/L2b; make the L4 correction minimal; add a rule for "unclear" leaks; add Jaccard gene overlap as an outcome; handle interactions.
4. **Revise the statistics** (Sections 5.2–5.3, 5.6, 5.9): raw-AUC primary scale with a robust summary; patient-bootstrap or honest "split-instability" wording; account for shared datasets; patient-level and overlap-consistent permutation; stratify by task.
5. **Update the novelty section** with Asiaee 2026, An 2026, Bernett 2024, Rosenblatt 2024, Castaldi 2011, Dupuy & Simon 2007, Nygaard 2016, Wang 2026 (*JMIR*) and the AI-reproduction work (CORE-Bench, PaperBench, BixBench3, Brodeur 2025, Bertran 2026). Reposition from "first to measure" to "first in patient transcriptomics, with leak types (L3/L4) the others lack". **Check all new PMIDs on NCBI before adding them.**

---

## Sources consulted (via web search; see the verification note at the top)

- CORE-Bench: <https://arxiv.org/abs/2409.11363v1>; <https://mlanthology.org/tmlr/2024/siegel2024tmlr-corebench>
- PaperBench: <https://proceedings.mlr.press/v267/starace25a.html>; <https://openai.com/index/paperbench>
- BixBench3: <https://arxiv.org/pdf/2608.25286>; <https://advances.edisonscientific.com/benchmarks/bixbench3/>
- BixBench: <https://arxiv.org/pdf/2503.00096>
- Asiaee et al. 2026: <https://www.biorxiv.org/content/10.64898/2026.02.05.704016v2>
- An et al. 2026: <https://www.medrxiv.org/content/10.64898/2026.09.02.26362037v2>
- Rosenblatt et al. 2024: <https://www.nature.com/articles/s41467-024-46150-w>
- Bernett et al. 2024: <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10939362/>
- Castaldi et al. 2011: <https://olympias2.lib.uoi.gr/items/387c428b-53da-48d9-897c-b683b8816a13>
- Dupuy & Simon 2007: <https://www.sciencedaily.com/releases/2007/01/070116205601.htm>; <https://academic.oup.com/jnci/issue/99/2>
- Nygaard et al. 2016: <https://pmc.ncbi.nlm.nih.gov/articles/PMC4679072>
- Moscovich & Rosset: <https://arxiv.org/pdf/1901.08974>
- bioLeak: <https://cloud.r-project.org/web/packages/bioLeak/index.html>; <https://arxiv.org/pdf/2604.10965>
- Brodeur et al. 2025: <https://www.iza.org/publications/dp/17645/comparing-human-only-ai-assisted-and-ai-led-teams-on-assessing-research-reproducibility-in-quantitative-social-science>
- Bertran et al. 2026: <https://arxiv.org/abs/2602.18710>
- Wang et al. 2026 (*JMIR*): <https://www.jmir.org/2026/1/e90209>
- Retracted SLE ML review (2023): <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10567382/>
- Other retracted SLE papers: <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10719036/>; <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12540918/>
- OUP AI guidance (secondary summaries): <https://www.enago.com/responsible-ai-movement/publisher-ai-guidelines/OUP-ai-guidelines>; <https://www.iscb.org/iscb-policy-statements/iscb-policy-for-acceptable-use-of-large-language-models>
