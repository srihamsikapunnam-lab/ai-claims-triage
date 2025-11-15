
# AI Claims Triage - Fairness Audit Report
## Generated: 2025-11-15 00:25

## Executive Summary
- **Dataset**: 46,556 insurance claims
- **Overall Accuracy**: 42.1%
- **Fraud Rate**: 18.8%

## Gender Fairness Analysis
   sample_size  actual_fraud_rate  predicted_fraud_rate  accuracy  false_positive_rate  false_negative_rate  avg_fraud_probability
M      11551.0           0.345425              0.439356  0.818111             0.210686             0.127318               0.344730
F      13503.0           0.351700              0.505443  0.752499             0.309459             0.133291               0.380328

## Age Group Fairness Analysis  
       sample_size  actual_fraud_rate  predicted_fraud_rate  accuracy  false_positive_rate  false_negative_rate
18-30      11638.0           0.129490              0.636450  0.389930             0.641595             0.398142
31-50      16239.0           0.308948              0.812673  0.476076             0.743539             0.032689
51-70       7947.0           0.130615              0.664024  0.425569             0.637140             0.157033
71+        10732.0           0.109765              0.700429  0.369456             0.685891             0.181664

## Key Fairness Metrics
- Demographic Parity Difference: 0.0661
- Equal Opportunity Difference: 0.0060

## Recommendations
1. Monitor model performance across demographic groups
2. Consider fairness-aware retraining if disparities persist
3. Regular fairness audits in production
