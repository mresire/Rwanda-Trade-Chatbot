import os
import json
import pandas as pd
from openai import OpenAI

class RwandaTradeBot:
    def __init__(self, data_dir="rwanda_trade_data", openai_api_key=None):
        # Set up OpenAI API key
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        elif "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY environment variable")
        
        self.data_dir = data_dir
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        
        # Create simplified memory
        self.chat_history = []
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load the trade data
        self.trade_data = self._load_trade_data()
        print(f"Loaded {len(self.trade_data)} trade procedures")
    
    def _load_trade_data(self):
        """Load trade procedures data from JSON file"""
        # Check different possible locations for the JSON file
        json_file = f"{self.data_dir}/rwanda_trade_procedures.json"
        
        if not os.path.exists(json_file):
            # Try alternate location
            alternate_file = "rwanda_trade_procedures.json"
            if os.path.exists(alternate_file):
                json_file = alternate_file
            else:
                raise FileNotFoundError(f"Could not find rwanda_trade_procedures.json in either {self.data_dir} directory or current directory")
        
        print(f"Loading data from {json_file}")
        with open(json_file, 'r') as f:
            procedures = json.load(f)
        
        # Preprocess the procedures to create a more searchable format
        processed_data = []
        
        for procedure in procedures:
            processed_procedure = {
                "title": procedure.get('title', 'N/A'),
                "url": procedure.get('url', 'N/A'),
                "procedure_id": procedure.get('procedure_id', 'N/A'),
                "description": procedure.get('description', 'No description available'),
                "keywords": self._extract_keywords(procedure)
            }
            processed_data.append(processed_procedure)
        
        # Save a CSV version for easier inspection
        df = pd.DataFrame(processed_data)
        df.to_csv(f"{self.data_dir}/processed_procedures.csv", index=False)
        print(f"Saved processed data to {self.data_dir}/processed_procedures.csv")
        
        return processed_data
    
    def _extract_keywords(self, procedure):
        """Extract relevant keywords from a procedure to improve searchability"""
        title = procedure.get('title', '').lower()
        desc = procedure.get('description', '').lower()
        
        # Extract common trade-related terms
        keywords = []
        
        # Product types
        product_types = ['coffee', 'tea', 'electronics', 'textile', 'animal', 'plant', 
                        'food', 'medical', 'vehicle', 'cattle', 'fish', 'poultry']
        
        # Document types
        document_types = ['certificate', 'license', 'permit', 'clearance', 'origin', 
                          'export', 'import', 'documentation']
        
        # Borders and locations
        locations = ['gatuna', 'rusumo', 'kagitumba', 'rusizi', 'cyanika', 'nemba', 
                    'mombasa', 'dar es salaam', 'corniche']
        
        # Check for these terms in title and description
        for term in product_types + document_types + locations:
            if term in title or term in desc:
                keywords.append(term)
        
        return keywords
    
    def _format_chat_history(self):
        """Format chat history for inclusion in the prompt"""
        formatted_history = ""
        for i, message in enumerate(self.chat_history[-5:]):  # Only include last 5 messages
            role = "Human" if message["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {message['content']}\n\n"
        return formatted_history
    
    def _find_relevant_procedures(self, query):
        """Find procedures relevant to the user's query using ChatGPT"""
        system_message = """You are a helpful assistant that helps find relevant trade procedures for Rwanda.
        Given a user's query about import/export requirements in Rwanda, your task is to:
        1. Identify 3-5 keywords from the query that are most relevant for searching trade procedures
        2. Return ONLY these keywords separated by commas and nothing else
        For example, if the query is "How do I export coffee from Rwanda?", you should return "coffee, export".
        """
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
            max_tokens=20
        )
        
        # Extract keywords from the response
        keywords = response.choices[0].message.content.lower().split(',')
        keywords = [k.strip() for k in keywords]
        
        print(f"Extracted keywords: {keywords}")
        
        # Find relevant procedures based on keywords
        relevant_procedures = []
        
        for procedure in self.trade_data:
            # Score each procedure based on keyword matches
            score = 0
            
            # Check title (higher weight)
            title = procedure['title'].lower()
            for keyword in keywords:
                if keyword in title:
                    score += 3
            
            # Check description
            desc = procedure['description'].lower()
            for keyword in keywords:
                if keyword in desc:
                    score += 1
            
            # Check keywords
            for keyword in keywords:
                if keyword in procedure['keywords']:
                    score += 2
            
            if score > 0:
                relevant_procedures.append((score, procedure))
        
        # Sort by relevance score
        relevant_procedures.sort(reverse=True, key=lambda x: x[0])
        
        # Take top 5 most relevant procedures
        top_procedures = [proc for _, proc in relevant_procedures[:5]]
        
        return top_procedures
    
    def query(self, question):
        """Answer a user query about Rwanda trade requirements"""
        # Add question to chat history
        self.chat_history.append({"role": "user", "content": question})
        
        try:
            # Find relevant procedures
            relevant_procedures = self._find_relevant_procedures(question)
            
            if not relevant_procedures:
                response = "I couldn't find specific information about that in the Rwanda Trade Portal data. Please try asking about specific import/export procedures, documents, or products."
                self.chat_history.append({"role": "assistant", "content": response})
                return response
            
            # Format the relevant procedures as context
            context = ""
            sources = []
            
            for proc in relevant_procedures:
                context += f"PROCEDURE: {proc['title']}\n"
                context += f"URL: {proc['url']}\n"
                context += f"DESCRIPTION: {proc['description']}\n\n"
                sources.append(proc['url'])
            
            # Format chat history
            chat_history = self._format_chat_history()
            
            # Create the prompt for ChatGPT
            system_message = """You are an expert assistant specialized in Rwanda import and export requirements.
            Answer the user's question about trade regulations, procedures, and requirements in Rwanda.
            
            Use ONLY the context provided to answer the question. If you don't know the answer based on the context,
            say "I don't have enough information about that" and suggest the user visit the Rwanda Trade Portal
            for more detailed information.
            
            Always cite your sources at the end of your response with direct links to the relevant procedures on Rwanda Trade Portal.
            
            When answering questions about specific products or procedures, provide:
            1. Required documents
            2. Fees (if available)
            3. Step-by-step process (if available)
            4. Any special requirements or restrictions
            5. Where to apply/obtain the required permits or licenses
            """
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Previous conversation:\n{chat_history}\n\nContext information:\n{context}\n\nQuestion: {question}"}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.2
            )
            
            answer = response.choices[0].message.content
            
            # Add citations if not already included
            if sources and "Source:" not in answer and "Sources:" not in answer:
                answer += "\n\nSources:\n"
                for source in set(sources):
                    answer += f"- {source}\n"
            
            # Add response to chat history
            self.chat_history.append({"role": "assistant", "content": answer})
            
            return answer
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(error_msg)
            return error_msg

# Example usage
if __name__ == "__main__":
    # Initialize the bot with your OpenAI API key
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        openai_api_key = input("Please enter your OpenAI API key: ")
    
    try:
        trade_bot = RwandaTradeBot(openai_api_key=openai_api_key)
        
        # Test query
        print("\nRwanda Trade Bot initialized. You can ask questions about trade procedures.")
        print("Type 'exit' to quit.\n")
        
        while True:
            query = input("Ask a question: ")
            if query.lower() == 'exit':
                break
            
            try:
                response = trade_bot.query(query)
                print("\nResponse:")
                print(response)
                print("\n" + "-"*80 + "\n")
            except Exception as e:
                print(f"Error processing query: {str(e)}")
    except Exception as e:
        print(f"Error initializing bot: {str(e)}")
        print("Make sure your OpenAI API key is valid and has access to the required models.")