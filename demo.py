import sys
import os
import pprint
sys.path.append('..')

from src.agent import EmissionsInsightsAgent
from src.data_loader import EmissionsDataLoader
from src.emissions_analyzer import EmissionsAnalyzer
import pandas as pd
# import plotly.graph_objects as go
print("Python executable:", sys.executable)
print("Python version:", sys.version)

agent = EmissionsInsightsAgent(model_version="gemini-2.5-flash")

agent.initialize(data_path='data/raw')
print("Agent initialized successfully!")

# Q1
question1 = """Should employee business travel be classified as Scope 1 or Scope 3? 
Explain the reasoning and describe how I can calculate my business travel emissions?"""
response1 = agent.answer_question(question1)
# print("Question1:", response1['question'])
# print()
# print("Answer:", response1['answer'].content)
# print()
# print("Context used:")
# print(response1['context_used'])
# print("\n\n")
# Write the output for question 1 to a file in demo_outputs/answer1
with open("demo_outputs/answer1.txt", "w", encoding="utf-8") as f:
    f.write(f"""
    Question1: {response1['question']} \n
    Answer: \n
    {response1['answer'].content} 
    Context used: \n
    {response1['context_used']}
    """)

# Q2
question2 = "Are my scope 2 emissions calculation valid according to the Greenhouse Gas Protocol?"
response2 = agent.validate_scope2_emissions(question2)
# print("Question2:",  response2['question'])
# print()
# print("Answer:", response2['answer'].content)
# print()
# print("Context used:")
# print(response2['context_used'])
# print("\n\n")
with open("demo_outputs/answer2.txt", "w", encoding="utf-8") as f:
    f.write(f"""
    Question2: {response2['question']} \n
    Answer: \n
    {response2['answer'].content} 
    Context used: \n
    {response2['context_used']}
    """)

# Q3
question3 = """How do my scope 1 & 2 emissions compare with other companies in my industry, 
and what insights can I derive from this comparison?"""
response3 = agent.compare_with_peers(question3, peer_docs=['peer1', 'peer2'])
with open("demo_outputs/answer3.txt", "w", encoding="utf-8") as f:
    f.write(f"""
    Question3: {response3['question']} \n
    Answer: \n
    {response3['answer'].content}
    """)

# Q4
question4 = "What is our highest emitting Scope 3 category and what specific activities contribute to it?"
response4 = agent.answer_question(question4)
# print("Question4:", response4['question'])
# print()
# print("Answer:", response4['answer'].content)
# print()
# print("Context used:")
# print(response4['context_used'])
# print("\n\n")
with open("demo_outputs/answer4.txt", "w", encoding="utf-8") as f:
    f.write(f"""
    Question4: {response4['question']} \n
    Answer: \n
    {response4['answer'].content} 
    Context used: \n
    {response4['context_used']}
    """)

# Q5
question5 = "Which suppliers should I prioritise to engage for emissions reduction efforts?"
response5 = agent.answer_question(question5)
# print("Question5:", response5['question'])
# print()
# print("Answer:", response5['answer'].content)
# print()
# print("Context used:")
# print(response5['context_used'])
# print("\n\n")
with open("demo_outputs/answer5.txt", "w", encoding="utf-8") as f:
    f.write(f"""
    Question5: {response5['question']} \n
    Answer: \n
    {response5['answer'].content} 
    Context used: \n
    {response5['context_used']}
    """)

# Q6
question6 = "Generate a summary report of our total emissions by scope with key insights"
response6 = agent.answer_question(question6)
# print("Question:", response6['question'])
# print()
# print("Answer:", response6['answer'].content)
# print()
# print("Context used:")
# print(response6['context_used']
with open("demo_outputs/answer6.txt", "w", encoding="utf-8") as f:
    f.write(f"""
    Question6: {response6['question']} \n
    Answer: \n
    {response6['answer'].content} 
    Context used: \n
    {response6['context_used']}
    """)