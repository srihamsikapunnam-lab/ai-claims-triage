# AI Claims Triage - Model Card
---
## Model Details
- **Developed by**: Person A (Data & ML Lead)
- **Model Type**: XGBClassifier
- **Version**: v1.0
- **Creation Date**: 2025-11-07

## Performance Metrics
- **Auc Score**: 0.99
- **Accuracy**: >95%
- **Precision**: >90%
- **Recall**: >85%
- **F1 Score**: >87%

## Features
**Total Features**: 12
- **patient_age**: Age of the patient in years
- **gender**: Gender of the patient (encoded)
- **hospital_id**: No description available
- **diagnosis_code**: Medical diagnosis code (encoded)
- **claimed_amount**: Total amount claimed for the procedure
- **billed_items_count**: Number of items billed
- **previous_claims_count**: Number of previous claims by patient
- **insurer_id**: No description available
- **doc_missing_flag**: Whether documents are missing (boolean)
- **length_of_stay**: Number of days in hospital
- **claimed_per_day**: Average claimed amount per day
- **amount_per_item**: Average amount per billed item

## Training Data
- **Size**: 953,554 claims
- **Sources**: Multiple Kaggle healthcare fraud datasets
- **Preprocessing**: Standardized, cleaned, and feature engineered

## Limitations & Considerations
### Data Limitations
- Trained on synthetic and real healthcare data mixtures
- Class imbalance present in some datasets
- Limited demographic diversity in some source datasets

### Ethical Considerations
- Should not be used as sole decision-making tool
- Requires human review for high-stakes decisions
- Potential for bias across demographic groups
- Regular fairness audits recommended

### Usage Recommendations
- Use as triage system to flag suspicious claims
- Combine with human expert review
- Monitor performance drift over time
- Retrain periodically with new data

## Intended Use
- **Primary Use**: Insurance claim fraud detection and triage
- **Users**: Insurance claims processors and auditors
- **Output**: Fraud probability score and explanatory factors

## Maintenance
- **Retraining Schedule**: Quarterly or when performance drops below 0.95 AUC
- **Monitoring**: Continuous performance and fairness monitoring
- **Version Control**: Git-based model versioning