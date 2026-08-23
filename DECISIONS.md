# Decisions

## 2026-08-23 — Initial Architecture

### Decision

Use a modular Python pipeline rather than building the solution
as a single notebook.

### Why

The problem requires a ranked investigation worklist, explanations,
fairness analysis and the ability to incorporate investigator
feedback when the requirements change.

A modular structure allows these components to be changed independently.

### Initial Approach

Start with an explainable signal-based ranking approach.

The supplied data does not contain confirmed improper-payment labels,
so the initial solution will not pretend to be a supervised fraud
classifier.

### Rejected for Initial Version

A black-box machine-learning model as the first implementation.

### Why

The first priority is to understand the supplied data and establish
transparent, explainable signals before introducing a more complex
model.

### Current Limitations

The initial version does not establish whether a payment is actually
improper. It only identifies cases that may be worth human review.

### Next Decision

Perform feature and signal discovery before finalising the ranking
algorithm.

## 2026-08-23 — Award Deviation Thresholds

### Decision

Use threshold-based award deviation signals rather than treating
every percentage above the recorded award as equally meaningful.

### Why

Exploration showed that C-33248 has a maximum payment-to-award ratio
of approximately 1.05. The investigator feedback indicates that this
case should not be treated as a strong investigation candidate.

A small deviation should therefore not automatically create a strong
risk signal.

### Initial thresholds

- Below 1.10x: no award-deviation signal
- 1.10x–1.25x: moderate signal
- 1.25x–1.50x: strong signal
- 1.50x–2.00x: very strong signal
- 2.00x or above: extreme signal

These thresholds are intended for investigation prioritisation,
not to establish improper payment.