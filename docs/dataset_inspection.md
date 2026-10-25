# ResolveAI — Dataset Inspection Notes

## 1. Purpose and status

This note records the initial inspection of the support-ticket dataset used for ResolveAI.

**Current phase:** Dataset inspection and validation  
**Status:** Inspection only. No source data has been modified, no model has been trained, and no performance claims have been made.

## 2. Dataset source and license

- **Dataset:** Support Tickets with an AI-Automation Counterfactual
- **Source:** https://huggingface.co/datasets/s2pidape/support-ticket-dataset
- **Configuration used:** `humans_only`
- **Split:** `train`
- **Rows:** 1,500,000
- **Columns:** 38
- **File:** `data/train-00000-of-00001.parquet`
- **License shown on the dataset card:** CC BY 4.0
- **Attribution:** Talgat Kozahmetov, “Support Tickets with an AI-Automation Counterfactual” (2026), https://huggingface.co/datasets/s2pidape/support-ticket-dataset

The dataset author explicitly states that the data is synthetic. It is a sandbox for methods, not evidence about real support desks. Preserve this limitation in the project README and any demo or evaluation report.

## 3. Intended use in ResolveAI

The dataset can support practice with data inspection, support-ticket workflow logic, validation, and selected ML experiments. Its suitability as a realistic NLP benchmark is limited by template-generated descriptions and repeated text.

Do not present results from this synthetic dataset as proof of real-world support performance.

## 4. Verified dataset structure and target

The dataset has 11 `category` labels. All 1,500,000 rows have a category.

Category counts range from:
- `Account Management`: 144,841 (9.66%)
- `Refunds`: 122,390 (8.16%)

The most-common-category baseline is approximately 9.66%. This is a reference baseline only, not a trained model result.

`issue_type_id` has 100 unique values. Inspection found that every `issue_type_id` maps to exactly one category, and no `issue_type_id` maps to multiple categories. Therefore, `issue_type_id` should be excluded from a first category-prediction model because it directly reveals the target.

## 5. Description repetition and label consistency

Observed results:
- Unique `issue_description` values: 277,373
- Descriptions appearing once: 120,786
- Descriptions appearing more than once: 156,587
- Ticket rows whose descriptions appear more than once: 91.95%
- Descriptions mapped to multiple categories: 0
- Descriptions mapped to multiple issue types: 0
- Issue types mapping to multiple descriptions: 100

The dataset card says descriptions are template-generated and one-to-one with `issue_type_id`. Repeated descriptions always having consistent labels creates a risk that a random row-level train/test split will place identical descriptions in both sets and overstate generalization to new text.

**Evaluation decision:** If a category classifier is evaluated later, compare a stratified row-level split with an evaluation that groups identical descriptions so that a description cannot appear in both train and test. Clearly describe the synthetic/template limitation. Do not claim realistic NLP generalization from a high score alone.

## 6. Description quality checks

- `issue_description` has no missing or empty values.
- No leading/trailing whitespace, repeated spaces, tabs, or newlines were found in the checks performed.
- Description lengths: mean approximately 99 characters; minimum 27; maximum 182.
- Some unusual capitalization/joined-word examples were observed, but no broad text-cleaning change has been justified.

Do not apply broad text normalization or alter source descriptions without a specific reason and a documented check.

## 7. Missing values and categorical fields

Some fields are complete, while several lifecycle/outcome fields have missing values that appear strongly related to ticket status.

Examples:
- `escalated`: 152,745 missing (10.18%)
- `resolution_time_hours`: 152,745 missing (10.18%)
- `customer_satisfaction_score`: 153,944 missing (10.26%)
- `escalation_reason`: 1,089,215 missing (72.61%)
- `resolution_notes`: 96,402 missing (6.43%)

Customer satisfaction scores are within the expected 1–5 range. There are 1,346,056 non-missing scores and no scores outside 1–5. Missing scores should remain missing unless a task-specific, justified method is chosen; do not replace them with zero.

Missing lifecycle fields should not automatically be interpreted as negative outcomes. Investigate the field's meaning and collection process before imputing or recoding.

## 8. Timestamp and SLA caveats

The following inconsistencies were observed:
- `first_resolved_at` precedes `created_at` in 4,349 rows.
- `resolved_at` precedes `created_at` in 1,802 rows; all 1,802 differences are exactly -5 hours.
- `closed_at` precedes `created_at` in 4,496 rows.
- `first_resolved_at` occurs after `resolved_at` in 6,445 rows with both timestamps present.
- The `first_resolved_at > resolved_at` issue is concentrated in tickets created in 2023: 5,221 cases in 2023, 457 in 2022, and 767 in 2024.
- These out-of-order `first_resolved_at`/`resolved_at` pairs occur in `Closed` and `Resolved` statuses: 6,404 in `Closed` and 41 in `Resolved`.

These findings establish inconsistencies, not their cause. A consistent five-hour difference may indicate a time-zone or generation convention, but that explanation has not been verified. Do not automatically shift or overwrite timestamps.

The dataset card also states that the `humans_only` configuration copies timing and outcome fields from the AI-world configuration rather than re-simulating human outcomes. Do not interpret these timings as an independent estimate of how long tickets would take in a human-only world.

### SLA margin

The observed `sla_breach_margin` sign is counterintuitive if interpreted as “time exceeded beyond SLA”:
- For `sla_breached = No`, most non-missing margins are positive.
- For `sla_breached = Yes`, most non-missing margins are negative.

The field's definition has not been verified. Do not label these rows erroneous or transform the sign until its semantics are established.

## 9. Leakage precautions for future modeling

For an initial category classifier, use `issue_description` as the input and `category` as the target. Exclude `issue_type_id` because it maps directly to the target.

Avoid using post-creation or post-resolution fields as intake-time model inputs without a justified, explicitly defined prediction moment. Potentially post-outcome fields include `assigned_team`, `assigned_to`, `resolved_by`, `status`, `escalated`, `escalation_reason`, `resolution_notes`, resolution timings, SLA outcomes, and satisfaction scores.

The dataset card provides a separate leakage warning for predicting `auto_resolved` in the `with_ai` configuration. If that task is ever attempted, follow the card's specified exclusions and drop rows with unknown `auto_resolved` outcomes rather than treating unknown outcomes as negatives.

## 10. Decisions and open questions

### Decisions recorded
- Keep the downloaded source dataset unchanged.
- Treat the dataset as synthetic and disclose this in project documentation.
- Do not use `issue_type_id` as a feature for category prediction.
- Do not make real-world NLP or operational-performance claims from this dataset.
- If evaluating text classification, include a split that prevents identical descriptions from crossing train/test boundaries.
- Do not repair timestamp or SLA fields without understanding their definitions.

### Open questions
- What exactly does `sla_breach_margin` represent?
- What caused the timestamp inconsistencies?
- Which dataset fields are genuinely available at ticket intake for each future prediction task?
- Is additional data needed to demonstrate realistic NLP generalization? This should be decided before presenting a classifier as a meaningful NLP benchmark.

## 11. Next project step

Finish the initial dataset-inspection phase and review the project scope before beginning preprocessing or model development. Choose each next task based on the project objective and these documented limitations.

### Additional timestamp validation

- All 1,500,000 `created_at` values matched the expected timestamp format and parsed successfully.
- `first_resolved_at` was earlier than `created_at` for 4,349 tickets.
- `resolved_at` was earlier than `created_at` for 1,802 tickets.
- All 1,802 cases with `resolved_at` earlier than `created_at` had exactly a 5-hour difference.
- The cause of the consistent 5-hour offset has not been established. No timestamps were modified.
- Missing resolution and closure timestamps showed consistent relationships with ticket status. Missing values have been preserved.

These findings are data-quality observations, not proof of the cause of the timestamp discrepancies.

### Resolution duration validation

- `resolution_time_hours` has 152,745 missing values.
- 1,797 rows have negative resolution durations.
- The minimum recorded duration is −192 hours.
- The inspected negative-duration examples show inconsistencies between recorded durations and their creation/resolution timestamps.
- The cause of these inconsistencies has not been established. No values were changed, imputed, or removed.

Negative durations should be investigated before using this field in duration analysis or as a model feature.

### Negative duration overlap check

- 1,797 rows have negative `resolution_time_hours`.
- None of these rows have `first_resolved_at` earlier than `created_at`.
- None of these rows have `resolved_at` earlier than `created_at`.
- The negative duration values are inconsistent with the observed timestamp ordering.
- The cause remains unknown; no records or values have been changed.

**Decision:** Preserve these records for now. Investigate the duration field's calculation or data-generation logic before deciding whether to exclude it from analysis or modeling.

### Negative resolution durations by status

| Status | Negative-duration rows | Total rows | Percentage |
|---|---:|---:|---:|
| Closed | 1,793 | 1,340,913 | 0.13% |
| Resolved | 4 | 6,342 | 0.06% |
| Cancelled | 0 | 56,343 | 0.00% |
| Open | 0 | 68,935 | 0.00% |
| Pending | 0 | 16,002 | 0.00% |
| On-Hold | 0 | 10,711 | 0.00% |
| New | 0 | 754 | 0.00% |

- All 1,797 negative-duration rows belong to `Closed` or `Resolved` tickets.
- The pattern is an association, not evidence that ticket status caused the negative values.
- No data has been modified or removed.

**Decision:** Keep the records unchanged while investigating the duration field's calculation or generation logic.

### Recorded versus timestamp-calculated resolution duration

- Compared all 1,797 rows with negative `resolution_time_hours` against elapsed time calculated from `created_at` and `resolved_at`.
- All 1,797 rows have non-negative timestamp-calculated durations.
- Example: ticket 1891 has a recorded duration of −80 hours, while the timestamps indicate 336 hours.
- This confirms a disagreement between the recorded duration field and the two timestamps for these records.
- The underlying cause has not been established.

**Decision:** Preserve the original data. Do not overwrite recorded durations with calculated values until the field definitions and intended calculation are understood.

### Ticket ID validation

- Total rows: 1,500,000.
- Unique ticket IDs: 1,500,000.
- Duplicate ticket ID rows: 0.
- Missing ticket IDs: 0.

**Conclusion:** `ticket_id` is unique and complete in this dataset. Keep it for record identification and joins, but exclude it as a predictive feature unless a specific, justified use is established.

### Ticket ID sequence validation

- Minimum ticket ID: 1.
- Maximum ticket ID: 1,500,000.
- Unique ticket IDs: 1,500,000.
- Missing IDs within the observed range: 0.

**Conclusion:** Every integer ID from 1 through 1,500,000 is present exactly once. The sequence is complete, but ticket IDs should be treated as identifiers rather than predictive features or chronological indicators.

### Ticket ID and chronological order

- Adjacent ticket-ID pairs checked: 1,499,999.
- Pairs where a higher ticket ID has an earlier creation timestamp: 750,064.
- Ticket IDs do not follow chronological creation order.
- Example: ticket ID 3 was created on 2023-06-15, while ticket ID 4 was created on 2022-12-15.

**Conclusion:** Use `ticket_id` as a record identifier only. Do not use it to infer chronological order or as a predictive feature. Use `created_at` when time-based ordering is needed.

### Ticket creation date coverage

- Earliest `created_at`: 2022-01-01 00:04:00.
- Latest `created_at`: 2024-12-30 23:58:00.

| Year | Ticket count | Percentage |
|---|---:|---:|
| 2022 | 371,773 | 24.78% |
| 2023 | 506,603 | 33.77% |
| 2024 | 621,624 | 41.44% |
| **Total** | **1,500,000** | **100.00%** |

- Ticket counts increase across these three calendar years.
- The dataset is synthetic, so this pattern should not be interpreted as evidence of real-world support-ticket growth.

**Conclusion:** The dataset covers nearly three calendar years. Preserve `created_at` for chronological analysis and consider time-based evaluation when assessing models.

### Creation timestamp completeness

- Total tickets: 1,500,000.
- Missing `created_at` values: 0.
- Unique non-missing creation timestamps: 730,445.
- Every ticket has a creation timestamp.
- Multiple tickets share the same timestamp; this is not automatically a data-quality issue.

**Conclusion:** `created_at` is complete and can be used for chronological ordering. When timestamps are tied, use an additional ordering rule if a deterministic sequence is required.

### Creation year range validation

- Expected creation years: 2022–2024.
- Tickets outside this range: 0.
- All 1,500,000 tickets have creation timestamps within the expected years.

**Conclusion:** No creation timestamps fall outside the expected 2022–2024 range. This check validates the year range only; it does not establish the accuracy of every timestamp.

### Shared ticket creation timestamps

- Total tickets: 1,500,000.
- Unique creation timestamps: 730,445.
- Distinct timestamps occurring more than once: 383,652.
- Tickets whose creation timestamp is shared by at least one other ticket: 1,153,207 (approximately 76.9%).
- The most frequently shared timestamp occurs 17 times.

**Conclusion:** Multiple tickets share creation timestamps. This is not automatically an error, but timestamp ties should be considered when ordering records for chronological analysis or time-based model evaluation.

### Monthly ticket creation distribution

- Number of months covered: 36.
- Date range: January 2022 through December 2024.
- Every month in this range contains tickets.
- Minimum monthly count: 28,122 (January 2022).
- Maximum monthly count: 56,966 (May 2024).
- Monthly counts vary across the period, with generally higher counts in 2024 than in 2022.

**Conclusion:** There are no missing calendar months in the observed creation-date range. Because the dataset is synthetic, the monthly variation should not be interpreted as evidence of real-world support demand. Use chronological evaluation when appropriate, while handling timestamp ties carefully.

### Issue description length analysis

- Total descriptions analyzed: 1,500,000.
- Missing descriptions: 0.
- Empty or whitespace-only descriptions: 0.
- Mean length: approximately 99.15 characters.
- Median length: 99 characters.
- 25th percentile: 86 characters.
- 75th percentile: 113 characters.
- Minimum length: 27 characters.
- Maximum length: 182 characters.
- Descriptions with 20 characters or fewer: 0.
- Descriptions longer than 500 characters: 0.

**Conclusion:** All tickets have non-empty descriptions, and description lengths fall within a relatively narrow range. No length-based filtering or truncation is justified by these checks alone. The dataset is documented as synthetic, with template-generated descriptions, so these findings should not be generalized to real-world support tickets.

### Duplicate issue description analysis

- Total tickets analyzed: 1,500,000.
- Unique descriptions: 277,373.
- Rows beyond the first occurrence of each unique description: 1,222,627.
- Rows beyond first occurrence as a percentage of all tickets: 81.51%.
- Most frequent description: "How do I turn off auto-renewal?" (10,286 occurrences).

**Conclusion:** Exact description repetition is substantial. A random row-level train/test split could place identical descriptions in both sets and produce an overly optimistic evaluation. Compare random-split performance with group-based evaluation that keeps identical descriptions together. Consider chronological evaluation as a separate assessment of performance on later tickets. Because the dataset is synthetic and template-generated, results should not be treated as evidence of real-world generalization.

### Issue description and category consistency

- Every exact issue description maps to exactly one category.
- Number of distinct descriptions mapping to multiple categories: 0.
- No conflicting category labels were found for identical descriptions.

**Conclusion:** The dataset has consistent category labels for identical descriptions. This reduces ambiguity for repeated text, but does not establish how well a model will classify unseen descriptions. Because many descriptions repeat, evaluation should keep identical descriptions together when measuring generalization to new text. The dataset is synthetic and template-generated, which further limits real-world conclusions.

### Category label validation

- Total tickets: 1,500,000.
- Missing category labels: 0.
- Blank or whitespace-only category labels: 0.
- Number of unique categories: 11.
- Largest category: Account Management (144,841 tickets, approximately 9.66%).
- Smallest category: Refunds (122,390 tickets, approximately 8.16%).

**Conclusion:** Every ticket has a valid, non-empty category label. The 11 categories are reasonably distributed, though not perfectly balanced. A most-frequent-category baseline would achieve approximately 9.66% accuracy. This baseline will help us assess whether trained models learn useful patterns beyond simply predicting the most common category.

### Category formatting validation

- Original unique category values: 11.
- Unique categories after trimming whitespace and normalizing letter case: 11.
- Category values with leading or trailing whitespace: 0.
- No category variants differing only by letter case were found.

**Conclusion:** Category labels have consistent formatting. No category normalization or whitespace cleaning is required based on these checks. The original category values will be preserved for model training and evaluation.

### Issue type ID and category relationship

- Unique `issue_type_id` values: 100.
- Unique category values: 11.
- Issue types mapping to multiple categories: 0.
- Categories mapping to multiple issue types: 11.
- Each observed issue type ID maps to exactly one category.

