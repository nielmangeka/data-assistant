from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import time

load_dotenv(override=True)

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

class TesterConfig():

    def __init__(self):
        self.MODEL = "llama3.2"
        self.api_key = 'ollama'
        self.ollama_base_url = "http://localhost:11434/v1"

        # self.openai = OpenAI(base_url=self.ollama_base_url, 
        #                      api_key=self.api_key
        #                     )

        self.openai = OpenAI(
            api_key=os.getenv("GOOGLE_API_KEY"), 
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        self.system_prompt = """
        You are an Expert Reviewer and also a Senior Data Engineer / Principal Data Engineer.
        Your role is to:
        1. You will given a result of BigQuery Data Dictionary Assistant.
            ```
            BigQuery Data Dictionary Assistant result : 
            {}
            ```

        2. Understand and Analyze the result above.
        3. Identify is the list of table recomendation in result already match with the metadata or not
        4. Provide correct answer if the result above are not correct
        5. Provide all the conclusion with this format : 
            ```
            Table: table_name
            Similarity Score: similiarity_score (in percent)
            Description: Table Description
            Columns: List of Columns
            Justification : justification
            ```

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
    
    def _reviewer(self, 
                  metadata: dict, 
                  agent_result: str,

                ):
        
        prompt = f"""
        System: {self.system_prompt.format(agent_result, metadata)}
        
        User Question: Is the BigQuery Data Dictionary Assistant result are correct?
        
        Your task is to:
        1. Analyze the answer of BigQuery Data Dictionary Assistant that given to you
        2. Compare the answer of BigQuery Data Dictionary Assistant with BigQuery Schema that given to you
        3. If you think the the answer of BigQuery Data Dictionary Assistant is not acceptable then provide the correct answer
        4. Your answer should provide at least 10 tables the releated with user question
        5. Do not provide any tables that are not in data dictionary
        6. Do not return the result without list of tables
        """

        try:

            response = self.openai.beta.chat.completions.parse(
                model="gemini-2.0-flash", 
                messages=[
                    {"role": "system", "content": self.system_prompt}, 
                    {"role": "user", "content": prompt}
                ], 
                response_format=Evaluation
            )
            resp = response.choices[0].message.content
            time.sleep(5)
            return resp

        except Exception as e:
            print(e)