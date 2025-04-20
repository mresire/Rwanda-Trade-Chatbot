import json
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rwanda_trade_bot_1 import RwandaTradeBot

class RwandaTradeBotTester:
    def __init__(self, bot=None, openai_api_key=None):
        if bot:
            self.bot = bot
        else:
            self.bot = RwandaTradeBot(openai_api_key=openai_api_key)
        
        self.test_cases = []
        self.results = []
    
    def load_test_cases(self, file_path=None):
        """Load test cases from file or use default ones if not provided"""
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self.test_cases = json.load(f)
        else:
            # Default test cases
            self.test_cases = [
                {
                    "query": "What are the requirements to export roasted coffee?",
                    "expected_keywords": ["roasted coffee", "NAEB", "license"]
                },
                {
                    "query": "How do I import electrical appliances to Rwanda?",
                    "expected_keywords": [""]
                },
                {
                    "query": "Do I need a certificate to export goods to China?",
                    "expected_keywords": ["certificate", "China"]
                },
                {
                    "query": "What is required to import fertilizers into Rwanda?",
                    "expected_keywords": ["fertilizer", "customs", "declaration"]
                },
                {
                    "query": "Can I export snakes from Rwanda?",
                    "expected_keywords": [""]
                },
                {
                    "query": "Is there a fee to export goods through Gatuna border?",
                    "expected_keywords": [""]
                },
                {
                    "query": "What permits do I need to import a car from Tanzania?",
                    "expected_keywords": ["car", "import", "customs"]
                },
                {
                    "query": "How do I register my agrochemical business?",
                    "expected_keywords": ["agrochemical", "RICA"]
                },
                {
                    "query": "How can I import radioactive materials?",
                    "expected_keywords": [""]
                },
                {
                    "query": "Do I need a special license to import food items?",
                    "expected_keywords": [""]
                }
            ]
        
        print(f"Loaded {len(self.test_cases)} test cases")
        return self.test_cases
    
    def run_tests(self):
        """Run all test cases and compute metrics"""
        print("Running tests...")
        self.results = []
        
        for i, test_case in enumerate(self.test_cases):
            print(f"Test case {i+1}/{len(self.test_cases)}: {test_case['query']}")
            
            # Run the query through the bot
            response = self.bot.query(test_case["query"])
            
            # Compute metrics
            keyword_matches = sum(1 for keyword in test_case["expected_keywords"] if keyword.lower() in response.lower())
            keyword_coverage = keyword_matches / len(test_case["expected_keywords"]) * 100
            
            # Has citation check
            has_citation = "source" in response.lower() or "www" in response.lower() or "http" in response.lower()
            
            result = {
                "query": test_case["query"],
                "response": response,
                "keyword_coverage": keyword_coverage,
                "has_citation": has_citation
            }
            
            self.results.append(result)
        
        return self.results
    
    def generate_report(self, output_file="Tests/test_results.csv"):
        """Generate a report of test results"""
        if not self.results:
            print("No test results to report. Run tests first.")
            return
        
        # Calculate overall metrics
        avg_keyword_coverage = sum(r["keyword_coverage"] for r in self.results) / len(self.results)
        citation_rate = sum(1 for r in self.results if r["has_citation"]) / len(self.results) * 100
        
        # Create DataFrame for CSV export
        df = pd.DataFrame(self.results)
        df.to_csv(output_file, index=False)
        
        print("\n===== Test Report =====")
        print(f"Tests run: {len(self.results)}")
        print(f"Average keyword coverage: {avg_keyword_coverage:.2f}%")
        print(f"Citation rate: {citation_rate:.2f}%")
        print(f"Detailed results saved to: {output_file}")
        
        # Return overall metrics
        return {
            "avg_keyword_coverage": avg_keyword_coverage,
            "citation_rate": citation_rate,
            "total_tests": len(self.results)
        }

# Example usage
if __name__ == "__main__":
    # Replace with your OpenAI API key or set as environment variable
    tester = RwandaTradeBotTester(openai_api_key=os.environ["OPENAI_API_KEY"])
    
    # Load test cases (uses default if not provided)
    tester.load_test_cases()
    
    # Run tests
    tester.run_tests()
    
    # Generate report
    tester.generate_report()