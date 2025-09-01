import os
from typing import Dict, List, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import pandas as pd
import json
from datetime import datetime

from .data_loader import EmissionsDataLoader
from .emissions_analyzer import EmissionsAnalyzer
from .document_processor import DocumentProcessor
from .quality_assessor import EmissionsQualityAssessor
from .utils import df_to_text

class EmissionsInsightsAgent:
    """Main agent orchestrating emissions analysis and insights"""
    def __init__(self, model_version: str = "gemini-2.5-flash"):
        self.model_version = model_version
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_version,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1
        )
        
        # Initialize components
        self.data_loader = EmissionsDataLoader(data_path="data/raw")
        self.doc_processor = DocumentProcessor()
        self.quality_assessor = EmissionsQualityAssessor()
        
        # Load data
        self.emissions_data = None
        self.analyzer = None
        
        # Setup prompts
        self._setup_prompts()
    
    def initialize(self, data_path: str = "data/raw"):
        """Initialize agent with data"""
        print("Initializing Emissions Insights Agent...")
        # Create data summary from emissions data
        self.emissions_data = self.data_loader.load_data(files=['scope1.csv', 'scope2.csv', 'scope3.csv'])
        self.analyzer = EmissionsAnalyzer(self.emissions_data)
        self.emissions_data_summary = self._prepare_data_summary()
        
        # Process PDF documents
        pdf_files = {
            "ghg_protocol": f"{data_path}/ghg-protocol-revised.pdf",
            "peer1": f"{data_path}/peer1_emissions_report.pdf",
            "peer2": f"{data_path}/peer2_emissions_report.pdf"
        }
        
        for name, path in pdf_files.items():
            if os.path.exists(path):
                print(f"Processing {name} ({path.split('.')[-1]}) file to create vector store")
                self.doc_processor.process_pdf(path, name)
        # Precompute data summary and store as an instance variable

        print("✅ Agent initialized successfully!")

    def _prepare_data_summary(self) -> str:
        """Prepare summary of emissions data for context
        
        returns:
            summary: text, Summary of emissions data
        """
        totals = self.analyzer.calculate_total_emissions()
        scope1_grouped_df = (self.emissions_data['scope1_df']
                             .groupby(['Facility', 'Activity_Type', "Fuel_Type"])[['CO2e_Tonnes']]
                             .sum())
        scope2_grouped_df = (self.emissions_data['scope2_df']
                             .groupby(['Facility', 'Energy_Type'])
                             .agg(CO2e_Tonnes=('CO2e_Tonnes', 'sum'), 
                                  Renewable_Percentage=('Renewable_Percentage', 'mean'
                            )))
        scope3_grp_cate_activity_df = (self.emissions_data['scope3_df']
                                       .groupby(['Category', 'Activity_Description'])[['CO2e_Tonnes']]
                                       .sum())
        scope3_grp_supplier_df = (self.emissions_data['scope3_df']
                                  .groupby(['Supplier'])[['CO2e_Tonnes']]
                                  .sum())
        
        summary = f"""
Total Emissions Overview:
- Scope 1: {totals.get('scope1', 0):.2f} tCO2e
- Scope 2: {totals.get('scope2', 0):.2f} tCO2e  
- Scope 3: {totals.get('scope3', 0):.2f} tCO2e
- Total: {totals.get('total', 0):.2f} tCO2e

<Scope 1 emissions summary by facility, activity type, and fuel type>
{df_to_text(scope1_grouped_df, decimal_places=2)}
</Scope 1 emissions summary by facility, activity type, and fuel type>

<Scope 2 emissions summary by facility and renewable energy percentage>
{df_to_text(scope2_grouped_df, value_cols=["CO2e_Tonnes", "Renewable_Percentage"], decimal_places=2)}
</Scope 2 emissions summary by facility and renewable energy percentage>

<Scope 3 emissions summary by category and activity>
{df_to_text(scope3_grp_cate_activity_df, decimal_places=2)}
</Scope 3 emissions summary by category and activity>

<Scope 3 emissions summary by supplier>
{df_to_text(scope3_grp_supplier_df, decimal_places=2)}
</Scope 3 emissions summary by supplier>

Data Records:
- Scope 1: {len(self.emissions_data['scope1_df'])} entries
- Scope 2: {len(self.emissions_data['scope2_df'])} entries
- Scope 3: {len(self.emissions_data['scope3_df'])} entries
        """
        
        # Add top categories if available
        top_scope3 = self.analyzer.identify_top_emitters(3, top_n=3)
        if not top_scope3.empty:
            summary += "\n\nTop Scope 3 Categories:\n"
            for _, row in top_scope3.iterrows():
                category = row.get('Category', row.get('Activity_Description', 'Unknown'))
                emissions = row.get('CO2e_Tonnes', 0)
                summary += f"- {category}: {emissions:.2f} tCO2e\n"
        return summary
    
    def answer_question(self, question: str) -> Dict:
        """Answer natural language questions about emissions using 
        RAG techniques"""
        
        # Search relevant context from documents
        ghg_context = self.doc_processor.query_documents(
            question, 
            doc_name="ghg_protocol",
            k=3
        )
        ghg_context_txt = ""
        for i, context in enumerate(ghg_context):
            ghg_context_txt += f"{i+1}. {context['content']} \n\n"
        
        # Generate answer using LLM
        chain = self.qa_prompt | self.llm
        
        response = chain.invoke({
                'ghg_context':ghg_context_txt,
                'data_summary':self.emissions_data_summary,
                'question':question}
                )
        
        return {
            "question": question,
            "answer": response,
            "context_used": ghg_context_txt,
            "timestamp": datetime.now().isoformat()
        }
    
    def validate_scope2_emissions(self, question: str) -> Dict:
        """Validate Scope 2 emissions according to GHG Protocol"""
        if self.emissions_data is None:
            return {"error": "No emissions data loaded"}
        
        scope2_data = self.emissions_data.get('scope2_df')
        if scope2_data is None or scope2_data.empty:
            return {"error": "No Scope 2 data available"}
        
        # Perform validation
        validation_result = self.quality_assessor.assess_scope2_validity(scope2_data)
        ghg_requirements = self.doc_processor.query_documents(
            question,
            doc_name="ghg_protocol",
            k=2
        )
        ghg_requirements_txt = ""
        for i, context in enumerate(ghg_requirements):
            ghg_requirements_txt += f"{i+1}. {context['content']} \n\n"

        chain = self.validate_scope2_prompt | self.llm

        response = chain.invoke({
            'ghg_context':ghg_requirements_txt,
            'human_summary':validation_result['summary'],
            'question':question}
        )
        return {
            "question": question,
            "answer": response,
            "context_used": ghg_requirements_txt,
            "timestamp": datetime.now().isoformat()
        }
    
    def compare_with_peers(self, question: str, peer_docs: List[str]) -> Dict:
        """Summarize peer reports using LLM and compare with company's emissions data.
        Both peer report summaries and company's emissions data summary are passed into LLM
        for final output.
        
        params:
            question: str, User question
            peer_docs: List[str], List of peer report names
        """
        peer_report_summary_txt = ""
        for peer_doc in peer_docs:
            with open(f"data/processed/{peer_doc}_text.txt", "r") as f:
                peer_report = f.read()
            chain = self.peer_report_summary_prompt | self.llm
            response = chain.invoke({"peer_report_summary": peer_report})
            peer_report_summary_txt += f"<{peer_doc} summary:> \n {response.content} \n </{peer_doc} summary:> \n\n"
        
        chain = self.compare_with_peers_prompt | self.llm
        response = chain.invoke({"peer_report_summary": peer_report_summary_txt,
                                 "data_summary": self.emissions_data_summary,
                                 "question": question})
        return {
            "question": question,
            "answer": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def _setup_prompts(self):
        """Setup LLM prompts for various tasks"""
        self.qa_prompt = ChatPromptTemplate.from_template("""
        You are an expert sustainability consultant specializing in GHG emissions analysis.
        
        <Context from GHG Protocol>
        {ghg_context}
        </Context from GHG Protocol>
        
        <Emissions Data Summary>
        {data_summary}
        </Emissions Data Summary>
        
        <User Question>
        {question}
        </User Question>
        
        Please provide a detailed, accurate answer based on the GHG Protocol guidelines and the emissions data.
        If the question involves calculations, show your work step by step.
        """)

        self.validate_scope2_prompt = ChatPromptTemplate.from_template("""
        You are a sustainability regulator with expert knowledge of the GHG Protocol, specifically Scope 2 emissions.  
        Your task is to validate Scope 2 emissions data provided to you.  

        You will be given three inputs:  
        1. **Context** — information from the GHG Protocol on what constitutes valid Scope 2 emissions data.  
        2. **Human Summary** — a summary of the reported Scope 2 emissions data.  
        3. **User Question** — the specific question you need to answer.  

        ### Your responsibilities:
        - Validate the reported Scope 2 emissions data against the provided GHG Protocol context.  
        - Check whether the data and interpretation are **up to date with the latest regulations**.  
        - Clearly state:  
        1. Whether the data is valid and aligned with the GHG Protocol.  
        2. The **latest update date** of the relevant regulations.  
        3. The **next expected update date** of the regulations.

        ### Inputs:
        <GHG Protocol Context>  
        {ghg_context}  
        </GHG Protocol Context>  

        <Human Summary of Scope 2 Data>  
        {human_summary}  
        </Human Summary of Scope 2 Data>  

        <User Question>  
        {question}  
        </User Question>  

        ### Output requirements:
        Provide a **detailed and accurate response** that:  
        - Directly answers the user’s question.  
        - References the GHG Protocol guidelines where relevant.  
        - Clearly explains the reasoning behind the validation.  
        - Includes the regulatory update information (latest update date and next expected update date).                       
        """)
        
        self.report_prompt = ChatPromptTemplate.from_template("""
        Generate a professional emissions summary report based on the following data:        
                                                                      
        <Emissions Data Summary>
        {data_summary}
        </Emissions Data Summary>
        
        <User Question>
        {question}
        </User Question>
        
        Create a comprehensive report with:
        1. Executive Summary
        2. Emissions Overview
        3. Key Findings and insights
        4. Recommendations
        """)

        self.compare_with_peers_prompt = ChatPromptTemplate.from_template("""
        We want to compare our emissions data with peer companies' emissions data.
        Let's be creative, try to think out of the box. 
                                                                          
        <User Question>
        {question}
        </User Question>
                                                                          
        <Peer Report Summary>
        {peer_report_summary}
        </Peer Report Summary>
        
        <Emissions Data Summary>
        {data_summary}
        </Emissions Data Summary>
                                                                          
        Your responsibilities:
        1. Answer the user’s question directly using the provided data.  
        2. Compare our emissions data with the peer report in a meaningful way.  
        3. Provide **clear reasoning** to support your insights.  
        4. Where relevant, think creatively and suggest out-of-the-box interpretations or implications.  

        Output requirements:
        1. A **detailed, well-structured response**.  
        2. Explicit explanation of your reasoning process behind each key insight.  
        3. Balanced view: highlight both similarities and differences.  
        4. Practical implications or recommendations, if applicable.  
        """)

        self.peer_report_summary_prompt = ChatPromptTemplate.from_template("""
        You are an expert sustainability consultant specializing in GHG emissions analysis.
        Summarize peer report below. Focus on its scope 1, 2, 3 emissions and its new ideas and initiatives.
                                                                           
        <Peer Report Summary>
        {peer_report_summary}
        </Peer Report Summary>
        """)