**Modeling decision:** Exclude `issue_type_id` from the initial category-prediction model because it directly identifies the target category. Using it would allow the model to rely on a lookup-like relationship instead of learning from ticket text.

**Initial modeling setup:** Use `issue_description` as the input feature and `category` as the target. Evaluate generalization using a split that keeps identical descriptions together, since repeated descriptions are common in this dataset.

**Limitation:** This relationship is specific to the inspected synthetic dataset and should not be assumed to hold in real-world support-ticket systems.

### Issue description completeness and duplication

- Total tickets: 1,500,000.
- Missing descriptions: 0.
- Blank descriptions: 0.
- Unique non-missing descriptions: 277,373.
- Duplicate rows beyond the first occurrence: 1,222,627 (approximately 81.51% of all rows).

**Conclusion:** Every ticket has a non-empty issue description, so missing-text filtering is unnecessary for the initial dataset. However, descriptions are heavily repeated. A random row-level train/test split could place identical descriptions in both sets and produce an overly optimistic evaluation.

**Modeling decision:** Preserve the descriptions and use a group-based split that keeps identical descriptions together when evaluating generalization to unseen text. Because the dataset is synthetic and template-generated, results should not be interpreted as guaranteed real-world performance.

### Category-related words in issue descriptions

A word-level exploratory check searched for selected words from each category label in the issue descriptions. The script ignored the words `and`, `access`, `management`, `how`, and `to`.

| Category | Descriptions matching selected words | Percentage |
|---|---:|---:|
| Account Management | 160,035 | 10.67% |
| Authentication & Access | 13,585 | 0.91% |
| Billing | 48,674 | 3.24% |
| Bugs & Errors | 12,713 | 0.85% |
| Data Sync | 241,385 | 16.09% |
| Integrations & API | 131,435 | 8.76% |
| Onboarding & How-To | 0 | 0.00% |
| Performance | 25,848 | 1.72% |
| Refunds | 0 | 0.00% |
| Security | 14,204 | 0.95% |
| Subscription | 25,427 | 1.70% |

**Interpretation:** Some category-related words occur in descriptions, but this check only searches selected literal words. A zero count does not mean that descriptions lack relevant clues, and a match does not establish target leakage. The percentages overlap because a description can match more than one category's word list.

**Modeling decision:** Preserve the original descriptions for the initial text-classification model. Do not strip category-related words based on this exploratory check alone. Evaluate generalization using a group-based split that keeps identical descriptions together.

**Limitation:** This is a synthetic, template-generated dataset. Word-occurrence results do not establish real-world classification performance.

### Issue type ID completeness

- Total tickets: 1,500,000.
- Missing `issue_type_id` values: 0.
- Blank or whitespace-only `issue_type_id` values: 0.
- Unique issue type IDs: 100.
- Most frequent issue type: `data_sync_status_check` (25,518 tickets).

**Conclusion:** Every ticket has a populated issue type ID. However, this column maps directly to the target category and will be excluded from the initial category-prediction model to prevent target leakage. Data completeness does not make a feature appropriate for modeling.

### Ticket ID validation

- Total tickets: 1,500,000.
- Missing ticket IDs: 0.
- Unique ticket IDs: 1,500,000.
- Duplicate ticket IDs: 0.
- Minimum ticket ID: 1.
- Maximum ticket ID: 1,500,000.

**Conclusion:** Every ticket has a unique, non-missing identifier. The IDs cover the range from 1 to 1,500,000.

**Modeling decision:** Exclude `ticket_id` from model features because it is an identifier rather than a meaningful description of the customer's issue. Retain it when needed to trace predictions back to individual records.

### Duplicate ticket record validation

- Total rows: 1,500,000.
- Total columns: 38.
- Completely duplicated rows across all columns: 0.
- Duplicate rows after excluding `ticket_id`: 0.

**Conclusion:** No complete duplicate ticket records were found, either including or excluding the unique ticket identifier. No record removal is needed based on complete-row duplication.

**Important distinction:** Repeated issue descriptions are common, but repeated descriptions alone do not make two ticket records duplicates. Different tickets can legitimately contain identical text.

**Modeling decision:** Preserve all ticket records for now. Handle repeated descriptions through the train/test evaluation strategy rather than deleting tickets automatically.

### Ticket creation timestamp validation

- Total tickets: 1,500,000.
- Missing `created_at` values: 0.
- Invalid timestamps under the expected `%Y-%m-%d %H:%M:%S` format: 0.
- Earliest creation timestamp: `2022-01-01 00:04:00`.
- Latest creation timestamp: `2024-12-30 23:58:00`.

**Ticket counts by year:**

- 2022: 371,773.
- 2023: 506,603.
- 2024: 621,624.

**Conclusion:** All creation timestamps are present and parse successfully using the expected format. The timestamps cover 2022 through 2024.

**Modeling consideration:** A chronological split is feasible for evaluating performance on later-created tickets. Because descriptions repeat frequently, we must also consider overlap between training and test descriptions. The increasing yearly record counts are properties of this synthetic dataset and should not be interpreted as evidence of real-world support-ticket growth.

### Dataset row order and chronological evaluation

- Total tickets: 1,500,000.
- Adjacent row pairs where `created_at` moves backward: 750,064.
- The dataset is not sorted in chronological order.
- Ticket IDs increase sequentially, but creation timestamps do not follow that order.

**Conclusion:** Original row order and ticket ID order cannot be used as a substitute for chronological order.

**Modeling decision:** For chronological evaluation, explicitly sort records by `created_at` before creating time-based training and test sets. Also check for repeated descriptions across the split, since repeated text is common in this dataset.

**Limitation:** The timestamps are valid, but their presence alone does not establish that the synthetic dataset represents real-world temporal patterns.

### Duplicate creation timestamp analysis

- Total tickets: 1,500,000.
- Unique creation timestamps: 730,445.
- Distinct timestamps shared by multiple tickets: 383,652.
- Tickets whose timestamp is shared by at least one other ticket: 1,153,207 (approximately 76.88%).
- Maximum tickets sharing one timestamp: 17.

**Conclusion:** Multiple tickets frequently share the same creation timestamp.

**Modeling decision:** When constructing a chronological train/test split, select a cutoff between timestamp groups so tickets with identical timestamps remain on the same side of the split. This prevents identical timestamps from being divided across training and test sets at the cutoff.

**Important limitation:** Keeping timestamps together does not prevent identical issue descriptions from appearing on both sides. Description overlap must be evaluated separately.

### Creation timestamp format validation

- Total timestamps checked: 1,500,000.
- Values matching the expected `YYYY-MM-DD HH:MM:SS` format: 1,500,000.
- Values with unexpected formatting: 0.

**Conclusion:** Every creation timestamp matches the expected string format. Combined with the earlier successful parsing check, this confirms that no timestamp-format cleanup is needed for the inspected column.

**Modeling decision:** Preserve the original timestamps and parse them explicitly when preparing chronological evaluation data.

### Creation timestamp range validation

- Total tickets: 1,500,000.
- Timestamps before `2022-01-01 00:00:00`: 0.
- Timestamps after `2024-12-31 23:59:59`: 0.
- Earliest timestamp: `2022-01-01 00:04:00`.
- Latest timestamp: `2024-12-30 23:58:00`.

**Conclusion:** All creation timestamps fall within the expected 2022–2024 date range. No records need to be filtered based on this range check.

**Modeling decision:** Retain all records for now and use the validated timestamps when constructing chronological evaluation data.

**Limitation:** This check confirms consistency with the inspected date range. It does not establish that the synthetic timestamps reproduce real-world support-ticket patterns.

### Region column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Blank or whitespace-only values: 0.
- Unique non-missing regions: 6.

| Region | Ticket count |
|---|---:|
| North America | 509,011 |
| Europe | 420,929 |
| Asia | 269,873 |
| South America | 150,448 |
| Oceania | 74,973 |
| Africa | 74,766 |

**Conclusion:** The `region` column is complete and contains six distinct region labels. No missing-value cleaning is required for this column.

**Modeling decision:** Do not automatically include `region` in the initial text-only category prediction model. Its predictive usefulness and suitability as an input available at ticket creation will be evaluated separately.

**Limitation:** These are distributions from a synthetic dataset and should not be interpreted as real-world customer geographic proportions.

### Language column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Blank or whitespace-only values: 0.
- Unique non-missing languages: 6.
- Values with leading or trailing whitespace: 0.

| Language | Ticket count |
|---|---:|
| English | 250,599 |
| German | 250,370 |
| French | 250,071 |
| Portuguese | 249,744 |
| Spanish | 249,732 |
| Mandarin | 249,484 |

**Conclusion:** The `language` column is complete, contains six distinct language labels, and has no leading or trailing whitespace. No cleaning is required based on these checks.

**Modeling decision:** Do not automatically use `language` as a feature in the initial text-only category prediction model. Its usefulness and availability at ticket creation will be assessed separately.

**Limitation:** The near-equal distribution is a property of this synthetic dataset and should not be interpreted as a real-world customer language distribution.

### Priority column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Blank or whitespace-only values: 0.
- Unique non-missing priorities: 4.
- Values with leading or trailing whitespace: 0.

| Priority | Ticket count |
|---|---:|
| Medium | 501,607 |
| Low | 420,377 |
| High | 396,683 |
| Urgent | 181,333 |

**Conclusion:** The `priority` column is complete and contains four consistently formatted labels. No missing-value or whitespace cleaning is required based on these checks.

**Modeling decision:** Do not automatically include priority in the initial text-only category prediction model. First establish whether priority is assigned before or after category classification and whether it is available at prediction time.

**Limitation:** The observed distribution belongs to a synthetic dataset and should not be treated as a real-world support-ticket priority distribution.

### Category and priority relationship

- Total tickets inspected: 1,500,000.
- Missing category values: 0.
- Missing priority values: 0.
- Categories inspected: 11.
- Priority levels observed: 4.
- Every category contains all four priority levels.

**Priority counts by category:**

| Category | High | Low | Medium | Urgent |
|---|---:|---:|---:|---:|
| Account Management | 27,927 | 56,211 | 50,021 | 10,682 |
| Authentication & Access | 39,643 | 30,155 | 48,293 | 18,896 |
| Billing | 38,448 | 39,455 | 47,296 | 17,801 |
| Bugs & Errors | 46,823 | 21,432 | 36,705 | 24,420 |
| Data Sync | 42,130 | 33,313 | 47,751 | 20,138 |
| Integrations & API | 33,972 | 36,576 | 47,341 | 14,970 |
| Onboarding & How-To | 17,315 | 78,680 | 42,571 | 4,497 |
| Performance | 37,384 | 27,231 | 47,391 | 16,915 |
| Refunds | 37,468 | 22,455 | 44,658 | 17,809 |
| Security | 42,611 | 22,739 | 46,133 | 20,733 |
| Subscription | 32,962 | 52,130 | 43,447 | 14,472 |

**Conclusion:** Every category includes tickets at all four priority levels. Priority and category are not in a one-to-one relationship, although their distributions differ across categories.

**Modeling decision:** Keep `priority` out of the initial text-only category prediction baseline. Evaluate it as a possible additional feature later, after confirming it is available at prediction time and does not introduce leakage.

**Limitation:** These associations come from a synthetic dataset and do not establish real-world relationships or causal effects.

### Product column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Blank or whitespace-only values: 0.
- Unique non-missing product labels: 6.
- Values with leading or trailing whitespace: 0.

| Product | Ticket count |
|---|---:|
| Desktop Client | 250,867 |
| API Platform | 250,723 |
| Web Portal | 250,259 |
| Payment Gateway | 249,725 |
| Analytics Suite | 249,561 |
| Mobile App | 248,865 |

**Conclusion:** The `product` column is complete and contains six consistently formatted labels. No cleaning is required based on these checks.

**Modeling decision:** Keep `product` out of the initial text-only category prediction baseline. Its usefulness for category prediction can be evaluated later, provided it is available at prediction time. The dataset's statement about its usefulness for `auto_resolved` should not automatically be generalized to a different target.

**Limitation:** The near-equal product distribution is observed in a synthetic dataset and should not be interpreted as a real-world product distribution.

### Channel column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Blank or whitespace-only values: 0.
- Unique non-missing channel labels: 5.
- Values with leading or trailing whitespace: 0.

| Channel | Ticket count |
|---|---:|
| Email | 509,578 |
| Chat | 450,518 |
| Self-Service | 225,301 |
| Phone | 209,717 |
| Social Media | 104,886 |

**Conclusion:** The `channel` column is complete and contains five consistently formatted labels. No missing-value or whitespace cleaning is required based on these checks.

**Modeling decision:** Keep `channel` out of the initial text-only category prediction baseline. Its potential usefulness can be evaluated later after confirming that it is available at prediction time.

**Limitation:** The channel distribution belongs to a synthetic dataset and should not be interpreted as a real-world support-channel distribution.

### Customer segment column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Blank or whitespace-only values: 0.
- Unique non-missing customer segments: 4.
- Values with leading or trailing whitespace: 0.

| Customer segment | Ticket count |
|---|---:|
| Individual | 376,038 |
| Corporate | 374,995 |
| Small Business | 374,879 |
| Enterprise | 374,088 |

**Conclusion:** The `customer_segment` column is complete and contains four consistently formatted labels. No cleaning is required based on these checks.

**Modeling decision:** Keep `customer_segment` out of the initial text-only category prediction baseline. Its usefulness can be evaluated later after confirming that it is available at prediction time.

**Limitation:** The near-equal segment distribution is observed in a synthetic dataset and should not be interpreted as a real-world customer distribution.

### Subscription type column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Blank or whitespace-only values: 0.
- Unique non-missing subscription types: 4.
- Values with leading or trailing whitespace: 0.

| Subscription type | Ticket count |
|---|---:|
| Basic | 480,638 |
| Free | 450,058 |
| Premium | 389,879 |
| Enterprise | 179,425 |

**Conclusion:** The `subscription_type` column is complete and contains four consistently formatted labels. No missing-value or whitespace cleaning is required based on these checks.

**Modeling decision:** Keep `subscription_type` out of the initial text-only category prediction baseline. Evaluate its usefulness separately after confirming that it is available at prediction time.

**Limitation:** This distribution comes from a synthetic dataset and should not be interpreted as a real-world subscription distribution.

### Customer age column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Data type: `int64`.
- Unique non-missing ages: 57.
- Minimum age: 18.
- First quartile (25%): 32.
- Median age: 46.
- Mean age: approximately 46.00.
- Third quartile (75%): 60.
- Maximum age: 74.
- Ages below 18: 0.
- Ages below 0: 0.
- Ages above 100: 0.

**Conclusion:** The `customer_age` column is complete, uses an integer data type, and contains values between 18 and 74. No cleaning is required based on the checks performed.

**Modeling decision:** Keep customer age out of the initial text-only category prediction baseline. Consider it separately only if it is available at prediction time and provides a justified benefit.

**Limitation:** Plausible numeric ranges do not establish that synthetic customer ages represent a real-world population.

### Customer gender column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Blank or whitespace-only values: 0.
- Unique non-missing labels: 3.
- Values with leading or trailing whitespace: 0.

| Gender label | Ticket count |
|---|---:|
| Other | 501,450 |
| Female | 499,547 |
| Male | 499,003 |

**Conclusion:** The `customer_gender` column is complete and contains three consistently formatted labels. No cleaning is required based on these checks.

**Modeling decision:** Exclude `customer_gender` from the initial text-only category prediction model. It is unnecessary for the baseline, and using a sensitive personal attribute would require a clear purpose and appropriate fairness assessment.

**Limitation:** The near-equal distribution is observed in a synthetic dataset and should not be interpreted as a real-world gender distribution.

### Customer tenure column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Data type: `int64`.
- Unique non-missing values: 72.
- Minimum tenure: 0 months.
- First quartile (25%): 17 months.
- Median tenure: 35 months.
- Mean tenure: approximately 35.48 months.
- Third quartile (75%): 53 months.
- Maximum tenure: 71 months.
- Negative tenure values: 0.
- Zero-tenure records: 20,854.

**Conclusion:** The `customer_tenure_months` column is complete, contains integer values between 0 and 71, and has no negative values. Zero months may represent a newly registered customer and should not automatically be treated as invalid.

**Modeling decision:** Keep customer tenure out of the initial text-only category prediction baseline. Evaluate it separately only if it is available at prediction time and provides a justified benefit.

**Limitation:** This range check does not verify tenure against account creation dates or establish that the synthetic values reflect real customer histories.

