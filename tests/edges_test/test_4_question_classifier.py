import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..',"..")))
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import unittest
import inspect

from rag.rag import ChatPDF
from config import Config as cfg


class TestQuestionClassifier(unittest.TestCase):
    def setUp(self):
        cfg.MODEL_TEMPERATURE = 0.0
        self.domain = "Sport"
        chat_pdf = ChatPDF()
        self.kbs = chat_pdf.knowledge_base_system
    
    
    def test_positive_question_classifier(self):    
        question = "Using a predictive model with an accuracy rate of 84%, how many games would you expect to correctly predict out of a total of 500 NBA games?"
        inputs = {"question": question}
        expected_classification = 'yes'
        
        state = self.kbs._question_classifier(inputs)
        
        print(f"\n{self.__class__.__name__}:       {inspect.currentframe().f_code.co_name}")
        print(f"\nQuestion_classifier -> State:      {state}")
        
        self.assertEqual(state['question_type'], expected_classification)
        
        
    def test_negative__question_classifier(self):
        question = "How has AI technology impacted the strategies employed by basketball coaches?"
        inputs = {"question": question}
        expected_classification = 'no'
        
        state = self.kbs._question_classifier(inputs)
        
        print(f"\n{self.__class__.__name__}:       {inspect.currentframe().f_code.co_name}")
        print(f"\nQuestion_classifier -> State:      {state}")
        
        self.assertEqual(state['question'], question)
        self.assertEqual(state['question_type'], expected_classification)
        
        
    def tearDown(self) -> None:
        self.kbs = None
        self.domain = None
        self.chat_pdf = None
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()