# Project Changelog

This changelog summarizes the development history of the Hospital Analytics Capstone in a cleaner, employer-readable format.

## Current Version

### Portfolio and Live Demo Polish

- Added an employer-friendly live demo page at `https://capstone-iitm.onrender.com/`.
- Kept the technical FastAPI docs available at `https://capstone-iitm.onrender.com/docs`.
- Updated the README to explain the project in plain language.
- Added sections for common healthcare analytics problems, AI usage, and responsible AI guardrails.
- Prepared the app for Render deployment with pinned dependencies and `render.yaml`.

Related commits:

- `06310fd` - Make README more employer friendly
- `b9f371e` - Add employer-friendly live demo page
- `b7150d4` - Add API landing route for live demo
- `5b93556` - Prepare FastAPI app for Render deployment
- `6b7ec5f` - Clarify project overview for portfolio readers

## Phase 7: Executive Business Report

- Added the final project notebook and report outputs.
- Expanded submission materials with notebook and report formats.
- Included final documentation for business-facing project review.

Related commits:

- `d9a8925` - Expand final submission notebooks and report formats
- `8d24408` - Add Phase 7 final report notebook
- `6053b16` - Update final report and Phase 6 deliverables notebook

## Phase 6: Monitoring and Governance

- Added monitoring scripts and governance outputs.
- Created drift detection, data validation, audit log, and compliance reports.
- Documented how the project checks for future data reliability issues.

Related commit:

- `ec6bffd` - Add Phase 6 monitoring and governance

## Phase 4 and Phase 5: Evaluation and API Deployment

- Added model evaluation and explainability outputs.
- Added safety checks, segment metrics, feature importance, and model-card documentation.
- Built the FastAPI app for prediction and scoring endpoints.
- Added deployment and API documentation.

Related commit:

- `8a3068d` - Add Phase 4 evaluation and Phase 5 API deployment

## Phase 3: Machine Learning Models

- Added classification models for visit risk and claim outcomes.
- Trained baseline and advanced models using leakage-safe feature sets.
- Saved deployable model artifacts and metrics.
- Added final report materials.

Related commit:

- `1be36e4` - Add Phase 3 modeling and final report

## Phase 2: EDA and Feature Engineering

- Added exploratory data analysis and data quality profiling.
- Built the 25,000-row model table.
- Added engineered features for patient visits, billing behavior, provider rejection rate, dates, missingness, and outliers.
- Added schema and drift summary outputs.

Related commit:

- `82d49b0` - Add Phase 2 EDA package

## Phase 1: SQL Analytics Foundation

- Built the SQLite analytics layer from patient, visit, and billing CSV files.
- Added raw staging tables and relational final tables.
- Added primary keys, foreign keys, constraints, indexes, reusable views, and analysis queries.
- Documented index strategy and Phase 1 analysis results.

Related commits:

- `7a09c22` - Complete Phase 1 SQL analytics layer
- `60cefcf` - Organize notebooks by project phase
- `c657173` - Clear Phase 1 notebook kernel error output

## Submission and Repository Hygiene

- Added the final notebook submission archive.
- Ignored extracted duplicate submission folders to keep the repository clean.

Related commits:

- `4671a8e` - Add final notebook submission archive
- `d51abe4` - Ignore extracted submission notebook folder