### Previous tickets column validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Data type: `int64`.
- Unique non-missing values: 16.
- Minimum previous-ticket count: 0.
- First quartile (25%): 2.
- Median: 3.
- Mean: approximately 3.00.
- Third quartile (75%): 4.
- Maximum previous-ticket count: 15.
- Negative values: 0.
- Zero values: 74,750.

**Conclusion:** The `previous_tickets` column is complete, contains integer values from 0 to 15, and has no negative values. Zero may represent a customer's first support interaction and should not automatically be treated as invalid.

**Modeling decision:** Keep `previous_tickets` out of the initial text-only category prediction baseline. Consider it separately only if it is available at prediction time and provides a justified benefit.

**Limitation:** These checks establish basic numeric validity, not whether the recorded counts are consistent with each customer's actual support history.

### Issue complexity score validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Data type: `int64`.
- Unique non-missing values: 10.
- Minimum score: 1.
- First quartile (25%): 3.
- Median: 5.
- Mean: approximately 4.74.
- Third quartile (75%): 7.
- Maximum score: 10.
- Values below 0: 0.
- Values above 1: 1,299,639.

**Conclusion:** The `issue_complexity_score` column is complete and contains integer values from 1 to 10. Values above 1 are valid under the observed scale and must not be treated as errors.

**Modeling decision:** Keep this column out of the initial text-only category prediction baseline. Before considering it as a feature, establish how the score is generated and whether it is available at prediction time.

**Limitation:** The numeric range check does not establish how the synthetic complexity scores were assigned or whether they reflect real-world issue complexity.

### Reopen count validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Data type: `int64`.
- Unique non-missing values: 9.
- Minimum reopen count: 0.
- Maximum reopen count: 8.
- Negative values: 0.
- Zero reopenings: 1,329,568 (approximately 88.64% of all tickets).
- Median: 0.
- Third quartile (75%): 0.
- Mean: approximately 0.31.

**Value counts:**

| Reopen count | Ticket count |
|---:|---:|
| 0 | 1,329,568 |
| 1 | 40,273 |
| 2 | 40,302 |
| 3 | 39,819 |
| 4 | 40,038 |
| 5 | 2,547 |
| 6 | 2,426 |
| 7 | 2,531 |
| 8 | 2,496 |

**Conclusion:** The `reopen_count` column is complete, contains non-negative integers from 0 to 8, and has no negative values. Most tickets have no recorded reopenings. The drop in frequency between values 4 and 5 is notable and should be preserved as an observation rather than treated as an error without further evidence.

**Modeling decision:** Exclude `reopen_count` from the initial text-only category prediction baseline because reopening may occur after ticket creation. Reconsider it only for a task where it is available at prediction time.

**Limitation:** These checks establish numeric validity, not whether the reopening counts accurately reflect real-world ticket histories.

### First response time validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Data type: `float64`.
- Unique non-missing values: 7,064.
- Minimum: 0.02 hours.
- First quartile (25%): 0.19 hours.
- Median: 0.45 hours.
- Third quartile (75%): 2.32 hours.
- Mean: approximately 2.98 hours.
- Maximum: 150.45 hours.
- Negative values: 0.
- Zero values: 0.

**Conclusion:** The `first_response_time_hours` column is complete and contains no negative or zero values. Its recorded values range from 0.02 to 150.45 hours.

**Distribution observation:** The mean is substantially higher than the median, indicating a right-skewed distribution with some comparatively long first-response times.

**Data-quality note:** The maximum value is unusually large compared with the median, but it should not be classified as an error without further evidence.

**Modeling consideration:** This column measures response time and may not be available when a ticket is first created. Exclude it from a ticket-creation-time prediction model unless its availability at prediction time is established.

**Limitation:** These checks establish numeric validity, not the accuracy of the recorded response times. The dataset is synthetic, so the distribution should not be treated as representative of real-world support operations.

### Resolution time validation

- Total tickets inspected: 1,500,000.
- Missing values: 152,745 (approximately 10.18%).
- Non-missing values: 1,347,255.
- Data type: `float64`.
- Unique non-missing values: 16,734.
- Minimum: -192.00 hours.
- First quartile (25%): 0.71 hours.
- Median: 1.82 hours.
- Third quartile (75%): 10.02 hours.
- Mean: approximately 12.79 hours.
- Maximum: 7,160.78 hours.
- Negative values: 1,797.
- Zero values: 0.

**Conclusion:** The `resolution_time_hours` column contains missing values, negative durations, and very large positive durations. These findings require further investigation before the column is used for analysis or modeling.

**Missing-value handling:** Do not automatically replace missing durations with zero. Missingness may be related to ticket status or whether a ticket was resolved.

**Negative-value handling:** A negative duration is inconsistent with the usual interpretation of elapsed resolution time. Preserve the original values until their relationship with the timestamp fields and the dataset's semantics is better understood.

**Extreme-value handling:** The maximum value is unusually large compared with the median. Investigate extreme values before deciding whether any should be excluded or corrected.

**Modeling consideration:** Exclude `resolution_time_hours` from a model that predicts ticket outcomes at creation time because it is a post-creation measurement.

**Limitation:** The column's numeric values alone cannot establish whether each duration is accurate. Earlier checks found discrepancies between recorded durations and timestamp-derived durations, but the underlying cause remains unconfirmed.

### Paused hours validation

- Total tickets inspected: 1,500,000.
- Missing values: 0.
- Data type: `float64`.
- Unique non-missing values: 33,535.
- Minimum: 0 hours.
- First quartile (25%): 0 hours.
- Median: 0 hours.
- Third quartile (75%): 5.64 hours.
- Mean: approximately 21.03 hours.
- Maximum: 2,879.96 hours.
- Negative values: 0.
- Zero values: 1,073,094 (approximately 71.54%).

**Conclusion:** The `paused_hours` column is complete and contains no negative values. Approximately 71.54% of tickets have zero recorded paused time.

**Distribution observation:** The mean is substantially higher than the median, indicating a strongly right-skewed distribution. Some tickets have much larger paused-hour values than the typical ticket.

**Extreme-value note:** The maximum of 2,879.96 hours is approximately 120 days. Investigate this value and other extreme durations before deciding whether they represent valid long pauses or data-quality issues.

**Modeling consideration:** Exclude `paused_hours` from a model that predicts outcomes at ticket creation time unless it can be established that this information is available at prediction time.

**Limitation:** Numeric checks establish completeness and non-negativity, but they do not verify that the recorded paused durations accurately represent real-world events. The dataset is synthetic.

### Resolution wall-clock time validation

- Total tickets inspected: 1,500,000.
- Missing values: 152,745 (approximately 10.18%).
- Non-missing values: 1,347,255.
- Data type: `float64`.
- Unique non-missing values: 64,678.
- Minimum: 0.05 hours.
- First quartile (25%): 7.77 hours.
- Median: 29.05 hours.
- Third quartile (75%): 102.23 hours.
- Mean: approximately 105.56 hours.
- Maximum: 10,025.09 hours.
- Negative values: 0.
- Zero values: 0.

**Conclusion:** The `resolution_wallclock_hours` column contains missing values but no negative or zero values among its recorded entries.

**Distribution observation:** The mean is substantially higher than the median, indicating a right-skewed distribution with some very long recorded durations.

**Extreme-value note:** The maximum of 10,025.09 hours is approximately 418 days. Investigate extreme durations before deciding whether they represent valid records or data-quality issues.

**Missing-value note:** The number of missing values matches that found in `resolution_time_hours`. This numerical match does not prove that the same tickets are missing both values; row-level overlap should be checked separately.

**Modeling consideration:** Exclude this resolution-related measurement from a model that predicts outcomes at ticket creation time because it is not generally available at that point.

**Limitation:** These checks establish numeric validity, not the accuracy or precise semantics of the recorded durations. The dataset is synthetic.

### Overlap between missing resolution durations

The missing-value patterns of `resolution_time_hours` and `resolution_wallclock_hours` were compared row by row.

- Total tickets: 1,500,000.
- Tickets missing `resolution_time_hours`: 152,745.
- Tickets missing `resolution_wallclock_hours`: 152,745.
- Tickets missing both columns: 152,745.
- Tickets missing only `resolution_time_hours`: 0.
- Tickets missing only `resolution_wallclock_hours`: 0.
- Tickets with both values present: 1,347,255.
- Missingness masks identical: Yes.

**Conclusion:** Both resolution-duration columns have exactly the same missing-value pattern. Every ticket missing one column is also missing the other.

**Interpretation:** The shared missingness may be associated with ticket status or resolution state. This relationship should be checked directly before assigning a cause.

**Data-handling decision:** Preserve these missing values during initial inspection. Do not automatically replace them with zero, because missing duration is not equivalent to zero elapsed time.

**Modeling consideration:** Both columns represent resolution-related information and should be excluded from prediction features that must be available at ticket creation time.

### Resolution duration missingness by ticket status

The missingness of `resolution_time_hours` was compared across ticket statuses.

| Status | Total tickets | Missing resolution time | Missing percentage |
|---|---:|---:|---:|
| Cancelled | 56,343 | 56,343 | 100% |
| Closed | 1,340,913 | 0 | 0% |
| New | 754 | 754 | 100% |
| On-Hold | 10,711 | 10,711 | 100% |
| Open | 68,935 | 68,935 | 100% |
| Pending | 16,002 | 16,002 | 100% |
| Resolved | 6,342 | 0 | 0% |

**Conclusion:** In the inspected dataset, all `Closed` and `Resolved` tickets have recorded resolution durations. All `Cancelled`, `New`, `On-Hold`, `Open`, and `Pending` tickets have missing resolution durations.

**Relationship to wall-clock duration:** The earlier row-level check established that `resolution_wallclock_hours` has exactly the same missing-value pattern as `resolution_time_hours`.

**Interpretation:** Missing resolution durations are perfectly associated with status in this dataset. This pattern is consistent with durations being recorded only for `Closed` and `Resolved` tickets, although the underlying data-generation logic has not been verified.

**Data-handling decision:** Do not automatically impute missing durations as zero. Retain the missing values and consider status when analyzing resolution-time data.

**Modeling caution:** Status is not available in its final form at ticket creation time, and resolution durations are post-creation measurements. Avoid using these fields as features in a model intended to predict outcomes at ticket creation time.

### First resolved timestamp validation

- Total tickets inspected: 1,500,000.
- Missing values: 152,745 (approximately 10.18%).
- Non-missing values: 1,347,255.
- Unique non-missing timestamps: 735,316.
- Stored data type: string (`str`).
- Unparseable non-missing values: 0.
- Earliest timestamp: `2022-01-02 23:03:00`.
- Latest timestamp: `2025-02-07 22:34:00`.

**Conclusion:** All non-missing `first_resolved_at` values were successfully parsed as timestamps. The column contains missing values but no unparseable non-missing entries.

**Date-range observation:** The latest first-resolution timestamp is in February 2025, while ticket creation timestamps extend only through December 2024. Later resolution dates may be valid for tickets created earlier, so this difference alone does not indicate an error.

**Data-quality note:** Earlier checks identified 4,349 records where `first_resolved_at` precedes `created_at`. These records require a separate consistency investigation.

**Modeling consideration:** Exclude `first_resolved_at` from features used to predict ticket outcomes at creation time because it is a post-creation timestamp.

**Limitation:** Successful parsing confirms timestamp format compatibility, not chronological correctness or the accuracy of the recorded events.

### First resolution timestamp consistency

The `first_resolved_at` timestamp was compared with `created_at` for every ticket where both timestamps were present.

| Check | Ticket count |
|---|---:|
| Total tickets | 1,500,000 |
| Comparable timestamp pairs | 1,347,255 |
| First resolution earlier than creation | 4,349 |
| First resolution equal to creation | 0 |
| First resolution later than creation | 1,342,906 |

Among comparable timestamp pairs, approximately 0.32% have a first-resolution timestamp earlier than the ticket creation timestamp.

**Time-difference analysis for inconsistent records:**

- Mean difference: approximately -6,776.97 hours.
- Median difference: -6,161 hours.
- Minimum difference: approximately -14,638.67 hours.
- Maximum difference: -0.70 hours.

Differences are calculated as `first_resolved_at - created_at`.

**Conclusion:** There are 4,349 chronological inconsistencies in which `first_resolved_at` precedes `created_at`. The differences can span months, so these are not explained merely by timestamps being equal or rounded to the same minute.

**Data-handling decision:** Preserve the original timestamp values. Do not automatically replace, reorder, or discard the affected records until the cause is understood.

**Modeling consideration:** Exclude `first_resolved_at` from features used for predictions at ticket creation time because it is a post-creation timestamp.

**Limitation:** This check identifies chronological inconsistencies but does not establish their cause. The dataset is synthetic, and the underlying timestamp-generation logic has not been verified.

### Resolved timestamp validation

- Total tickets inspected: 1,500,000.
- Missing values: 152,745 (approximately 10.18%).
- Non-missing values: 1,347,255.
- Unique non-missing timestamps: 764,563.
- Stored data type: string (`str`).
- Unparseable non-missing values: 0.
- Earliest timestamp: `2022-01-01 08:58:00`.
- Latest timestamp: `2025-02-22 17:58:00`.

**Conclusion:** All non-missing `resolved_at` values were successfully parsed as timestamps. The column contains missing values but no unparseable non-missing entries.

**Date-range observation:** The latest resolution timestamp is in February 2025, later than the latest ticket creation date in December 2024. This can be valid when tickets are resolved after creation, so the date range alone does not establish an error.

**Data-quality note:** Earlier checks identified 1,802 records where `resolved_at` precedes `created_at`. These records require a separate chronological consistency check.

**Modeling consideration:** Exclude `resolved_at` from features used to predict ticket outcomes at creation time because it is a post-creation timestamp.

**Limitation:** Successful parsing establishes format compatibility, not chronological correctness or the accuracy of the recorded resolution events.

### Resolved timestamp consistency

The `resolved_at` timestamp was compared with `created_at` for all tickets where both timestamps were present.

| Check | Ticket count |
|---|---:|
| Total tickets | 1,500,000 |
| Comparable timestamp pairs | 1,347,255 |
| Resolution earlier than creation | 1,802 |
| Resolution equal to creation | 0 |
| Resolution later than creation | 1,345,453 |

**Time-difference analysis for inconsistent records:**

- Number of inconsistent records: 1,802.
- Mean difference: -5 hours.
- Median difference: -5 hours.
- Minimum difference: -5 hours.
- Maximum difference: -5 hours.
- Standard deviation: 0 hours.

Differences are calculated as `resolved_at - created_at`.

**Conclusion:** All 1,802 records with `resolved_at` earlier than `created_at` have exactly the same five-hour negative difference. The uniform offset suggests a systematic timestamp inconsistency rather than varied chronological errors.

**Data-handling decision:** Preserve the original timestamps. Do not automatically add five hours or otherwise correct these records until the timestamp-generation logic and timezone conventions are understood.

**Comparison with first-resolution timestamps:** The previously identified `first_resolved_at` inconsistencies have varied negative differences, unlike the uniform five-hour offset observed here.

**Modeling consideration:** Exclude `resolved_at` from features used to predict ticket outcomes at creation time because it is a post-creation timestamp.

**Limitation:** The uniform offset is an observed pattern; its cause has not been established. The dataset is synthetic.


### Closed timestamp validation

The `closed_at` column was checked for missing values, unique timestamps, parsing errors, and timestamp range.

| Check | Result |
|---|---:|
| Total tickets | 1,500,000 |
| Missing values | 102,744 (6.85%) |
| Non-missing values | 1,397,256 |
| Unique non-missing timestamps | 900,713 |
| Unparseable non-missing values | 0 |
| Earliest timestamp | 2022-01-01 18:45:00 |
| Latest timestamp | 2025-01-04 16:40:00 |

**Conclusion:** All non-missing `closed_at` values parsed successfully. The column contains 102,744 missing values, and 900,713 distinct non-missing timestamps.

**Timestamp-range observation:** The latest closure timestamp is later than the latest `created_at` timestamp. This may be reasonable because tickets can be closed after creation; chronological consistency still needs to be verified.

**Data-handling decision:** Preserve the original timestamps and missing values. Do not impute missing closure timestamps or change dates without further investigation.

**Modeling consideration:** Exclude `closed_at` from features used to predict ticket outcomes at creation time because it is a post-creation timestamp.

**Limitation:** This is a synthetic dataset, so observed timestamp patterns should not be treated as evidence about real-world support operations.


### Closed timestamp consistency

The `closed_at` timestamp was compared with `created_at` for all tickets where both timestamps were present.

| Check | Ticket count |
|---|---:|
| Total tickets | 1,500,000 |
| Comparable timestamp pairs | 1,397,256 |
| Closure earlier than creation | 4,496 |
| Closure equal to creation | 0 |
| Closure later than creation | 1,392,760 |

