import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from rag.rag import ChatPDF
from config import Config as cfg



class TestDomainCheck(unittest.TestCase):
    def setUp(self):
        cfg.MODEL_TEMPERATURE = 0.0
        self.domain = "Sport"
        chat_pdf = ChatPDF(cfg)
        self.kbs = chat_pdf.knowledge_base_system
    
    def test_positive_classification(self):
        question = "How can AI improve basketball training?"
        inputs = {"question": question, "domain": self.domain, "execution_path": []}
        expected_classification = 'yes'
        
        state = self.kbs._check_query_domain(inputs)
        print(f"State: {state}")
        self.assertEqual(state['question'], question)
        self.assertEqual(state['generation_score'], expected_classification)
        
        
    def test_negative_classification(self):
        question = "How is the weather today?"
        inputs = {"question": question, "domain": self.domain, "execution_path": []}
        expected_classification = 'no'
        
        state = self.kbs._check_query_domain(inputs)
        print(f"State: {state}")
        self.assertEqual(state['question'], question)
        self.assertEqual(state['generation_score'], expected_classification)
        
        
    def tearDown(self) -> None:
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()