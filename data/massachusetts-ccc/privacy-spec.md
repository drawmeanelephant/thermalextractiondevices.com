# Massachusetts CCC — Privacy and Excluded-Field Specification

State: massachusetts  ·  Generator: state_ingest-0.1

## Excluded field names

- `agent_email`
- `agent_first_name`
- `agent_last_name`
- `agent_name`
- `application_notes`
- `business_address`
- `business_address_1`
- `business_address_2`
- `business_email`
- `business_phone`
- `ein`
- `ein_tin`
- `email`
- `email_address`
- `establishment_address_1`
- `establishment_address_2`
- `fax`
- `fein`
- `internal_notes`
- `lat`
- `latitude`
- `lon`
- `longitude`
- `mailing_address_1`
- `mailing_address_2`
- `mailing_city`
- `mailing_state`
- `mailing_zip_code`
- `notes_comments`
- `phone`
- `phone_number`
- `tin`

## Sensitive-value patterns scanned

- EIN/TIN (`NN-NNNNNNN`)
- Email addresses
- Phone numbers
- Full street addresses
- Raw coordinates

## Entity allowlists

### affected_product

- `package_label`
- `packaged_date`
- `tested_on_date`
- `source_product_text`
- `source_product_identifier`
- `commercial_product_label`
- `package_size_text`
- `product_form`
- `cultivar_candidate_text`
- `sold_between`
- `advisory_date`
- `advisory_source`

### contaminant

- `name`
- `source_name`
- `unit`
- `matrix`
- `appears_in`
- `advisories`
- `notes`

### dataset

- `title`
- `slug`
- `official_source_url`
- `json_url`
- `format`
- `reporting_period`
- `source_last_updated`
- `retrieval_date`
- `row_count`
- `columns`
- `disclaimer`
- `clarification`

### license

- `legal_name`
- `license_number`
- `license_type`
- `program`
- `status`
- `commence_ops`
- `municipality`
- `county`
- `cultivation_environment`
- `cultivation_tier`
- `license_start_date`
- `license_expiration_date`

### organization

- `legal_name`
- `license_numbers`
- `license_types`
- `program`
- `municipality`

### requirement

- `title`
- `citation`
- `regulator`
- `official_source_url`
- `notes`

### safety_advisory

- `title`
- `advisory_date`
- `canonical_url`
- `concern`
- `consumer_instructions`
- `date_ranges`
- `affected_product_count`
- `product_category_summary`
- `testing_date_range`
- `packaged_date_range`
- `sale_date_range`
- `revision_status`

### testing_laboratory

- `legal_name`
- `license_number`
- `license_type`
- `program`
- `status`
- `commence_ops`
- `municipality`
- `related_jurisdiction`
- `related_requirements`
- `related_safety_advisories`