**Time-difference analysis for inconsistent records:**

- Number of inconsistent records: 4,496.
- Mean difference: -6,735.24 hours.
- Median difference: -6,101.21 hours.
- Minimum difference: -14,634.93 hours.
- Maximum difference: -0.38 hours.
- Standard deviation: 4,188.75 hours.

Differences are calculated as `closed_at - created_at`.

**Conclusion:** There are 4,496 records where `closed_at` is earlier than `created_at`. The differences vary substantially, and examples include closure dates in 2022 paired with creation dates in 2023.

**Data-handling decision:** Preserve the original timestamps. Do not automatically shift dates, impute values, or remove inconsistent records until their cause and the intended timestamp semantics are better understood.

**Modeling consideration:** Exclude `closed_at` from features used to predict ticket outcomes at creation time because it is a post-creation timestamp.

**Limitation:** The cause of these chronological inconsistencies has not been established. The dataset is synthetic, and these findings should not be generalized to real-world support operations.


### Escalation reason validation

The `escalation_reason` column was checked for missing values and distinct non-missing values.

| Check | Result |
|---|---:|
| Total tickets | 1,500,000 |
| Missing values | 1,089,215 (72.61%) |
| Non-missing values | 410,785 (27.39%) |
| Unique non-missing reasons | 3 |

**Non-missing reason distribution:**

| Escalation reason | Ticket count | Share of all tickets |
|---|---:|---:|
| Requires specialist / policy decision | 286,244 | 19.08% |
| LLM confidence below threshold | 123,949 | 8.26% |
| Customer requested human agent | 592 | 0.04% |

**Conclusion:** Three distinct non-missing escalation reasons were observed. Most records have a missing `escalation_reason` value.

**Data-handling decision:** Preserve the original values and missing entries. Do not automatically replace missing reasons with a label such as "No escalation" until the relationship with the `escalated` column and ticket status has been checked.

**Modeling consideration:** Treat `escalation_reason` as a post-decision field when building a model that predicts escalation at ticket creation time. Exclude it from the initial feature set for that task.

**Limitation:** The meaning of missing escalation reasons has not yet been established. The dataset is synthetic, so the observed distribution should not be interpreted as a real-world escalation rate.


### Escalation status and reason relationship

The `escalated` and `escalation_reason` columns were compared to understand whether missing escalation reasons correspond to non-escalated tickets.

| Escalation status | Reason recorded | Reason missing | Total |
|---|---:|---:|---:|
| No | 0 | 936,470 | 936,470 |
| Yes | 410,785 | 0 | 410,785 |
| Missing | 0 | 152,745 | 152,745 |
| Total | 410,785 | 1,089,215 | 1,500,000 |

**Findings:**

- All 410,785 tickets marked `Yes` have a non-missing escalation reason.
- All 936,470 tickets marked `No` have a missing escalation reason.
- All 152,745 tickets with a missing `escalated` value also have a missing escalation reason.
- No exceptions were observed in this dataset.

**Conclusion:** The two columns have a perfectly aligned relationship in the observed data. A missing escalation reason is associated with `escalated = No` or a missing escalation status, so the reason column should not be interpreted independently of the status column.

**Modeling consideration:** If predicting escalation, use `escalated` as the target and exclude `escalation_reason` from the initial feature set because it records the reason for an already-made decision. Missing target labels must be handled explicitly rather than automatically assigned to the negative class.

**Limitation:** This is an observed relationship in a synthetic dataset, not proof that the same relationship holds in real customer-support systems.


### Escalation status by ticket status

The relationship between `status` and `escalated` was examined using ticket counts and escalation percentages within each status.

| Ticket status | No | Yes | Missing escalation status | Total |
|---|---:|---:|---:|---:|
| Closed | 932,952 | 407,961 | 0 | 1,340,913 |
| Resolved | 3,518 | 2,824 | 0 | 6,342 |
| Open | 0 | 0 | 68,935 | 68,935 |
| Cancelled | 0 | 0 | 56,343 | 56,343 |
| Pending | 0 | 0 | 16,002 | 16,002 |
| On-Hold | 0 | 0 | 10,711 | 10,711 |
| New | 0 | 0 | 754 | 754 |
| Total | 936,470 | 410,785 | 152,745 | 1,500,000 |

**Escalation percentages among tickets with observed labels:**

- Closed: 30.42% escalated and 69.58% not escalated.
- Resolved: 44.53% escalated and 55.47% not escalated.
- Other statuses have missing escalation labels for all their tickets.

**Conclusion:** Observed escalation labels occur only for Closed and Resolved tickets. The remaining statuses have missing labels throughout.

**Modeling decision:** Do not interpret missing escalation labels as negative examples. For an escalation-prediction task, exclude `status` from the initial feature set unless its availability at the intended prediction time can be established. Define the labeled training population explicitly and investigate whether restricting it to Closed and Resolved tickets introduces selection bias.

**Limitation:** These are patterns in a synthetic dataset. They do not establish how escalation status behaves in real customer-support systems.


### Escalation status by priority

The relationship between `priority` and `escalated` was examined using ticket counts and escalation percentages among tickets with observed escalation labels.

| Priority | Total tickets | No | Yes | Missing escalation label |
|---|---:|---:|---:|---:|
| High | 396,683 | 211,398 | 145,039 | 40,246 |
| Low | 420,377 | 320,802 | 56,643 | 42,932 |
| Medium | 501,607 | 318,383 | 132,100 | 51,124 |
| Urgent | 181,333 | 85,887 | 77,003 | 18,443 |
| Total | 1,500,000 | 936,470 | 410,785 | 152,745 |

**Escalation percentages among tickets with observed labels:**

- Low: 15.01%.
- Medium: 29.32%.
- High: 40.69%.
- Urgent: 47.27%.

**Conclusion:** Escalation percentages increase across the observed priority levels from Low to Urgent. This indicates an association between priority and escalation within the labeled subset.

**Modeling consideration:** Priority may be a useful feature for escalation prediction if it is available at the intended prediction time. Missing escalation labels must not be treated as negative examples.

**Limitation:** These percentages describe only tickets with observed escalation labels, which occur exclusively in the Closed and Resolved statuses. The association does not establish causation or generalize automatically to the unlabeled tickets or real-world support operations.


### Escalation status by ticket category

The relationship between `category` and `escalated` was examined using ticket counts and escalation percentages among tickets with observed escalation labels.

| Category | No | Yes | Total labeled tickets | Escalation percentage |
|---|---:|---:|---:|---:|
| Account Management | 102,017 | 28,140 | 130,157 | 21.62% |
| Authentication & Access | 90,525 | 32,537 | 123,062 | 26.44% |
| Billing | 93,537 | 34,796 | 128,333 | 27.11% |
| Bugs & Errors | 72,453 | 43,668 | 116,121 | 37.61% |
| Data Sync | 95,246 | 33,379 | 128,625 | 25.95% |
| Integrations & API | 101,423 | 18,018 | 119,441 | 15.09% |
| Onboarding & How-To | 107,481 | 20,931 | 128,412 | 16.30% |
| Performance | 85,959 | 29,900 | 115,859 | 25.81% |
| Refunds | 47,044 | 62,858 | 109,902 | 57.19% |
| Security | 53,208 | 65,541 | 118,749 | 55.19% |
| Subscription | 87,577 | 41,017 | 128,594 | 31.90% |
| Total | 936,470 | 410,785 | 1,347,255 | 30.49% |

**Key findings:**

- Refunds has the highest observed escalation percentage at 57.19%.
- Security follows at 55.19%.
- Integrations & API has the lowest observed escalation percentage at 15.09%.
- Escalation percentages vary substantially across categories.

**Conclusion:** Ticket category is associated with different observed escalation percentages in this dataset. The association may be worth investigating as part of escalation-prediction modeling.

**Modeling consideration:** Category may be a useful feature if it is available at the intended prediction time. Evaluate its contribution using a proper held-out dataset and compare against a baseline. Do not use post-decision fields such as `escalation_reason` as predictive inputs.

**Limitation:** The percentages are calculated only for tickets with observed escalation labels. The dataset is synthetic, so these patterns do not establish causation or real-world escalation behavior.


### Ticket category and priority relationship

The relationship between `category` and `priority` was examined using ticket counts and priority percentages within each category.

| Category | High | Low | Medium | Urgent |
|---|---:|---:|---:|---:|
| Account Management | 19.28% | 38.81% | 34.54% | 7.37% |
| Authentication & Access | 28.94% | 22.01% | 35.25% | 13.79% |
| Billing | 26.89% | 27.59% | 33.07% | 12.45% |
| Bugs & Errors | 36.19% | 16.57% | 28.37% | 18.87% |
| Data Sync | 29.39% | 23.24% | 33.31% | 14.05% |
| Integrations & API | 25.57% | 27.53% | 35.63% | 11.27% |
| Onboarding & How-To | 12.10% | 55.00% | 29.76% | 3.14% |
| Performance | 29.00% | 21.12% | 36.76% | 13.12% |
| Refunds | 30.61% | 18.35% | 36.49% | 14.55% |
| Security | 32.23% | 17.20% | 34.89% | 15.68% |
| Subscription | 23.05% | 36.45% | 30.38% | 10.12% |

**Key observations:**

- Onboarding & How-To has the largest Low-priority share at 55.00%.
- Bugs & Errors has the largest High-priority share at 36.19%.
- Security has an Urgent-priority share of 15.68%.
- Priority distributions vary across categories.

**Conclusion:** Ticket category and priority are associated in the observed dataset. These differences may be useful for exploratory analysis, but they do not establish causation.

**Modeling consideration:** Both fields may be candidates for escalation prediction if they are available at the intended prediction time. Evaluate their predictive value on held-out data rather than assuming that the observed associations will improve model performance.

**Limitation:** The dataset is synthetic. These distributions should not be interpreted as evidence of real-world support-team prioritization practices.


### Escalation status by region

The relationship between `region` and `escalated` was examined using ticket counts and escalation percentages among tickets with observed escalation labels.

| Region | No | Yes | Missing escalation label | Total tickets | Escalation percentage |
|---|---:|---:|---:|---:|---:|
| Africa | 46,773 | 20,410 | 7,583 | 74,766 | 30.38% |
| Asia | 167,980 | 74,154 | 27,739 | 269,873 | 30.63% |
| Europe | 263,068 | 114,731 | 43,130 | 420,929 | 30.37% |
| North America | 317,789 | 139,635 | 51,587 | 509,011 | 30.53% |
| Oceania | 46,897 | 20,559 | 7,517 | 74,973 | 30.48% |
| South America | 93,963 | 41,296 | 15,189 | 150,448 | 30.53% |
| Total | 936,470 | 410,785 | 152,745 | 1,500,000 | 30.49% |

**Key findings:**

- Asia has the highest observed escalation percentage at 30.63%.
- Europe has the lowest observed escalation percentage at 30.37%.
- The difference between the highest and lowest rates is 0.26 percentage points.
- Escalation percentages are broadly similar across regions.

**Conclusion:** Region has little unadjusted association with escalation in the observed labeled subset. Its additional predictive value, if any, would need to be tested alongside other features.

**Modeling consideration:** Do not assume region is useful simply because it is available. Compare models with and without this feature using held-out data and appropriate evaluation metrics.

**Limitation:** The percentages exclude tickets with missing escalation labels. This is a synthetic dataset, so the observed regional patterns should not be generalized to real-world support operations.


### Escalation status by language

The relationship between `language` and `escalated` was examined using ticket counts and escalation percentages among tickets with observed escalation labels.

| Language | No | Yes | Missing escalation label | Total tickets | Escalation percentage |
|---|---:|---:|---:|---:|---:|
| English | 156,642 | 68,670 | 25,287 | 250,599 | 30.48% |
| French | 156,162 | 68,512 | 25,397 | 250,071 | 30.49% |
| German | 156,240 | 68,301 | 25,829 | 250,370 | 30.42% |
| Mandarin | 155,845 | 68,290 | 25,349 | 249,484 | 30.47% |
| Portuguese | 155,765 | 68,389 | 25,590 | 249,744 | 30.51% |
| Spanish | 155,816 | 68,623 | 25,293 | 249,732 | 30.58% |
| Total | 936,470 | 410,785 | 152,745 | 1,500,000 | 30.49% |

**Key findings:**

- Spanish has the highest observed escalation percentage at 30.58%.
- German has the lowest observed escalation percentage at 30.42%.
- The difference between the highest and lowest rates is 0.16 percentage points.
- Ticket counts are nearly balanced across the six languages.
- Escalation percentages are broadly similar across languages.

**Conclusion:** Language has little unadjusted association with escalation in the observed labeled subset. Its additional predictive value should be evaluated alongside other features rather than assumed.

**Limitation:** The percentages exclude tickets with missing escalation labels. This is a synthetic dataset, so these patterns should not be generalized to real-world support operations.


### Escalation status by customer segment

The relationship between `customer_segment` and `escalated` was examined using ticket counts and escalation percentages among tickets with observed escalation labels.

| Customer segment | No | Yes | Missing escalation label | Total tickets | Escalation percentage |
|---|---:|---:|---:|---:|---:|
| Corporate | 234,134 | 102,784 | 38,077 | 374,995 | 30.51% |
| Enterprise | 233,654 | 102,156 | 38,278 | 374,088 | 30.42% |
| Individual | 234,622 | 103,211 | 38,205 | 376,038 | 30.55% |
| Small Business | 234,060 | 102,634 | 38,185 | 374,879 | 30.48% |
| Total | 936,470 | 410,785 | 152,745 | 1,500,000 | 30.49% |

**Key findings:**

- Individual customers have the highest observed escalation percentage at 30.55%.
- Enterprise customers have the lowest observed escalation percentage at 30.42%.
- The difference between the highest and lowest rates is 0.13 percentage points.
- Ticket counts are nearly balanced across the four customer segments.
- Escalation percentages are broadly similar across segments.

**Conclusion:** Customer segment has little unadjusted association with escalation in the observed labeled subset. Its additional predictive value should be tested alongside other features rather than assumed.

**Limitation:** The percentages exclude tickets with missing escalation labels. This is a synthetic dataset, so these patterns should not be generalized to real-world support operations.


### Escalation status by subscription type

The relationship between `subscription_type` and `escalated` was examined using ticket counts and escalation percentages among tickets with observed escalation labels.

| Subscription type | No | Yes | Missing escalation label | Total tickets | Escalation percentage |
|---|---:|---:|---:|---:|---:|
| Basic | 299,935 | 131,810 | 48,893 | 480,638 | 30.53% |
| Enterprise | 112,157 | 48,960 | 18,308 | 179,425 | 30.39% |
| Free | 281,283 | 122,995 | 45,780 | 450,058 | 30.42% |
| Premium | 243,095 | 107,020 | 39,764 | 389,879 | 30.57% |
| Total | 936,470 | 410,785 | 152,745 | 1,500,000 | 30.49% |

**Key findings:**

- Premium has the highest observed escalation percentage at 30.57%.
- Enterprise has the lowest observed escalation percentage at 30.39%.
- The difference between the highest and lowest rates is 0.18 percentage points.
- Escalation percentages are broadly similar across subscription types.

**Conclusion:** Subscription type has little unadjusted association with escalation in the observed labeled subset. Its predictive value should be tested rather than assumed.

**Modeling consideration:** The dataset creator identifies `subscription_type` as noise for the separate `auto_resolved` prediction task. That warning does not automatically establish its value for escalation prediction, so it should be evaluated empirically.

**Limitation:** The percentages exclude tickets with missing escalation labels. This is a synthetic dataset, so these patterns should not be generalized to real-world support operations.


### Escalation status by product

The relationship between `product` and `escalated` was examined using ticket counts and escalation percentages among tickets with observed escalation labels.

| Product | No | Yes | Missing escalation label | Total tickets | Escalation percentage |
|---|---:|---:|---:|---:|---:|
| API Platform | 156,614 | 68,701 | 25,408 | 250,723 | 30.49% |
| Analytics Suite | 155,596 | 68,445 | 25,520 | 249,561 | 30.55% |
| Desktop Client | 157,012 | 68,331 | 25,524 | 250,867 | 30.32% |
| Mobile App | 155,103 | 68,271 | 25,491 | 248,865 | 30.56% |
| Payment Gateway | 155,922 | 68,498 | 25,305 | 249,725 | 30.52% |
| Web Portal | 156,223 | 68,539 | 25,497 | 250,259 | 30.49% |
| Total | 936,470 | 410,785 | 152,745 | 1,500,000 | 30.49% |

