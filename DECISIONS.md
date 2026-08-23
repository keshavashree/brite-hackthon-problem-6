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