import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from rag.rag import ChatPDF
from config import Config as cfg
from langchain_core.messages import HumanMessage, AIMessage



class TestRephraseQuestionDomain(unittest.TestCase):
    def setUp(self):
        cfg.MODEL_TEMPERATURE = 0.0
        self.domain = "Sport"
        chat_pdf = ChatPDF(cfg)
        self.kbs = chat_pdf.knowledge_base_system
        self.kbs.chat_history.extend([HumanMessage(content="What is the difference between a winning and a losing team?"), AIMessage(content="According to Ene et al.'s research (2018) published in the International Journal of Performance Analysis in Sport, the difference between a winning and a losing team lies in insights from Euroleague basketball.")])
    
    
    def test_positive_rephrased_quesiton_domain(self):
        question = "What are the key factors?"
        inputs = {"question": question, "execution_path": []}
        expected_classification = 'yes'
        
        state = self.kbs._rephrase_query(inputs)
        inputs = {"question": state['question'], "domain": self.domain, "execution_path": []}
        state = self.kbs._check_query_domain(inputs)
        print(f"State: {state}")
        self.assertEqual(state['generation_score'], expected_classification)
    
        
    def test_negative_rephrased_quesiton(self):
        question = "How is the weather today?"
        inputs = {"question": question, "execution_path": []}
        expected_classification = 'no'
        
        state = self.kbs._rephrase_query(inputs)
        inputs = {"question": state['question'], "domain": self.domain, "execution_path": []}
        state = self.kbs._check_query_domain(inputs)
        print(f"State: {state}")
        self.assertEqual(state['generation_score'], expected_classification)
            
        
    def tearDown(self) -> None:
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()