**Key findings:**

- Mobile App has the highest observed escalation percentage at 30.56%.
- Desktop Client has the lowest observed escalation percentage at 30.32%.
- The difference between the highest and lowest rates is 0.24 percentage points.
- Ticket counts are nearly balanced across products.
- Escalation percentages are broadly similar across products.

**Conclusion:** Product has little unadjusted association with escalation in the observed labeled subset. Its predictive value should be tested rather than assumed.

**Modeling consideration:** The dataset creator identifies `product` as noise for the separate `auto_resolved` prediction task. This does not automatically determine its usefulness for escalation prediction, so evaluate it empirically.

**Limitation:** The percentages exclude tickets with missing escalation labels. This is a synthetic dataset, so these patterns should not be generalized to real-world support operations.


### Escalation status by channel

The relationship between `channel` and `escalated` was examined using ticket counts and escalation percentages among tickets with observed escalation labels.

| Channel | No | Yes | Missing escalation label | Total tickets | Escalation percentage |
|---|---:|---:|---:|---:|---:|
| Chat | 281,016 | 123,466 | 46,036 | 450,518 | 30.52% |
| Email | 318,648 | 139,233 | 51,697 | 509,578 | 30.41% |
| Phone | 130,959 | 57,281 | 21,477 | 209,717 | 30.43% |
| Self-Service | 140,276 | 62,051 | 22,974 | 225,301 | 30.67% |
| Social Media | 65,571 | 28,754 | 10,561 | 104,886 | 30.48% |
| Total | 936,470 | 410,785 | 152,745 | 1,500,000 | 30.49% |

**Key findings:**

- Self-Service has the highest observed escalation percentage at 30.67%.
- Email has the lowest observed escalation percentage at 30.41%.
- The difference between the highest and lowest rates is 0.26 percentage points.
- Email has the most tickets, while Social Media has the fewest.
- Escalation percentages are broadly similar across channels.

**Conclusion:** Channel has little unadjusted association with escalation in the observed labeled subset. Its predictive value should be evaluated rather than assumed.

**Limitation:** The percentages exclude tickets with missing escalation labels. This is a synthetic dataset, so these patterns should not be generalized to real-world support operations.


### Escalation status by issue complexity score

The relationship between `issue_complexity_score` and `escalated` was examined by dividing the scores into five quantile-based groups. Because the score takes discrete values, the groups are not exactly equal in size.

| Complexity score group | No | Yes | Missing escalation label | Total tickets | Escalation percentage |
|---|---:|---:|---:|---:|---:|
| (0.999, 2.0] | 302,683 | 10,611 | 0 | 349,109 | 3.39% |
| (2.0, 4.0] | 264,841 | 51,399 | 0 | 351,938 | 16.25% |
| (4.0, 6.0] | 226,491 | 131,003 | 0 | 397,880 | 36.64% |
| (6.0, 7.0] | 75,610 | 81,915 | 0 | 175,219 | 52.00% |
| (7.0, 10.0] | 66,845 | 135,857 | 0 | 225,854 | 67.02% |
| Total | 936,470 | 410,785 | 152,745 | 1,500,000 | 30.49% |

**Key findings:**

- The observed escalation percentage increases across every successive complexity group.
- The lowest-score group has an escalation percentage of 3.39%.
- The highest-score group has an escalation percentage of 67.02%.
- The difference between the highest and lowest rates is 63.63 percentage points.
- All 1,500,000 tickets have a recorded complexity score.

**Conclusion:** Issue complexity has a strong unadjusted association with escalation in the observed labeled subset. It is a promising candidate feature for further evaluation.

**Modeling considerations:**

- Confirm that the complexity score is available at the time an escalation prediction would be made.
- Investigate how the score is generated to rule out target leakage or information derived from later ticket outcomes.
- Evaluate the feature using held-out data and appropriate metrics before drawing conclusions about predictive performance.

**Limitation:** The percentages exclude tickets with missing escalation labels. This is a synthetic dataset, so the observed association should not be generalized to real-world support operations.


### Escalation status by previous ticket count

The relationship between `previous_tickets` and `escalated` was examined by grouping tickets according to the number of previous tickets.

| Previous-ticket group | Total tickets | Escalation percentage |
|---|---:|---:|
| 0 previous tickets | 74,750 | 30.47% |
| 1–2 previous tickets | 560,475 | 30.53% |
| 3–5 previous tickets | 738,563 | 30.46% |
| 6–10 previous tickets | 125,803 | 30.53% |
| More than 10 previous tickets | 409 | 30.27% |
| Total | 1,500,000 | 30.49% |

**Key findings:**

- Escalation percentages are broadly similar across the previous-ticket groups.
- The highest observed rate is 30.53%, and the lowest is 30.27%, a difference of 0.26 percentage points.
- The group with more than 10 previous tickets contains only 409 tickets, so its rate should be interpreted cautiously.
- All tickets have a recorded `previous_tickets` value.

**Conclusion:** Previous ticket count has little unadjusted association with escalation in the observed labeled subset. Its additional predictive value should be evaluated using a model rather than assumed.

**Modeling consideration:** Confirm that previous-ticket counts reflect information available when a new ticket is created and do not incorporate future activity.

**Limitation:** Escalation percentages exclude tickets with missing escalation labels. This is a synthetic dataset, so the observed patterns should not be generalized to real-world support operations.


### Escalation status by customer tenure

The relationship between `customer_tenure_months` and `escalated` was examined by grouping tickets according to customer tenure.

| Customer tenure group | Total tickets | Escalation percentage among labeled tickets |
|---|---:|---:|
| 0–6 months | 145,970 | 30.43% |
| 7–12 months | 125,241 | 30.54% |
| 13–24 months | 249,769 | 30.56% |
| 25–48 months | 500,539 | 30.50% |
| More than 48 months | 478,481 | 30.44% |
| Total | 1,500,000 | 30.49% |

**Key findings:**

- Escalation percentages are broadly similar across all five tenure groups.
- The highest observed rate is 30.56%, for customers with 13–24 months of tenure.
- The lowest observed rate is 30.43%, for customers with 0–6 months of tenure.
- The difference between the highest and lowest rates is 0.13 percentage points.
- All tickets have a recorded customer tenure value.

**Conclusion:** Customer tenure has little unadjusted association with escalation in the observed labeled subset. Its additional predictive value should be evaluated using a model rather than assumed.

**Modeling consideration:** Confirm that tenure is calculated using information available when the ticket is created.

**Limitation:** Escalation percentages exclude tickets with missing escalation labels. This is a synthetic dataset, so the observed patterns should not be generalized to real-world support operations.


### Escalation status by customer age

The relationship between `customer_age` and `escalated` was examined by grouping customers into five age bands.

| Customer age group | Total tickets | Escalation percentage among labeled tickets |
|---|---:|---:|
| 24 or younger | 184,114 | 30.51% |
| 25–34 | 262,918 | 30.51% |
| 35–44 | 263,573 | 30.49% |
| 45–54 | 263,522 | 30.45% |
| 55 or older | 525,873 | 30.50% |
| Total | 1,500,000 | 30.49% |

**Key findings:**

- Escalation percentages are nearly identical across age groups.
- The highest observed rate is 30.51%, and the lowest is 30.45%.
- The difference between the highest and lowest rates is 0.06 percentage points.
- All tickets have a recorded customer age.

**Conclusion:** Customer age has very little unadjusted association with escalation in the observed labeled subset.

**Modeling consideration:** Because age is personal information and shows almost no unadjusted association with escalation, exclude it from the initial model unless a clear, justified need emerges. Evaluate feature choices using held-out data and appropriate fairness and privacy considerations.

**Limitation:** Escalation percentages exclude tickets with missing escalation labels. This is a synthetic dataset, so these patterns should not be generalized to real-world support operations.

## Escalation Status by Customer Gender

### Objective
Check whether escalation rates differ across customer gender groups.

### Findings
The dataset contains 1,500,000 tickets:

| Customer gender | Total tickets | Not escalated | Escalated | Missing escalation label | Escalation rate among labeled tickets |
|---|---:|---:|---:|---:|---:|
| Female | 499,547 | 311,665 | 136,961 | 50,921 | 30.53% |
| Male | 499,003 | 311,938 | 136,409 | 50,656 | 30.42% |
| Other | 501,450 | 312,867 | 137,415 | 51,168 | 30.52% |
| **Total** | **1,500,000** | **936,470** | **410,785** | **152,745** | **30.49%** |

- No customer gender values are missing.
- Escalation rates are very similar across all three groups.
- The difference between the highest and lowest observed escalation rates is approximately 0.11 percentage points.
- These are descriptive, unadjusted comparisons and do not establish causation.

### Modeling Decision
Exclude `customer_gender` from the initial escalation prediction model because the observed differences are small and there is no clear need to use this demographic attribute. Reconsider only if a justified use case and appropriate fairness evaluation support its inclusion.

Rows with missing escalation labels must remain unlabeled rather than being treated as non-escalated.

### Limitation
The dataset is synthetic. These results should not be interpreted as evidence of real-world customer behavior or demographic fairness.

## Reopen Count Validation and Escalation Association

### Objective
Inspect the distribution of `reopen_count`, check for missing values, and examine its unadjusted relationship with escalation status.

### Findings
- Total tickets: 1,500,000.
- Missing `reopen_count` values: 0.
- Minimum: 0; maximum: 8.
- Mean: 0.3103; median: 0.
- Tickets with `reopen_count = 0`: 1,329,568 (approximately 88.64%).
- Counts of 1–4 each occur approximately 40,000 times.
- Counts of 5–8 occur approximately 2,400–2,500 times each.
- Escalation rates vary across reopen-count values without a clear monotonic trend.
- There are 152,745 tickets with missing escalation labels. These must not be treated as non-escalated.

### Modeling Decision
Do not include `reopen_count` in the initial escalation prediction model until its availability at prediction time is established. If the value reflects events occurring after the initial escalation decision, using it could cause target leakage.

### Limitation
These are descriptive associations from a synthetic dataset. They do not establish that reopening a ticket causes escalation or prevents it.

## First Response Time Validation

### Objective
Inspect `first_response_time_hours` for missing values, invalid values, distribution, and its descriptive relationship with escalation status.

### Findings
- Total tickets: 1,500,000.
- Missing response times: 0.
- Negative response times: 0.
- Zero response times: 0.
- Minimum response time: 0.02 hours.
- Median response time: 0.45 hours (27 minutes).
- Mean response time: approximately 2.98 hours.
- Maximum response time: 150.45 hours (approximately 6.27 days).
- The mean being considerably higher than the median suggests a right-skewed distribution.
- Missingness by ticket status: 0% for every observed status.

### Association with Escalation
- Escalated = No: median 0.41 hours; mean 1.09 hours.
- Escalated = Yes: median 3.35 hours; mean 7.29 hours.
- Missing escalation label: median 0.45 hours; mean approximately 2.99 hours.

Tickets labeled as escalated have higher recorded response times on average. This is a descriptive association and does not establish causation.

### Modeling Decision
Do not include `first_response_time_hours` in the initial escalation prediction model until its timing and availability at the intended prediction point are verified. If it is recorded after the decision being predicted, using it could introduce data leakage.

### Limitation
The dataset is synthetic, and the observed association should not be generalized to real-world support operations without external validation.

## Resolution Time Validation

### Objective
Inspect `resolution_time_hours` for missing values, invalid durations, distribution, and its descriptive relationship with escalation status.

### Findings
- Total tickets: 1,500,000.
- Non-missing resolution times: 1,347,255.
- Missing resolution times: 152,745 (10.18%).
- Negative resolution times: 1,797.
- Zero resolution times: 0.
- Minimum recorded duration: -192 hours.
- Median recorded duration: 1.82 hours.
- Mean recorded duration: approximately 12.79 hours.
- Maximum recorded duration: 7,160.78 hours.

### Missingness by Status
Resolution times are missing for all tickets with statuses Cancelled, New, On-Hold, Open, and Pending. They are present for all Closed and Resolved tickets in the observed dataset.

### Association with Escalation
- Escalated = No: 936,470 records; mean 5.05 hours; median 1.50 hours.
- Escalated = Yes: 410,785 records; mean 30.46 hours; median 14.29 hours.
- Missing escalation label: 152,745 records, all with missing resolution time.

Escalated tickets have longer recorded resolution durations on average. This is a descriptive association and does not establish causation.

### Data Quality Decision
There are 1,797 negative recorded durations. A previous timestamp consistency check found that their timestamp-calculated durations were non-negative. The cause of the discrepancy is unconfirmed. Preserve the original values for now and investigate their semantics before deciding whether to correct, exclude, or otherwise handle them.

Do not replace missing resolution times with zero: missingness reflects unresolved or otherwise non-completed ticket states in the observed data.

### Modeling Decision
Exclude `resolution_time_hours` from the initial escalation prediction model because it is an outcome-related duration that may only be known after resolution. Using it to predict an earlier escalation decision could introduce target leakage.

### Limitation
The dataset is synthetic. These results should not be interpreted as real-world customer-support performance measurements.

## Paused Hours Validation

### Objective
Inspect `paused_hours` for missing values, invalid values, distribution, and its descriptive relationship with escalation status.

### Findings
- Total tickets: 1,500,000.
- Missing values: 0.
- Negative values: 0.
- Zero values: 1,073,094 (approximately 71.54%).
- Median: 0 hours.
- Mean: approximately 21.03 hours.
- Maximum: 2,879.96 hours (approximately 120 days).
- The mean is substantially higher than the median, indicating a right-skewed distribution with some large values.

### Association with Escalation
- Escalated = No: 936,470 tickets; mean 22.26 hours; median 0 hours.
- Escalated = Yes: 410,785 tickets; mean 22.25 hours; median 0 hours.
- Missing escalation label: 152,745 tickets; mean 10.25 hours; median 0 hours.

The mean paused time is almost identical for tickets labeled escalated and not escalated. This is a descriptive comparison and does not establish causation or prove that the feature has no predictive value.

### Modeling Decision
Exclude `paused_hours` from the initial escalation prediction model until its timing and availability at the intended prediction point are verified. If it accumulates during ticket handling, using it could introduce data leakage.

### Limitation
The dataset is synthetic. These findings should not be interpreted as measurements of real-world customer-support operations.

## Resolution Wall-Clock Time Validation

### Objective
Inspect `resolution_wallclock_hours` for missing values, invalid durations, distribution, and its descriptive relationship with escalation status.

### Findings
- Total tickets: 1,500,000.
- Non-missing wall-clock values: 1,347,255.
- Missing values: 152,745 (10.18%).
- Negative values: 0.
- Zero values: 0.
- Minimum recorded duration: 0.05 hours.
- Median: 29.05 hours.
- Mean: approximately 105.56 hours.
- Maximum: 10,025.09 hours (approximately 418 days).
- The mean is substantially higher than the median, indicating a strongly right-skewed distribution.

### Missingness by Status
Wall-clock values are missing for all tickets with statuses Cancelled, New, On-Hold, Open, and Pending. They are present for all Closed and Resolved tickets in the observed dataset.

### Association with Escalation
- Escalated = No: 936,470 records; mean 80.46 hours; median 17.00 hours.
- Escalated = Yes: 410,785 records; mean 162.77 hours; median 87.68 hours.
- Missing escalation label: 152,745 records, all with missing wall-clock time.

Tickets labeled as escalated have longer recorded wall-clock times on average. This is a descriptive association and does not establish causation.

### Modeling Decision
Exclude `resolution_wallclock_hours` from the initial escalation prediction model because it is an outcome-related duration that may only be known after resolution. Using it to predict an earlier escalation decision could introduce target leakage.

### Limitation
The dataset is synthetic. These values should not be interpreted as real-world support performance measurements.


## Resolution Duration Missingness Overlap

### Objective
Verify whether `resolution_time_hours` and `resolution_wallclock_hours` have missing values in exactly the same rows.

### Findings
- Both fields are missing for 152,745 tickets (10.18%).
- Both fields are present for 1,347,255 tickets (89.82%).
- No tickets have only one of these two fields missing.
- All Closed and Resolved tickets have both duration values present.
- All Cancelled, New, On-Hold, Open, and Pending tickets have both duration values missing.

### Interpretation
The two duration fields have identical missingness patterns in the inspected dataset. Missingness is associated with ticket status rather than occurring independently in each field.

This does not establish that the fields measure the same concept or that their recorded values are interchangeable.

### Modeling Decision
Do not impute missing duration values as zero. Exclude both duration fields from the initial escalation prediction model because they are outcome-related and may not be available at prediction time.

