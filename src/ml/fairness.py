import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import pickle
import sys
    # Add src to Python path
sys.path.append(str(Path(__file__).parent.parent))
    
from data.data_loader import DataLoader
from data.data_unifier import DataUnifier
from data.preprocessor import ClaimPreprocessor

logger = logging.getLogger(__name__)

class FairnessAnalyzer:
    def __init__(self, model_path="../../models/fraud_model_v1.pkl", 
                 preprocessor_path="../../models/model_artifacts/preprocessor.pkl"):
        self.model_path = Path(model_path)
        self.preprocessor_path = Path(preprocessor_path)
        self.model = None
        self.preprocessor_data = None
        
    def load_model_and_preprocessor(self):
        """Load the trained model and preprocessor"""
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(self.preprocessor_path, 'rb') as f:
            self.preprocessor_data = pickle.load(f)
        
        logger.info("Model and preprocessor loaded for fairness analysis")
        
    def analyze_fairness(self, features, true_labels, protected_attributes):
        """
        Analyze model fairness across protected attributes
        
        Parameters:
        - features: DataFrame with features
        - true_labels: Series with true labels
        - protected_attributes: Dict of {attribute_name: Series}
        """
        predictions = self.model.predict(features)
        probabilities = self.model.predict_proba(features)[:, 1]
        
        fairness_report = {}
        
        for attr_name, attr_values in protected_attributes.items():
            logger.info(f"Analyzing fairness for {attr_name}...")
            fairness_report[attr_name] = self._analyze_attribute_fairness(
                attr_values, true_labels, predictions, probabilities, attr_name
            )
            
        return fairness_report
    
    def _analyze_attribute_fairness(self, attribute, true_labels, predictions, probabilities, attr_name):
        """Analyze fairness for a single protected attribute"""
        unique_groups = attribute.unique()
        group_metrics = {}
        
        for group in unique_groups:
            mask = (attribute == group)
            group_true = true_labels[mask]
            group_pred = predictions[mask]
            group_proba = probabilities[mask]
            
            if len(group_true) > 0:  # Ensure group has samples
                group_metrics[group] = {
                    'count': len(group_true),
                    'fraud_rate': group_true.mean(),
                    'accuracy': accuracy_score(group_true, group_pred),
                    'precision': precision_score(group_true, group_pred, zero_division=0),
                    'recall': recall_score(group_true, group_pred, zero_division=0),
                    'prediction_rate': group_pred.mean(),
                    'avg_probability': group_proba.mean()
                }
        
        return group_metrics
    
    def calculate_disparity_metrics(self, fairness_report):
        """Calculate disparity metrics between groups"""
        disparity_report = {}
        
        for attr_name, group_metrics in fairness_report.items():
            groups = list(group_metrics.keys())
            if len(groups) < 2:
                continue
                
            # Calculate disparities
            prediction_rates = [metrics['prediction_rate'] for metrics in group_metrics.values()]
            precision_scores = [metrics['precision'] for metrics in group_metrics.values()]
            recall_scores = [metrics['recall'] for metrics in group_metrics.values()]
            
            disparity_report[attr_name] = {
                'prediction_rate_disparity': max(prediction_rates) - min(prediction_rates),
                'precision_disparity': max(precision_scores) - min(precision_scores),
                'recall_disparity': max(recall_scores) - min(recall_scores),
                'demographic_parity_violation': any(pr > 0.1 for pr in prediction_rates)  # Threshold of 10%
            }
            
        return disparity_report
    
    def plot_fairness_analysis(self, fairness_report, save_path="../../models/fairness_analysis.png"):
        """Create visualization of fairness analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Model Fairness Analysis Across Protected Attributes', fontsize=16)
        
        for idx, (attr_name, group_metrics) in enumerate(fairness_report.items()):
            if idx >= 4:  # Limit to 4 attributes for clarity
                break
                
            ax1 = axes[idx // 2, idx % 2]
            
            # Prepare data for plotting
            groups = list(group_metrics.keys())
            fraud_rates = [metrics['fraud_rate'] for metrics in group_metrics.values()]
            prediction_rates = [metrics['prediction_rate'] for metrics in group_metrics.values()]
            
            x = np.arange(len(groups))
            width = 0.35
            
            ax1.bar(x - width/2, fraud_rates, width, label='Actual Fraud Rate', alpha=0.7)
            ax1.bar(x + width/2, prediction_rates, width, label='Predicted Fraud Rate', alpha=0.7)
            ax1.set_xlabel(attr_name)
            ax1.set_ylabel('Rate')
            ax1.set_title(f'Fairness Analysis: {attr_name}')
            ax1.set_xticks(x)
            ax1.set_xticklabels([str(g) for g in groups], rotation=45)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Fairness plot saved to {save_path}")
        
    def generate_fairness_report(self, fairness_report, disparity_report):
        """Generate comprehensive fairness report"""
        report_lines = []
        report_lines.append("# FAIRNESS ANALYSIS REPORT")
        report_lines.append("=" * 50)
        
        for attr_name, group_metrics in fairness_report.items():
            report_lines.append(f"\n## Protected Attribute: {attr_name}")
            report_lines.append("-" * 40)
            
            for group, metrics in group_metrics.items():
                report_lines.append(f"\n**Group: {group}** (n={metrics['count']})")
                report_lines.append(f"  - Actual Fraud Rate: {metrics['fraud_rate']:.3f}")
                report_lines.append(f"  - Predicted Fraud Rate: {metrics['prediction_rate']:.3f}")
                report_lines.append(f"  - Accuracy: {metrics['accuracy']:.3f}")
                report_lines.append(f"  - Precision: {metrics['precision']:.3f}")
                report_lines.append(f"  - Recall: {metrics['recall']:.3f}")
                
            if attr_name in disparity_report:
                disp = disparity_report[attr_name]
                report_lines.append(f"\n**Disparity Analysis:**")
                report_lines.append(f"  - Prediction Rate Disparity: {disp['prediction_rate_disparity']:.3f}")
                report_lines.append(f"  - Precision Disparity: {disp['precision_disparity']:.3f}")
                report_lines.append(f"  - Recall Disparity: {disp['recall_disparity']:.3f}")
                report_lines.append(f"  - Demographic Parity Violation: {disp['demographic_parity_violation']}")
                
        return "\n".join(report_lines)

def run_fairness_analysis():
    """Run comprehensive fairness analysis using existing unified data"""
    logging.basicConfig(level=logging.INFO)
    
    import sys
    from pathlib import Path
    
    # Add src to Python path
    sys.path.append(str(Path(__file__).parent.parent))
    
    from data.preprocessor import ClaimPreprocessor
    
    print("=== RUNNING FAIRNESS ANALYSIS (USING EXISTING DATA) ===")
    
    # Load existing unified data instead of reprocessing
    unified_path = Path("../../data/processed/unified_claims_v1.csv")
    if not unified_path.exists():
        print("❌ Unified data not found. Run data pipeline first.")
        return
    
    # Load the unified data
    unified_df = pd.read_csv(unified_path)
    print(f"Loaded unified data: {unified_df.shape}")
    
    # Use preprocessor only for feature engineering, not data loading
    preprocessor = ClaimPreprocessor()
    features, processed_df = preprocessor.preprocess_data(unified_df.head(10000))  # Use sample for speed
    
    # Check if target exists
    if 'is_fraud' not in processed_df.columns:
        print("❌ ERROR: 'is_fraud' column not found in processed data")
        print("Available columns:", processed_df.columns.tolist())
        return
    
    target = processed_df['is_fraud']
    
    # Define protected attributes for fairness analysis
    protected_attributes = {}
    
    # Add gender if available
    if 'gender' in processed_df.columns:
        protected_attributes['gender'] = processed_df['gender']
    
    # Add age groups
    if 'patient_age' in processed_df.columns:
        protected_attributes['age_group'] = pd.cut(
            processed_df['patient_age'], 
            bins=[0, 30, 50, 100], 
            labels=['young', 'middle', 'senior']
        )
    
    # Add age_group if already exists
    if 'age_group' in processed_df.columns:
        protected_attributes['age_group'] = processed_df['age_group']
    
    if not protected_attributes:
        print("❌ No protected attributes found for fairness analysis")
        print("Available columns:", processed_df.columns.tolist())
        return
    
    # Initialize fairness analyzer
    analyzer = FairnessAnalyzer()
    analyzer.load_model_and_preprocessor()
    
    # Run fairness analysis
    fairness_report = analyzer.analyze_fairness(features, target, protected_attributes)
    disparity_report = analyzer.calculate_disparity_metrics(fairness_report)
    
    # Generate visualizations and report
    analyzer.plot_fairness_analysis(fairness_report)
    fairness_text = analyzer.generate_fairness_report(fairness_report, disparity_report)
    
    # Save report - CREATE DOCS FOLDER IF NOT EXISTS
    docs_path = Path('../../docs')
    docs_path.mkdir(exist_ok=True)
    
    with open(docs_path / 'fairness_report.md', 'w') as f:
        f.write(fairness_text)
    
    print("\n" + fairness_text)
    print(f"\n✅ Fairness analysis complete!")
    print(f"📊 Plot saved to: models/fairness_analysis.png")
    print(f"📄 Report saved to: docs/fairness_report.md")
    
    return fairness_report, disparity_report
run_fairness_analysis()