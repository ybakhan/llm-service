import unittest
from unittest.mock import Mock, patch
from generate import generate_text
import torch

class TestGenerateText(unittest.TestCase):

    def setUp(self):
        self.tokenizer = Mock()
        self.model = Mock()
        self.model.generate.reset_mock()
        self.tokenizer.reset_mock()

    def test_generate_text_with_valid_input(self):
        prompt = "test prompt"
        expectedGeneration = "test generation"
        
        self.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]), 
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        self.model.generate.return_value = torch.tensor([[4, 5, 6]])
        self.tokenizer.decode.return_value = expectedGeneration

        result = generate_text(prompt, self.tokenizer, self.model)
        
        self.assertEqual(result, expectedGeneration)
        self.tokenizer.assert_called_once_with(prompt, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
        self.model.generate.assert_called_once()

    def test_generate_text_with_empty_prompt(self):
        self.tokenizer.return_value = {
            'input_ids': torch.tensor([[]]), 
            'attention_mask': torch.tensor([[]])
        }
        self.model.generate.return_value = torch.tensor([[]])
        self.tokenizer.decode.return_value = ""

        result = generate_text("", self.tokenizer, self.model)
        
        self.assertEqual(result, "")

    def test_generate_text_raises_runtime_error(self):
        self.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]), 
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        self.model.generate.side_effect = RuntimeError("Model generation error")

        with self.assertRaises(RuntimeError):
            generate_text("prompt", self.tokenizer, self.model)

    @patch('torch.no_grad')
    def test_context_manager_for_no_grad(self, mock_no_grad):
        self.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]), 
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        self.model.generate.return_value = torch.tensor([[4, 5, 6]])
        
        generate_text("test", self.tokenizer, self.model)
        mock_no_grad.assert_called_once()

if __name__ == '__main__':
    unittest.main()