### Limitation
The dataset is synthetic. The observed status-to-missingness relationship may reflect the dataset-generation process.


## SLA Target Hours Validation

### Objective
Inspect `sla_target_hours` for missing values, invalid durations, distinct values, and descriptive association with escalation status.

### Findings
- Total tickets: 1,500,000.
- Missing values: 0.
- Zero values: 0.
- Negative values: 0.
- Number of distinct values: 4.
- Valid observed targets: 4, 24, 72, and 120 hours.

### Distribution

| SLA target (hours) | Ticket count |
|---:|---:|
| 4 | 181,333 |
| 24 | 396,683 |
| 72 | 501,607 |
| 120 | 420,377 |

### Association with Escalation
- Escalated = No: 936,470 tickets; mean SLA target approximately 71.37 hours.
- Escalated = Yes: 410,785 tickets; mean SLA target approximately 48.92 hours.
- Missing escalation label: 152,745 tickets; mean SLA target approximately 64.63 hours.

Tickets labeled as escalated have a lower average SLA target in the observed data. This is a descriptive association and does not establish causation.

### Modeling Decision
Do not automatically include `sla_target_hours` in the initial escalation model. First verify that it is assigned and available at prediction time, and assess whether it encodes priority or escalation-related policy rules.

### Limitation
The dataset is synthetic. These SLA targets should not be interpreted as real-world service-level policies.


## SLA Breach Validation

### Objective
Inspect `sla_breached` for missing values, class distribution, and its association with escalation status and ticket status.

### Findings
- Total tickets: 1,500,000.
- Missing values: 0.
- SLA not breached: 1,359,877 (90.66%).
- SLA breached: 140,123 (9.34%).

### Association with Escalation
Among tickets with known escalation labels:
- SLA not breached: 912,969 not escalated and 294,750 escalated.
- SLA breached: 23,501 not escalated and 116,035 escalated.
- Approximately 24.4% of labeled tickets without an SLA breach were escalated.
- Approximately 83.2% of labeled tickets with an SLA breach were escalated.

This is a strong descriptive association, but it does not establish causation.

### Missing Escalation Labels
- SLA not breached: 152,158 tickets have missing escalation labels.
- SLA breached: 587 tickets have missing escalation labels.
- All tickets have an SLA breach label, even when the escalation label is missing.

### Modeling Decision
Exclude `sla_breached` from the initial escalation prediction model. Its timing and relationship to the escalation outcome must be understood before considering it as a feature. It may introduce target leakage if the breach is determined after the prediction point.

### Limitation
The dataset is synthetic. The observed association should not be treated as evidence of real-world escalation behavior.


## SLA Breach Margin Validation

### Objective
Inspect `sla_breach_margin` for missing values, invalid or unusual values, and consistency with `sla_breached`.

### Findings
- Total tickets: 1,500,000.
- Non-missing values: 1,347,255.
- Missing values: 152,745 (10.18%).
- Negative values: 137,833.
- Zero values: 119.
- Positive values: 1,209,303.
- Minimum: -188 hours.
- Median: 62.89 hours.
- Maximum: 119.95 hours.

### Relationship with SLA Breach
- All 137,833 negative-margin records are labeled as SLA breaches.
- Of 1,209,303 positive-margin records, 1,359,821 are labeled as not breached and 2,227 as breached.
- Of 119 zero-margin records, 56 are labeled as not breached and 63 as breached.

The margin sign is strongly associated with the breach label, but the observed exceptions mean the two fields are not perfectly equivalent.

### Missingness
The 152,745 missing margin values match the missingness count observed in the resolution-duration fields. Further checks are needed to confirm whether they occur in exactly the same rows.

### Modeling Decision
Exclude `sla_breach_margin` from the initial escalation prediction model. Its strong association with `sla_breached` suggests that it may encode the SLA outcome, and its availability at the intended prediction time is unconfirmed.

### Limitation
The dataset is synthetic. The intended definition and sign convention of the margin have not yet been verified.


## SLA Margin and Resolution Duration Missingness Overlap

### Objective
Verify whether `sla_breach_margin` has the same missing-value pattern as `resolution_time_hours` and `resolution_wallclock_hours`.

### Findings
- All three fields are missing for the same 152,745 tickets (10.18%).
- All three fields are present for the same 1,347,255 tickets (89.82%).
- No ticket has only one or two of these three fields missing.
- All Closed and Resolved tickets have all three fields present.
- All Cancelled, New, On-Hold, Open, and Pending tickets have all three fields missing.

### Interpretation
The three fields have identical missingness patterns in the inspected dataset. This is consistent with a shared relationship to ticket status or the data-generation process, although the underlying cause has not been established.

### Modeling Decision
Exclude all three fields from the initial escalation prediction model. They are outcome-related or potentially unavailable at prediction time, and their missingness pattern is closely tied to ticket status.

### Limitation
The dataset is synthetic. The observed missingness pattern should not be assumed to represent real-world support systems.


## Customer Satisfaction Score Validation

### Objective
Inspect `customer_satisfaction_score` for missing values, distribution, and descriptive association with escalation.

### Findings
- Total tickets: 1,500,000.
- Non-missing scores: 1,346,056.
- Missing scores: 153,944 (approximately 10.26%).
- Minimum score: 1.
- Median score: 4.
- Mean score: approximately 3.64.
- Maximum score: 5.
- The observed score range is 1–5.

### Score Distribution

| Score | Ticket count |
|---:|---:|
| 1 | 40,357 |
| 2 | 144,762 |
| 3 | 370,554 |
| 4 | 500,267 |
| 5 | 290,116 |
| Missing | 153,944 |

### Association with Escalation
- Escalated = No: 935,225 scored tickets; mean approximately 4.00.
- Escalated = Yes: 410,244 scored tickets; mean approximately 2.81.
- Missing escalation label: 587 scored tickets; all have a score of 5.

Tickets labeled as escalated have lower average satisfaction scores in the observed data. This is a descriptive association and does not establish causation.

### Missingness by Status
Missing satisfaction scores occur across multiple ticket statuses. The field's missingness pattern differs from the resolution-duration fields, so it should be analyzed separately.

### Modeling Decision
Exclude `customer_satisfaction_score` from the initial escalation prediction model because it may be measured after the support experience and could introduce target leakage.

### Limitation
The dataset is synthetic. These satisfaction values should not be interpreted as real-world customer sentiment or service quality.


## Resolution Notes Validation

### Objective
Inspect `resolution_notes` for missing values, distinct values, frequency distribution, and relationship with ticket status.

### Findings
- Total tickets: 1,500,000.
- Missing notes: 96,402 (6.43%).
- Distinct non-missing notes: 10.
- The field contains a small set of repeated, template-like resolution statements.

### Missingness by Status
- Cancelled: 0 missing notes; cancellation/withdrawal note present.
- Closed: 0 missing notes.
- Resolved: 0 missing notes.
- New: all 754 notes missing.
- On-Hold: all 10,711 notes missing.
- Open: all 68,935 notes missing.
- Pending: all 16,002 notes missing.

### Data Quality Observations
Some notes contain inconsistent spacing or joined words. The low number of distinct values suggests the field is highly repetitive and may not provide meaningful generalizable text variation.

### Modeling Decision
Exclude `resolution_notes` from the initial escalation prediction model because the notes describe investigation, resolution, or other outcome-related actions that may not be available at prediction time.

### Limitation
The dataset is synthetic. These notes should not be treated as evidence of real-world support workflows.


## First Resolved Timestamp Validation

### Objective
Validate `first_resolved_at` for missing or invalid timestamps and check its ordering relative to `created_at`.

### Findings
- Total tickets: 1,500,000.
- Missing timestamps: 152,745 (10.18%).
- Invalid non-missing timestamps: 0.
- Timestamps before ticket creation: 4,349.
- Timestamps equal to ticket creation: 0.
- Timestamps after ticket creation: 1,342,906.

### Timestamp Ordering by Status
- Closed: 1,336,564 timestamps after creation and 4,349 before creation.
- Resolved: all 6,342 timestamps occur after creation.
- Cancelled, New, On-Hold, Open, and Pending: all timestamps are missing.

### Data Quality Assessment
The 4,349 timestamps preceding ticket creation are chronological anomalies. All occur in Closed tickets. Their cause has not been established.

### Modeling Decision
Exclude `first_resolved_at` from the initial escalation prediction model because it is an outcome-related timestamp that would generally be unavailable at the initial prediction point.

Preserve the original values for investigation rather than correcting them without evidence.

### Limitation
The dataset is synthetic, so the anomalies may reflect its generation process rather than real-world timestamp errors.


## Resolved Timestamp Validation

### Objective
Validate `resolved_at` for missing or invalid timestamps and compare its ordering with `created_at`.

### Findings
- Total tickets: 1,500,000.
- Missing timestamps: 152,745 (10.18%).
- Invalid non-missing timestamps: 0.
- Timestamps before ticket creation: 1,802.
- Timestamps equal to ticket creation: 0.
- Timestamps after ticket creation: 1,345,453.

### Five-Hour Anomaly
All 1,802 timestamps preceding ticket creation differ from `created_at` by exactly five hours.

- Closed: 1,794 anomalous timestamps.
- Resolved: 8 anomalous timestamps.

This consistent difference suggests a systematic offset or data-generation rule, but its cause has not been established.

### Missingness by Status
Cancelled, New, On-Hold, Open, and Pending tickets have missing `resolved_at` values. Closed and Resolved tickets have non-missing timestamps, including the identified anomalies.

### Modeling Decision
Exclude `resolved_at` from the initial escalation prediction model because it is an outcome-related timestamp that is generally unavailable at the initial prediction point.

Preserve the original timestamps until the five-hour discrepancy is understood.

### Limitation
The dataset is synthetic. The anomaly should not be assumed to represent a real-world time-zone or data-processing error.

## Closed Timestamp Validation

### Objective
Validate `closed_at` for missing or invalid timestamps and compare its ordering with `created_at`.

### Findings
- Total tickets: 1,500,000.
- Missing timestamps: 102,744 (6.85%).
- Invalid non-missing timestamps: 0.
- Timestamps before ticket creation: 4,496.
- Timestamps equal to ticket creation: 0.
- Timestamps after ticket creation: 1,392,760.

### Timestamp Anomalies
The 4,496 timestamps preceding ticket creation are distributed as follows:
- Closed: 4,331.
- Cancelled: 165.

No New, On-Hold, Open, Pending, or Resolved tickets have a non-missing `closed_at` timestamp.

### Missingness by Status
All New, On-Hold, Open, Pending, and Resolved tickets have missing `closed_at` values. Closed and Cancelled tickets have non-missing timestamps in this dataset.

### Modeling Decision
Exclude `closed_at` from the initial escalation prediction model because it is an outcome-related timestamp that would generally be unavailable when a ticket is first created.

Preserve the original timestamps and investigate the 4,496 anomalies before considering any corrections.

### Limitation
The dataset is synthetic. The timestamp anomalies do not establish that the same issue occurs in real customer-support systems.

## First-Resolved and Resolved Timestamp Comparison

### Objective
Compare `first_resolved_at` with `resolved_at` wherever both timestamps are present.

### Findings
- Total tickets: 1,500,000.
- Rows with both timestamps present: 1,347,255.
- `first_resolved_at` earlier than `resolved_at`: 148,242.
- Both timestamps equal: 1,192,568.
- `first_resolved_at` later than `resolved_at`: 6,445.
- Missing `first_resolved_at`: 152,745.
- Missing `resolved_at`: 152,745.

### Timestamp Ordering Anomalies
The 6,445 cases where `first_resolved_at` is later than `resolved_at` are distributed as follows:
- Closed: 6,404.
- Resolved: 41.

Among Resolved tickets, 2,402 have `first_resolved_at` earlier than `resolved_at`, and 3,899 have equal timestamps.

### Interpretation
The two timestamps are equal for most rows where both are present. However, 6,445 rows violate the expected ordering implied by the field names.

The exact equality could reflect how the synthetic dataset was generated or how the fields were populated. The cause of the reversed ordering has not been established.

### Modeling Decision
Exclude both timestamps from the initial escalation prediction model because they describe resolution outcomes and are generally unavailable when a ticket is first created.

Do not automatically swap or overwrite timestamps. Preserve the original values until their semantics are better understood.

### Limitation
The dataset is synthetic. These patterns should not be treated as evidence of real-world support-system behavior.

## Customer Email Validation

### Objective
Check `customer_email` for missing values, empty strings, duplicate addresses, and basic email-format inconsistencies without printing personal email addresses.

### Findings
- Total rows: 1,500,000.
- Missing email values: 0.
- Empty or whitespace-only email values: 0.
- Unique non-missing email addresses: 1,055,202.
- Rows beyond the first occurrence of an email: 444,798.
- Values matching the basic email-format check: 1,498,000.
- Values failing the basic email-format check: 2,000.

### Interpretation
Every row contains a non-empty email value. However, email addresses are repeated across multiple tickets, so they should not be treated as unique ticket identifiers.

The basic format check flags 2,000 values. This check is intentionally simple and cannot establish whether an address exists, belongs to the stated customer, or is deliverable.

### Privacy and Modeling Decision
Customer email addresses are personally identifiable information. Exclude `customer_email` from the initial category-prediction and escalation-prediction models unless a clearly justified, privacy-conscious use is established.

Avoid printing raw email addresses in logs, reports, screenshots, or shared outputs. Preserve the original dataset and investigate the format anomalies separately if needed.

### Limitation
This validation checks only a basic string pattern. It does not verify email ownership or deliverability.

## Customer Name Validation

### Objective
Check `customer_name` for missing values, blank strings, repeated names, and whitespace inconsistencies without exposing actual customer names.

### Findings
- Total rows: 1,500,000.
- Missing customer names: 0.
- Empty or whitespace-only names: 0.
- Unique non-missing names: 400.
- Rows beyond the first occurrence of a name: 1,499,600.
- Names with leading or trailing whitespace: 0.
- Names containing repeated consecutive spaces: 0.

### Interpretation
All rows have a non-empty customer name, and the inspected values show no leading/trailing whitespace or repeated consecutive spaces.

Only 400 distinct names appear across the 1.5 million tickets. Therefore, many tickets share the same name. A name alone cannot reliably identify a unique customer.

### Privacy and Modeling Decision
Exclude `customer_name` from the initial category-prediction and escalation-prediction models. Names are personally identifiable information and may encourage unintended memorization rather than useful generalization.

Do not use customer names as unique identifiers. Avoid printing raw names in logs or shared reports.

### Limitation
Repeated names do not necessarily represent the same person, and distinct names do not guarantee distinct customers. The dataset is synthetic, so these patterns should not be generalized to real customer populations.

## Ticket ID Validation — Recheck

### Objective
Revalidate `ticket_id` completeness, uniqueness, numeric parsing, and integer consistency.

### Findings
- Total rows: 1,500,000.
- Missing ticket IDs: 0.
- Unique ticket IDs: 1,500,000.
- Duplicate ticket ID rows: 0.
- Data type: `int64`.
- Minimum ticket ID: 1.
- Maximum ticket ID: 1,500,000.
- IDs that are not integer-valued: 0.
- IDs not parseable as numbers: 0.

### Interpretation
Every row has a unique, non-missing integer ticket ID. The observed IDs range from 1 to 1,500,000.

### Modeling Decision
Keep `ticket_id` as a record identifier, but exclude it from the initial category-prediction and escalation-prediction features. An identifier may encode dataset-generation or row-order patterns that do not generalize to new tickets.

### Limitation
Uniqueness and integer formatting do not establish that ticket IDs are chronological or that they represent real-world ticketing-system identifiers.

## Customer Age Validation — Recheck

### Objective
Validate `customer_age` for missing values, numeric consistency, and values outside the selected plausibility checks.

### Findings
- Total rows: 1,500,000.
- Missing ages: 0.
- Data type: `int64`.
- Minimum age: 18.
- Maximum age: 74.
- Unique age values: 57.
- Non-integer numeric ages: 0.
- Ages below 18: 0.
- Ages above 100: 0.
- Values not parseable as numbers: 0.

### Interpretation
All age values are present and stored as integers. The observed range is 18–74, with 57 distinct age values.

These checks identify no formatting or range anomalies under the selected criteria. They do not establish whether the synthetic ages are realistic or accurate.

### Modeling and Privacy Decision
Exclude `customer_age` from the initial escalation prediction model unless a clear, justified need for age-related prediction is established. Earlier analysis showed almost identical escalation rates across age groups, so age has little apparent unadjusted association with the target.

Avoid retaining or exposing demographic information unnecessarily.

### Limitation
The dataset is synthetic. Its age distribution should not be treated as representative of real customer populations.

