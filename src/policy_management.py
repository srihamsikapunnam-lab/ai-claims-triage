import json
from typing import List, Dict, Any

class Policy:
    """Represents a single policy with content, category, and enabled status."""
    
    def __init__(self, content: str, category: str, enabled: bool = True):
        self.content = content
        self.category = category
        self.enabled = enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary for JSON serialization."""
        return {
            'content': self.content,
            'category': self.category,
            'enabled': self.enabled
        }
    
    def __repr__(self):
        return f"Policy(content='{self.content}', category='{self.category}', enabled={self.enabled})"

class PolicyManager:
    """Manages a collection of policies with import/export and evaluation capabilities."""
    
    # Class attribute to store all policies
    policy_list: List[Policy] = []
    
    def evaluate(self, user_input: str, category: str = "general") -> Dict[str, Any]:
        """
        Evaluate user input against policies in the specified category.
        
        Args:
            user_input: The text to evaluate
            category: The policy category to check against
            
        Returns:
            Dictionary with evaluation results
        """
        violations = []
        relevant_policies = [policy for policy in self.policy_list 
                           if policy.category == category and policy.enabled]
        
        for policy in relevant_policies:
            if self._check_violation(user_input, policy.content):
                violations.append({
                    'policy_content': policy.content,
                    'severity': 'high' if 'prohibited' in policy.content.lower() else 'medium'
                })
        
        return {
            'has_violations': len(violations) > 0,
            'violation_count': len(violations),
            'violations': violations,
            'policies_checked': len(relevant_policies)
        }
    
    def _check_violation(self, user_input: str, policy_content: str) -> bool:
        """
        Check if user input violates a specific policy.
        Improved version with better keyword matching.
        """
        user_input_lower = user_input.lower()
        policy_lower = policy_content.lower()
        
        # Extract the main subject from the policy
        prohibited_keywords = []
        
        # Look for patterns like "X is prohibited", "Y is not allowed", etc.
        patterns = [
            ('prohibited', 'prohibited'),
            ('forbidden', 'forbidden'), 
            ('not allowed', 'not allowed'),
            ('banned', 'banned'),
            ('requires', 'requires'),
            ('must be', 'must be')
        ]
        
        for pattern, keyword in patterns:
            if pattern in policy_lower:
                # Extract what comes before the pattern
                parts = policy_lower.split(pattern)
                if parts[0]:
                    # Get the main subject (last few words before the pattern)
                    subject = parts[0].strip().split()[-2:]  # Last 2 words
                    prohibited_keywords.extend(subject)
                break
        
        # Also add obvious keywords from policy
        if 'credit card' in policy_lower:
            prohibited_keywords.extend(['credit card', 'card number', 'credit'])
        if 'medical' in policy_lower or 'diagnosis' in policy_lower:
            prohibited_keywords.extend(['diagnose', 'illness', 'sickness', 'medical'])
        if 'hate speech' in policy_lower:
            prohibited_keywords.extend(['hate', 'racist', 'discriminat'])
        if 'commercial' in policy_lower or 'promotion' in policy_lower:
            prohibited_keywords.extend(['buy', 'purchase', 'product', 'amazing'])
        
        # Check if any prohibited keywords appear in user input
        for keyword in prohibited_keywords:
            if keyword in user_input_lower:
                return True
        
        return False
    
    def analyze(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input across all policy categories.
        
        Args:
            user_input: The text to analyze
            
        Returns:
            Dictionary with analysis results across all categories
        """
        categories = set(policy.category for policy in self.policy_list)
        results = {}
        
        for category in categories:
            results[category] = self.evaluate(user_input, category)
        
        total_violations = sum(result['violation_count'] for result in results.values())
        
        return {
            'overall_violations': total_violations,
            'category_breakdown': results,
            'input_length': len(user_input),
            'categories_checked': list(categories)
        }
    
    def export_policies(self, filename: str):
        """Export policies to a JSON file."""
        try:
            # Convert policies to a list of dictionaries
            policies_data = [policy.to_dict() for policy in PolicyManager.policy_list]
            
            with open(filename, 'w') as file:
                json.dump(policies_data, file, indent=4)  # indent=4 for pretty printing
                
            print(f"Policies exported successfully to {filename}")
            
        except Exception as e:
            print(f"An error occurred during export: {e}")
    
    def import_policies(self, filename: str):
        """Import policies from a JSON file."""
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                
            imported_count = 0
            for policy_data in data:
                # Basic validation for required fields
                if all(key in policy_data for key in ['content', 'category', 'enabled']):
                    # Check for duplicate based on content and category
                    is_duplicate = any(policy.content == policy_data['content'] and 
                                     policy.category == policy_data['category'] 
                                     for policy in PolicyManager.policy_list)
                    
                    if not is_duplicate:
                        policy = Policy(
                            policy_data['content'],
                            policy_data['category'],
                            policy_data['enabled']
                        )
                        PolicyManager.policy_list.append(policy)
                        imported_count += 1
                    else:
                        print(f"Warning: Duplicate policy skipped - '{policy_data['content']}' in category '{policy_data['category']}'")
                else:
                    print(f"Warning: Skipped invalid policy data due to missing fields: {policy_data}")
                    
            print(f"Successfully imported {imported_count} policies from {filename}.")
            
        except FileNotFoundError:
            print(f"Error: The file {filename} was not found.")
        except json.JSONDecodeError:
            print(f"Error: The file {filename} contains invalid JSON.")
        except Exception as e:
            print(f"An unexpected error occurred during import: {e}")
    
    def list_policies(self) -> List[Policy]:
        """Return a list of all current policies."""
        return PolicyManager.policy_list.copy()
    
    def add_policy(self, content: str, category: str, enabled: bool = True):
        """Add a new policy to the manager."""
        # Check for duplicates
        is_duplicate = any(policy.content == content and policy.category == category 
                          for policy in PolicyManager.policy_list)
        
        if not is_duplicate:
            policy = Policy(content, category, enabled)
            PolicyManager.policy_list.append(policy)
            print(f"Policy added: {content}")
        else:
            print(f"Warning: Policy already exists - '{content}' in category '{category}'")
    
    def clear_policies(self):
        """Clear all policies from the manager."""
        PolicyManager.policy_list.clear()
        print("All policies cleared.")

# Example usage and testing
if __name__ == "__main__":
    # Create a policy manager
    manager = PolicyManager()
    
    # Add some sample policies
    manager.add_policy("Sharing personal information is prohibited", "privacy", True)
    manager.add_policy("Hate speech is not allowed", "content", True)
    manager.add_policy("Commercial advertising requires approval", "commercial", True)
    manager.add_policy("Medical advice must be from certified professionals", "medical", True)
    
    # Test evaluation
    test_input = "I want to share my credit card number"
    result = manager.evaluate(test_input, "privacy")
    print(f"Evaluation result: {result}")
    
    # Test analysis
    analysis = manager.analyze(test_input)
    print(f"Analysis result: {analysis}")
    
    # Export policies
    manager.export_policies("policies.json")
    
    # List current policies
    print("Current policies:")
    for policy in manager.list_policies():
        print(f"  - {policy}")