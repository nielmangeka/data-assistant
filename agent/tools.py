from openai import OpenAI
from tester.validator import TesterConfig
import json

class AgenConfig():

    def __init__(self):
        self.MODEL = "llama3.2"
        self.api_key = 'ollama'
        self.ollama_base_url = "http://localhost:11434/v1"

        self.openai = OpenAI(base_url=self.ollama_base_url, 
                             api_key=self.api_key
                            )
        
        self.system_prompt = """
        You are a BigQuery Data Dictionary Assistant. Your role is to:
        1. Analyze a BigQuery metadata that given to you as list of json format : 
            ```
            json
            {}
            ```
        2. Understand user questions about where to find data
        3. Identify the most relevant tables in our data warehouse (based on metadata given to you)
        4. Provide clear explanations of why tables are relevant
        
        You have access to:
        - A searchable data dictionary with table {}
        - Vector similarity capabilities for matching queries to tables
        - Reasoning capabilities to interpret complex queries
        
        Always:
        - Be precise about table names and descriptions
        - Highlight key columns that match the query
        - Indicate your confidence in each recommendation
        - Offer to provide more details when needed
        """
    
    def catalog_assitant(self, metadata: dict, user_question:str):
        prompt = f"""
        System: {self.system_prompt.format(metadata, metadata)}
        
        User Question: {user_question}
        
        Search Results:
        results_str = [
            Table: table_name"
            Similarity Score: similiarity_score"
            Description: Table Description"
            Columns: List of Columns"
            
        ]
        
        Your task is to:
        1. Analyze which tables are most relevant to the question. You can elaborate with the tables column
        2. Explain why each recommended table matches the query
        3. Highlight any important columns that specifically answer the question
        4. Provide your response in a helpful, natural language format
        5. If matched table more than ten tables, you have to ranked the similiarity. 
        6. Get ten tables after ranked the similiarity
        7. Provide only the table name and example query how to use the table
        8. Do not answer or provide anything if user query are not releated with data dictionary topic
        """

        try:
            print('Asking BigQuery Assistant ... \n')
            response = self.openai.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt}, 
                    {"role": "user", "content": prompt}
                    ]
                ).choices[0].message.content

            if response:
                print('Validation process ...\n\n')

                checker = TesterConfig()._reviewer(
                    metadata,
                    response
                )
                
                if checker:
                    data = json.loads(checker)
                    
                    if data["is_acceptable"] == True:
                        return response
                    elif data["is_acceptable"] == False:
                        return data["feedback"]
                    else:
                        print('is_acceptable is None')
                        return None
                else:
                    print('No result from Validator')
            else:
                print('No result from Agent')

        except Exception as e:
            print(e)