## Customer Gender Validation — Recheck

### Objective
Validate `customer_gender` for missing values, blank strings, category consistency, and whitespace issues.

### Findings
- Total rows: 1,500,000.
- Missing values: 0.
- Empty or whitespace-only values: 0.
- Unique category values: 3.
- Female: 499,547.
- Male: 499,003.
- Other: 501,450.
- Values with leading or trailing whitespace: 0.

### Interpretation
Every row contains a non-empty gender category. The column has three distinct values, with no whitespace inconsistencies detected.

### Modeling and Privacy Decision
Exclude `customer_gender` from the initial category-prediction and escalation-prediction models unless a clear, justified need is established. Earlier analysis found nearly identical escalation rates across these groups, indicating little unadjusted association with the target.

Avoid unnecessary use or exposure of demographic information.

### Limitation
The dataset is synthetic. These category counts do not establish that the distribution represents real customers or that the recorded categories capture every individual's identity.

## Customer Tenure Validation — Recheck

### Objective
Validate `customer_tenure_months` for missing values, numeric consistency, negative values, and the observed range.

### Findings
- Total rows: 1,500,000.
- Missing values: 0.
- Data type: `int64`.
- Minimum tenure: 0 months.
- Maximum tenure: 71 months.
- Unique tenure values: 72.
- Negative tenure values: 0.
- Non-integer numeric values: 0.
- Values not parseable as numbers: 0.

### Interpretation
All customer-tenure values are present and stored as integers. The observed values cover every integer from 0 through 71 months.

No missing-value, formatting, or negative-value issues were detected.

### Modeling Decision
Do not automatically include customer tenure in the initial escalation prediction model. Earlier analysis found very similar escalation rates across tenure groups, suggesting little unadjusted association with the target.

If used later, confirm that tenure is available at prediction time and provides measurable value during evaluation.

### Limitation
The dataset is synthetic. The observed tenure range and distribution should not be assumed to represent real customer populations.

## Previous Tickets Validation — Recheck

### Objective
Validate `previous_tickets` for missing values, numeric consistency, negative counts, and the observed range.

### Findings
- Total rows: 1,500,000.
- Missing values: 0.
- Data type: `int64`.
- Minimum previous tickets: 0.
- Maximum previous tickets: 15.
- Unique values: 16.
- Negative counts: 0.
- Non-integer numeric values: 0.
- Values not parseable as numbers: 0.

### Interpretation
All values are present and stored as integers. Every integer from 0 through 15 occurs in the dataset, with no negative or non-integer values detected.

### Modeling Decision
Do not automatically include `previous_tickets` in the initial escalation prediction model. Earlier analysis found nearly identical escalation rates across previous-ticket groups, suggesting little unadjusted association with the target.

If considered later, verify that the feature is available at prediction time and assess its contribution through evaluation.

### Limitation
The dataset is synthetic. These counts should not be interpreted as a realistic distribution of customer support histories.

## Issue Complexity Score Validation — Recheck

### Objective
Validate `issue_complexity_score` for missing values, numeric consistency, integer-valued scores, and values outside the expected 1–10 range.

### Findings
- Total rows: 1,500,000.
- Missing values: 0.
- Values not parseable as numbers: 0.
- Data type: `int64`.
- Minimum score: 1.
- Maximum score: 10.
- Unique score values: 10.
- Scores below 1: 0.
- Scores above 10: 0.
- Non-integer scores: 0.

### Interpretation
Every row has an integer complexity score between 1 and 10. No missing values, invalid numeric values, or out-of-range scores were detected.

### Modeling Decision
The column may be worth evaluating as a potential escalation-prediction feature because earlier analysis found a strong association between complexity scores and observed escalation rates.

Before including it, verify that the score is available at the intended prediction time and is not derived from escalation outcomes or other post-ticket information. Association alone does not establish causation or predictive validity.

### Limitation
The dataset is synthetic. The score's range and association with escalation do not establish how complexity scores behave in real customer-support systems.

## Reopen Count Validation — Recheck

### Objective
Validate `reopen_count` for missing values, numeric consistency, negative counts, and the frequency distribution.

### Findings
- Total rows: 1,500,000.
- Missing values: 0.
- Values not parseable as numbers: 0.
- Data type: `int64`.
- Minimum reopen count: 0.
- Maximum reopen count: 8.
- Unique values: 9.
- Negative counts: 0.
- Non-integer counts: 0.

### Frequency Distribution

| Reopen count | Tickets |
|---:|---:|
| 0 | 1,329,568 |
| 1 | 40,273 |
| 2 | 40,302 |
| 3 | 39,819 |
| 4 | 40,038 |
| 5 | 2,547 |
| 6 | 2,426 |
| 7 | 2,531 |
| 8 | 2,496 |

### Interpretation
All values are non-negative integers between 0 and 8. Approximately 88.64% of tickets have a reopen count of zero. Counts of 5–8 are substantially less common than counts of 0–4.

### Modeling Decision
Do not automatically include `reopen_count` in the initial escalation prediction model. Reopening is generally an event that occurs after a ticket has been handled, so this field may not be available at the time an initial escalation prediction is made.

Earlier analysis also found no clear monotonic relationship between reopen count and escalation rate. Reconsider this feature only for a prediction task where its timing is appropriate.

### Limitation
The dataset is synthetic. The frequency distribution should not be interpreted as representative of real support-ticket reopening behavior.

## First Response Time Validation — Recheck

### Objective
Validate `first_response_time_hours` for missing values, numeric consistency, non-positive values, and distribution characteristics.

### Findings
- Total rows: 1,500,000.
- Missing values: 0.
- Values not parseable as numbers: 0.
- Data type: `float64`.
- Minimum response time: 0.02 hours.
- Maximum response time: 150.45 hours.
- Negative response times: 0.
- Zero response times: 0.
- Mean response time: 2.9848 hours.
- Median response time: 0.45 hours (27 minutes).

### Percentiles

| Percentile | Response time |
|---|---:|
| 25th | 0.19 hours |
| 50th | 0.45 hours |
| 75th | 2.32 hours |
| 95th | 15.40 hours |
| 99th | 34.64 hours |

### Interpretation
All response times are present, numeric, and strictly positive. The mean is substantially higher than the median, indicating a right-skewed distribution with a relatively small number of long response times.

### Modeling Decision
Exclude `first_response_time_hours` from the initial escalation prediction model if predictions are made when a ticket is created. This measurement is generally only known after the first response occurs and could introduce temporal leakage.

It may be useful for later operational analysis or for a different prediction task where the response time is already available.

### Limitation
The dataset is synthetic. These response-time statistics should not be interpreted as benchmarks for real customer-support operations.

## Resolution Time Validation — Recheck

### Objective
Validate `resolution_time_hours` for missing values, numeric consistency, negative or zero durations, and distribution characteristics.

### Findings
- Total rows: 1,500,000.
- Missing values: 152,745 (10.18%).
- Values not parseable as numbers: 0.
- Data type: `float64`.
- Minimum resolution time: -192.0 hours.
- Maximum resolution time: 7,160.78 hours.
- Negative durations: 1,797.
- Zero durations: 0.
- Mean resolution time: 12.7937 hours.
- Median resolution time: 1.82 hours.

### Percentiles

| Percentile | Resolution time |
|---|---:|
| 25th | 0.71 hours |
| 50th | 1.82 hours |
| 75th | 10.02 hours |
| 95th | 68.52 hours |
| 99th | 96.31 hours |

### Interpretation
The column contains 152,745 missing values and 1,797 negative durations. The mean exceeds the median, indicating a right-skewed distribution.

Negative durations are inconsistent with the ordinary interpretation of elapsed resolution time. Their cause has not been established, so the original values should be preserved rather than automatically replaced.

### Modeling Decision
Exclude `resolution_time_hours` from the initial escalation prediction model because it describes a resolution outcome and is generally unavailable at the time of ticket creation.

Do not replace missing durations with zero or silently remove negative values. Investigate the anomalies before using this column for outcome analysis.

### Limitation
The dataset is synthetic. These duration statistics and anomalies should not be interpreted as benchmarks for real support operations.

## Paused Hours Validation — Recheck

### Objective
Validate `paused_hours` for missing values, numeric consistency, negative values, and distribution characteristics.

### Findings
- Total rows: 1,500,000.
- Missing values: 0.
- Values not parseable as numbers: 0.
- Data type: `float64`.
- Minimum paused hours: 0.0.
- Maximum paused hours: 2,879.96 hours.
- Negative values: 0.
- Zero values: 1,073,094 (approximately 71.54%).
- Mean paused hours: 21.0312 hours.
- Median paused hours: 0.0 hours.

### Percentiles

| Percentile | Paused hours |
|---|---:|
| 25th | 0.00 |
| 50th | 0.00 |
| 75th | 5.64 |
| 95th | 60.44 |
| 99th | 224.0601 |

### Interpretation
All values are present, numeric, and non-negative. Approximately 71.54% of tickets have zero paused hours. The mean is substantially higher than the median, indicating a right-skewed distribution.

### Modeling Decision
Exclude `paused_hours` from the initial escalation prediction model unless it can be established that this value is available at the intended prediction time. It may reflect events that occur after ticket creation and could introduce temporal leakage.

### Limitation
The dataset is synthetic. These statistics do not establish realistic pause durations in production support systems.


## Resolution Wall-Clock Time Validation — Recheck

### Objective
Validate `resolution_wallclock_hours` for missing values, numeric consistency, invalid durations, and distribution characteristics.

### Findings
- Total rows: 1,500,000.
- Missing values: 152,745 (approximately 10.18%).
- Values not parseable as numbers: 0.
- Data type: `float64`.
- Minimum non-missing duration: 0.05 hours.
- Maximum duration: 10,025.09 hours (approximately 417.7 days).
- Negative durations: 0.
- Zero durations: 0.
- Mean duration: 105.5612 hours.
- Median duration: 29.05 hours.

### Percentiles

| Percentile | Wall-clock resolution time (hours) |
|---|---:|
| 25th | 7.77 |
| 50th | 29.05 |
| 75th | 102.23 |
| 95th | 423.88 |
| 99th | 947.1392 |

### Interpretation
All non-missing values are numeric and strictly positive. The mean is substantially higher than the median, indicating a right-skewed distribution. The maximum duration is approximately 417.7 days, which is worth noting but is not automatically an error.

### Modeling Decision
Exclude `resolution_wallclock_hours` from the initial escalation prediction model because it reflects resolution outcomes and may not be available when a new ticket is created. Its missingness may also be related to ticket status.

### Limitation
The dataset is synthetic, so these statistics should not be interpreted as evidence of real-world support-resolution durations.


## First-Resolved Timestamp Validation — Recheck

### Objective
Validate `first_resolved_at` for missing values, timestamp parsing errors, and timestamps that precede ticket creation.

### Findings
- Total rows: 1,500,000.
- Missing `first_resolved_at` values: 152,745 (approximately 10.18%).
- Non-missing timestamps that failed to parse: 0.
- First-resolved timestamps before ticket creation: 4,349.
- Earliest non-missing timestamp: 2022-01-02 23:03:00.
- Latest non-missing timestamp: 2025-02-07 22:34:00.

### Time Difference from Ticket Creation

| Statistic | Hours |
|---|---:|
| Count of valid timestamp pairs | 1,347,255 |
| Mean | 52.6071 |
| Standard deviation | 606.9211 |
| Minimum | -14,638.67 |
| 25th percentile | 5.7833 |
| Median | 20.5833 |
| 75th percentile | 65.0667 |
| Maximum | 11,822.45 |

### Interpretation
All non-missing timestamps are parseable, but 4,349 occur before ticket creation. The minimum time difference is approximately -14,638.67 hours, indicating a substantial timestamp inconsistency in at least some records. The cause has not yet been established.

The latest first-resolved timestamp falls in February 2025, even though ticket creation dates end in December 2024. A resolution timestamp occurring after the creation period is not inherently invalid, but it should be considered when reviewing the dataset's time range.

### Modeling Decision
Do not use `first_resolved_at` as a feature for predicting escalation at ticket creation. It records a resolution event that occurs after ticket creation. Preserve the original values for investigation rather than silently correcting them.

### Limitation
The dataset is synthetic. Timestamp anomalies should be reported as observed data-quality issues, not assumed to represent a particular real-world cause.


import pandas as pd

df = pd.read_parquet(
    "Data/train-00000-of-00001.parquet",
    columns=["created_at", "resolved_at"],
)

created = pd.to_datetime(
    df["created_at"],
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce",
)

resolved = pd.to_datetime(
    df["resolved_at"],
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce",
)

print("Total rows:", len(df))
print("Missing resolved_at:", df["resolved_at"].isna().sum())

print(
    "Non-missing timestamps that failed to parse:",
    (df["resolved_at"].notna() & resolved.isna()).sum(),
)

before_creation = resolved.notna() & created.notna() & (resolved < created)
print("Resolved timestamps before creation:", before_creation.sum())

print("\nResolved timestamp range:")
print("Earliest:", resolved.min())
print("Latest:", resolved.max())

print("\nTime difference from creation (hours), for valid timestamps:")
duration_hours = (resolved - created).dt.total_seconds() / 3600
print(duration_hours[resolved.notna() & created.notna()].describe())


## Resolved Timestamp Validation — Recheck

### Objective
Validate `resolved_at` for missing values, timestamp parsing errors, and timestamps that occur before ticket creation.

### Findings
- Total rows: 1,500,000.
- Missing `resolved_at` values: 152,745 (approximately 10.18%).
- Non-missing timestamps that failed to parse: 0.
- Resolved timestamps before ticket creation: 1,802.
- Earliest non-missing timestamp: 2022-01-01 08:58:00.
- Latest non-missing timestamp: 2025-02-22 17:58:00.

### Time Difference from Ticket Creation

| Statistic | Hours |
|---|---:|
| Count of valid timestamp pairs | 1,347,255 |
| Mean | 91.3863 |
| Standard deviation | 152.6729 |
| Minimum | -5.00 |
| 25th percentile | 7.5167 |
| Median | 28.20 |
| 75th percentile | 98.4167 |
| Maximum | 1,869.6333 |

### Interpretation
All non-missing timestamps are parseable. However, 1,802 resolved timestamps precede ticket creation, and the minimum time difference is exactly -5 hours. This suggests a systematic pattern that deserves further investigation; its cause is not yet confirmed.

The latest resolved timestamp falls in February 2025, later than the latest ticket creation date in December 2024. This may be possible for tickets created near the end of the dataset's time range, but should be kept in mind when interpreting the data.

### Modeling Decision
Exclude `resolved_at` from the initial escalation prediction model because it represents a resolution outcome and is not available at ticket creation. Preserve the original values rather than automatically correcting timestamps.

### Limitation
The dataset is synthetic. These anomalies should be reported as observed data-quality issues, not assumed to have a particular real-world cause.


## Closed Timestamp Validation — Recheck

### Objective
Validate `closed_at` for missing values, timestamp parsing errors, and timestamps that occur before ticket creation.

### Findings
- Total rows: 1,500,000.
- Missing `closed_at` values: 102,744 (approximately 6.85%).
- Non-missing timestamps that failed to parse: 0.
- Closed timestamps before ticket creation: 4,496.
- Earliest non-missing timestamp: 2022-01-01 18:45:00.
- Latest non-missing timestamp: 2025-01-04 16:40:00.

### Time Difference from Ticket Creation

| Statistic | Hours |
|---|---:|
| Count of valid timestamp pairs | 1,397,256 |
| Mean | 120.1990 |
| Standard deviation | 618.5678 |
| Minimum | -14,634.93 |
| 25th percentile | 34.4167 |
| Median | 77.50 |
| 75th percentile | 135.85 |
| Maximum | 11,602.28 |

### Interpretation
All non-missing timestamps are parseable. However, 4,496 closure timestamps precede ticket creation, including some with very large negative time differences. The cause has not been established, so these records should be investigated rather than automatically corrected.

The latest closure timestamp is in January 2025, later than the latest ticket creation date in December 2024. This may be possible for tickets created near the end of the dataset's time range.

### Modeling Decision
Exclude `closed_at` from the initial escalation prediction model because it records a later ticket outcome and would introduce temporal leakage if used to predict escalation at ticket creation. Preserve the original values for data-quality investigation.

### Limitation
The dataset is synthetic. These findings describe this dataset and should not be generalized to real-world support systems.


## Resolved Timestamp Anomaly Investigation

### Objective
Investigate records where `resolved_at` occurs before `created_at` and determine whether the negative time differences follow a consistent pattern.

