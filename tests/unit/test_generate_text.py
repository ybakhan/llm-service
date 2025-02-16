import unittest
from unittest.mock import Mock, patch
from generate import generate_text
import torch

class TestGenerateText(unittest.TestCase):

    def setUp(self):
        self.tokenizer = Mock()
        self.model = Mock()
        self.device = torch.device("cpu")

        # Mock `.to(device)` to return the tensor itself
        def mock_to_device(tensor, _=None, **kwargs):
            return tensor  # Simply return the tensor unchanged
        self.mock_tensor = lambda _: Mock(spec=torch.Tensor, to=Mock(side_effect=mock_to_device))

        self.model.generate.reset_mock()
        self.tokenizer.reset_mock()

    def test_generate_text_with_valid_input(self):
        prompt = "test prompt"
        expectedGeneration = "test generation"
        
        self.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]], device=self.device),
            'attention_mask': torch.tensor([[1, 1, 1]], device=self.device)
        }

        self.model.generate.return_value = torch.tensor([[4, 5, 6]], device=self.device)
        self.tokenizer.decode.return_value = expectedGeneration
        
        result = generate_text(prompt, self.tokenizer, self.model, self.device)
        self.assertEqual(result, expectedGeneration)
        self.tokenizer.assert_called_once_with(prompt, return_tensors="pt", padding=False, truncation=True, max_length=512)
        self.model.generate.assert_called_once()

    def test_generate_text_with_empty_prompt(self):
        self.tokenizer.return_value = {
            'input_ids': torch.tensor([[]], device=self.device), 
            'attention_mask': torch.tensor([[]], device=self.device)
        }
        self.model.generate.return_value = torch.tensor([[]], device=self.device)
        self.tokenizer.decode.return_value = ""

        result = generate_text("", self.tokenizer, self.model, self.device)
        
        self.assertEqual(result, "")

    def test_generate_text_raises_runtime_error(self):
        self.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]], device=self.device), 
            'attention_mask': torch.tensor([[1, 1, 1]], device=self.device)
        }
        self.model.generate.side_effect = RuntimeError("Model generation error")

        with self.assertRaises(RuntimeError):
            generate_text("prompt", self.tokenizer, self.model, self.device)

    @patch('torch.no_grad')
    def test_context_manager_for_no_grad(self, mock_no_grad):
        self.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]], device=self.device), 
            'attention_mask': torch.tensor([[1, 1, 1]], device=self.device)
        }
        self.model.generate.return_value = torch.tensor([[4, 5, 6]], device=self.device)
        
        generate_text("test", self.tokenizer, self.model, self.device)
        mock_no_grad.assert_called_once()

if __name__ == '__main__':
    unittest.main()