### Findings
- Total tickets with `resolved_at` before `created_at`: 1,802.
- All 1,802 records have an exact time difference of -5 hours.
- No other negative time-difference values were observed.
- Example: ticket 2359 has `created_at` = `2024-08-19 08:51:00` and `resolved_at` = `2024-08-19 03:51:00`.

### Interpretation
The consistent five-hour difference suggests a systematic timestamp offset rather than a collection of unrelated duration errors. However, the available evidence does not establish its cause.

### Data-Quality Decision
Preserve the original timestamps. Do not add five hours automatically or treat the suspected cause as confirmed. Further investigation would be needed before correcting these values.

### Modeling Implication
Do not derive resolution durations blindly from these timestamps without accounting for the identified anomaly. Exclude resolution timestamps from features used to predict escalation at ticket creation.

### Limitation
The dataset is synthetic, and this finding applies only to the observed records.


## Closed Timestamp Anomaly Investigation

### Objective
Investigate records where `closed_at` occurs before `created_at` and determine whether the negative time differences follow a consistent pattern.

### Findings
- Tickets with `closed_at` before `created_at`: 4,496.
- The negative time differences have many different values; they do not share one consistent offset.
- Observed examples include:
  - Ticket 40: created at `2023-09-05 07:24:00`, closed at `2022-11-25 01:52:00`.
  - Ticket 154: created at `2023-09-04 07:01:00`, closed at `2022-06-18 05:46:00`.
  - Ticket 2303: created at `2023-09-04 16:28:00`, closed at `2022-10-05 17:16:00`.

### Interpretation
The negative differences vary substantially, including cases where the closure timestamp is months before ticket creation. Unlike the `resolved_at` anomaly, this pattern is not explained by one fixed offset based on the observed results. The underlying cause remains unknown.

### Data-Quality Decision
Preserve the original timestamps. Do not apply a blanket correction or silently replace these values. Any future duration analysis using `closed_at` should account for these inconsistencies.

### Modeling Implication
Exclude `closed_at` from features used to predict escalation at ticket creation because it represents a later ticket outcome and is unavailable at prediction time.

### Limitation
The dataset is synthetic. These findings describe observed records and do not establish a real-world cause.


## Closed Timestamp and Status Relationship

### Objective
Check whether missing `closed_at` values are associated with particular ticket statuses.

### Findings

| Status | Total tickets | Missing `closed_at` | Missing percentage |
|---|---:|---:|---:|
| Cancelled | 56,343 | 0 | 0% |
| Closed | 1,340,913 | 0 | 0% |
| New | 754 | 754 | 100% |
| On-Hold | 10,711 | 10,711 | 100% |
| Open | 68,935 | 68,935 | 100% |
| Pending | 16,002 | 16,002 | 100% |
| Resolved | 6,342 | 6,342 | 100% |

- Total rows: 1,500,000.
- Total missing `closed_at` values: 102,744.
- All non-missing `closed_at` values belong to `Closed` or `Cancelled` tickets.
- All `New`, `On-Hold`, `Open`, `Pending`, and `Resolved` tickets have missing `closed_at` values.

### Interpretation
In this dataset, `closed_at` missingness is perfectly associated with ticket status. Notably, tickets marked `Resolved` have no closure timestamp, while tickets marked `Closed` have one.

This is an observed dataset pattern; it does not establish the intended business meaning of each status.

### Modeling Decision
Do not use `closed_at` as a feature for predicting escalation at ticket creation. Its availability is directly tied to a later ticket status and could introduce temporal leakage.

### Limitation
The dataset is synthetic. This status-to-timestamp relationship should not be assumed to hold in real support systems.


## Initial Escalation Model — Feature Selection Plan

### Prediction Objective
Predict whether a support ticket will be escalated using information available when the ticket is created.

### Target Column
- `escalated`

Target values:
- `Yes`: escalation occurred.
- `No`: escalation did not occur.
- Missing: outcome is unavailable; do not automatically label it as `No`.

### Candidate Features for Initial Investigation
These columns may be available at ticket creation, but their timing and usefulness must be verified before modeling:

- `issue_description`
- `category`
- `product`
- `channel`
- `region`
- `language`
- `customer_age`
- `customer_gender`
- `subscription_type`
- `customer_tenure_months`
- `previous_tickets`
- `customer_segment`
- `priority`
- `issue_complexity_score`
- `sla_target_hours`

Important considerations:
- `issue_type_id` maps perfectly to `category`, so exclude it to avoid target leakage in category prediction and possible shortcut learning.
- The dataset author identifies `product`, `channel`, `customer_segment`, and `subscription_type` as noise for the `auto_resolved` target. Their usefulness for escalation prediction must be evaluated separately.
- Verify that `category`, `priority`, `issue_complexity_score`, and `sla_target_hours` are available before escalation occurs.

### Exclude from the Initial Model
Do not use these columns as initial prediction features because they represent ticket outcomes, assignment decisions, or potentially post-creation information:

- `ticket_id`
- `created_at` (exclude initially; consider temporal features only with a justified evaluation plan)
- `issue_type_id`
- `customer_name`
- `customer_email`
- `assigned_team`
- `assigned_to`
- `status`
- `escalation_reason`
- `reopen_count`
- `first_response_time_hours`
- `resolution_time_hours`
- `paused_hours`
- `resolution_wallclock_hours`
- `first_resolved_at`
- `resolved_at`
- `closed_at`
- `resolved_by`
- `resolution_notes`
- `sla_breached`
- `sla_breach_margin`
- `customer_satisfaction_score`

### Modeling Safeguards
- Do not convert missing escalation labels into `No`.
- Investigate why escalation labels are missing before deciding which rows belong in training.
- Split the data before fitting preprocessing steps.
- Evaluate class-wise precision, recall, F1-score, and the confusion matrix.
- Because descriptions repeat, test for duplicate-description leakage during evaluation.
- Describe results as findings on a synthetic dataset, not evidence of real-world performance.

### Status
Initial feature-selection plan drafted; candidate features require validation before model training.


## Escalation Target Label Availability

### Objective
Measure the availability and distribution of the `escalated` target before model training.

### Findings

| Label | Count | Percentage of all rows |
|---|---:|---:|
| No | 936,470 | 62.43% |
| Yes | 410,785 | 27.39% |
| Missing | 152,745 | 10.18% |
| Total | 1,500,000 | 100.00% |

- Rows with known escalation labels: 1,347,255 (89.82%).
- Rows with missing escalation labels: 152,745 (10.18%).
- Among labeled rows, `No` represents approximately 69.53% and `Yes` approximately 30.47%.

### Modeling Decision
For supervised training, initially retain only rows with known `escalated` labels. Do not convert missing labels to `No`.

### Limitation
Missing labels may not be random. Investigate how label availability relates to ticket status and other attributes before interpreting model performance. Results may not generalize to tickets without labels.

### Status
Target-label availability measured; missing-label selection effects remain a consideration.


## Escalation Label Missingness by Ticket Status

### Findings

Escalation label availability is completely associated with ticket status in the observed dataset:

- Closed: 1,340,913 tickets; all have escalation labels.
- Resolved: 6,342 tickets; all have escalation labels.
- Cancelled: 56,343 tickets; all escalation labels are missing.
- Open: 68,935 tickets; all escalation labels are missing.
- Pending: 16,002 tickets; all escalation labels are missing.
- On-Hold: 10,711 tickets; all escalation labels are missing.
- New: 754 tickets; all escalation labels are missing.

### Interpretation
The labeled dataset contains only Closed and Resolved tickets. Therefore, training on known labels excludes all tickets in the other five statuses.

This creates a substantial selection limitation: model performance on labeled tickets may not represent performance on newly created or still-active tickets.

### Modeling Decision
Do not use `status` as an initial prediction feature because it may not be known in its recorded form at ticket creation. Do not treat missing escalation labels as `No`.

### Limitation
The dataset is synthetic, and the reason for this label-availability pattern is unknown. The results do not establish how escalation labels are collected in real support systems.


## Priority Feature Validation — Modeling Review

### Findings
- Total records: 1,500,000.
- Missing priority values: 0.
- Observed values: Low, Medium, High, Urgent.

| Priority | Count |
|---|---:|
| Medium | 501,607 |
| Low | 420,377 |
| High | 396,683 |
| Urgent | 181,333 |

### Interpretation
The priority column is complete and contains four consistent categorical values.

### Modeling Decision
Keep `priority` as a candidate feature, pending confirmation that it is available at ticket creation and is not assigned using information about the eventual escalation outcome.

### Limitation
This validation establishes completeness and observed values, not the timing or business rules used to assign priority.


## Issue Complexity Score Validation — Modeling Review

### Findings
- Total records: 1,500,000.
- Missing values: 0.
- Minimum score: 1.
- Maximum score: 10.
- Unique scores: 10.
- Mean: 4.735445.
- Median: 5.
- Standard deviation: 2.490208.

All integer scores from 1 through 10 occur in the dataset.

### Score Frequencies

| Score | Count |
|---|---:|
| 1 | 200,361 |
| 2 | 148,748 |
| 3 | 169,106 |
| 4 | 182,832 |
| 5 | 195,697 |
| 6 | 202,183 |
| 7 | 175,219 |
| 8 | 121,713 |
| 9 | 66,565 |
| 10 | 37,576 |

### Interpretation
The column is complete and its observed values fall within the expected integer range of 1–10.

Earlier analysis found that higher complexity scores are associated with higher escalation rates. This is an observed association, not proof that complexity causes escalation.

### Modeling Decision
Keep `issue_complexity_score` as a candidate feature, pending verification that it is available at ticket creation and is not calculated using the escalation outcome or later ticket information.

### Limitation
This check validates data completeness and range only. It does not establish how the score was generated or when it became available.


## SLA Target Hours Validation — Modeling Review

### Findings
- Total records: 1,500,000.
- Missing values: 0.
- Minimum value: 4 hours.
- Maximum value: 120 hours.
- Unique values: 4, 24, 72, and 120 hours.

| SLA target hours | Count |
|---:|---:|
| 4 | 181,333 |
| 24 | 396,683 |
| 72 | 501,607 |
| 120 | 420,377 |

### Interpretation
The column is complete and contains four distinct positive SLA targets.

### Modeling Decision
Keep `sla_target_hours` as a candidate feature, pending confirmation that it is available at ticket creation and does not encode decisions made using later ticket information.

### Limitation
This check establishes completeness and observed values only. It does not establish the business rules used to assign SLA targets.


## Duplicate Issue Descriptions — Escalation Modeling

### Findings
- Total dataset rows: 1,500,000.
- Rows with known escalation labels: 1,347,255.
- Unique descriptions among labeled rows: 264,222.
- Rows beyond the first occurrence of each exact description: 1,083,033.
- Unique descriptions associated with multiple escalation labels: 55,552.

### Interpretation
Exact issue descriptions repeat frequently in the labeled dataset. Some descriptions are associated with both escalated and non-escalated outcomes, so description text alone does not determine the escalation label.

### Evaluation Decision
A random row-level split may place identical descriptions in both training and test sets, potentially producing overly optimistic estimates of generalization.

Evaluate the model using a group-aware split that keeps identical descriptions together. Compare this with a stratified random split as a diagnostic, and report the limitations of both approaches.

### Limitation
This is a synthetic dataset with repeated, template-generated descriptions. Results should not be interpreted as evidence of real-world escalation prediction performance.


## Candidate Feature Review — Escalation Prediction

### Objective
Select features that are available when a ticket is created and avoid features that encode later outcomes or introduce misleading shortcuts.

### Candidate Feature Groups

**Ticket content and classification**
- `issue_description`
- `category`
- `priority`
- `issue_complexity_score`

**Customer context**
- `customer_age`
- `customer_gender`
- `customer_tenure_months`
- `previous_tickets`
- `customer_segment`
- `subscription_type`

### Feature Timing — Category

- `category` is a candidate feature, but its availability at ticket creation has not yet been verified.
- Do not include it in the escalation model until its assignment timing is established.
- The current text-only baseline remains the reference model for comparisons.

**Other context**
- `product`
- `channel`
- `region`
- `language`
- `sla_target_hours`

### Decisions and Limitations
- The dataset author identifies `product`, `channel`, `customer_segment`, and `subscription_type` as noise for the `auto_resolved` target. Their usefulness for escalation prediction must be evaluated separately.
- Feature completeness does not establish that a feature is available at ticket creation.
- `category`, `priority`, `issue_complexity_score`, and `sla_target_hours` require verification of their assignment timing.
- `status`, `escalation_reason`, resolution fields, and other later outcomes must not be used as initial prediction features.
- The dataset is synthetic, and model performance should not be presented as proof of real-world performance.

### Next Step
Build a simple baseline using a defensible initial feature set, then compare alternatives using leakage-aware evaluation.

## Baseline Escalation Model — Text Only

### Model Setup
- **Target:** `escalated` (`Yes` / `No`)
- **Input feature:** `issue_description`
- **Text representation:** TF-IDF with unigrams and bigrams
- **Maximum features:** 50,000
- **Minimum document frequency:** 2
- **Classifier:** Logistic Regression
- **Class weighting:** Balanced
- **Maximum iterations:** 1,000
- **Training rows:** 1,078,218
- **Test rows:** 269,037
- **Split strategy:** GroupShuffleSplit, with identical descriptions assigned to only one split
- **Exact descriptions shared across splits:** 0

### Test Results

| Metric | No | Yes |
|---|---:|---:|
| Precision | 0.88 | 0.84 |
| Recall | 0.94 | 0.71 |
| F1-score | 0.91 | 0.77 |
| Support | 186,117 | 82,920 |

- Accuracy: 0.87
- Macro average F1-score: 0.84
- Weighted average F1-score: 0.87

### Confusion Matrix

Rows represent actual labels; columns represent predicted labels. Label order: `No`, `Yes`.

| Actual / Predicted | No | Yes |
|---|---:|---:|
| No | 175,045 | 11,072 |
| Yes | 24,145 | 58,775 |

### Interpretation
- The model correctly identified 58,775 escalated tickets and missed 24,145 escalated tickets in the held-out test set.
- The `Yes` class has higher precision than recall, indicating that some actual escalations are missed.
- The evaluation prevents exact-description overlap, but similar templates may still appear in both splits.
- The dataset is synthetic, and escalation labels are observed only for tickets with `Closed` or `Resolved` status. These results do not establish performance on all incoming tickets or on real support operations.
- Treat this as an initial baseline, not a production-ready model.

### Next Step
Compare the text model against a simple majority-class baseline and then investigate whether a carefully selected set of additional features improves performance under the same evaluation strategy.

## Majority-Class Baseline Comparison

### Baseline Setup
- Model: `DummyClassifier(strategy="most_frequent")`
- Training data: same group-aware training split as the text model
- Test data: same held-out test split
- Predicted class: `No` for every ticket

### Results

| Metric | Majority baseline | TF-IDF + Logistic Regression |
|---|---:|---:|
| Accuracy | 0.69 | 0.87 |
| Escalation precision | 0.00 | 0.84 |
| Escalation recall | 0.00 | 0.71 |
| Escalation F1-score | 0.00 | 0.77 |

### Interpretation
The majority-class baseline achieves 69% accuracy but identifies no escalated tickets. The text model achieves 87% accuracy and identifies 58,775 of 82,920 escalated tickets in the held-out test set.

This comparison demonstrates that the text model provides predictive signal beyond simply predicting the majority class within this synthetic dataset. It does not establish real-world generalization or production readiness.

### Next Step
Investigate whether additional features available at ticket creation improve the model. Compare changes using the same group-aware evaluation approach and continue monitoring precision, recall, F1-score, and false negatives.

## Decision Threshold Experiment — 0.50 vs 0.40

### Results

| Metric | Threshold 0.50 | Threshold 0.40 |
|---|---:|---:|
| Escalation precision | 0.84 | 0.66 |
| Escalation recall | 0.71 | 0.78 |
| Escalation F1-score | 0.77 | 0.72 |
| Accuracy | 0.87 | 0.81 |
| False positives | 11,072 | 33,109 |
| False negatives | 24,145 | 18,143 |

### Interpretation
Lowering the threshold from 0.50 to 0.40 detected 6,002 additional actual escalations while producing 22,037 additional false positives on the same test set.

Threshold 0.40 increases escalation recall but reduces precision and F1-score. Threshold selection should reflect the operational costs of missed escalations and unnecessary human reviews rather than accuracy alone.

### Limitations
- These results come from a synthetic dataset and a group-aware held-out test split.
- The threshold comparison uses the same fitted model and test examples; it does not establish production performance.
- A threshold should ultimately be selected using validation data and operational cost requirements, with the final test set reserved for unbiased evaluation.






















































