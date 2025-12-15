# SentimentAnalysisModel - Sentiment Analysis Models

## Package Identity
SentimentAnalysisModel is a collection of sentiment analysis models for the BettaFish platform. It includes multiple approaches: BERT/GPT-2 fine-tuned models, multilingual sentiment analysis, small parameter Qwen3 fine-tuning, and traditional machine learning methods.

Primary tech/framework: Python with PyTorch for deep learning models, Transformers library for model loading, and Scikit-learn for traditional ML approaches.

## Setup & Run
```bash
# Navigate to specific model directory
cd SentimentAnalysisModel/[model_name]

# Run predictions
python predict.py --text "This product is amazing!" --lang "en"

# Train models (if needed)
python train.py
```

## Patterns & Conventions

### File Organization
- `WeiboSentiment_Finetuned/` - BERT and GPT-2 fine-tuned models
- `WeiboMultilingualSentiment/` - Multilingual sentiment analysis
- `WeiboSentiment_SmallQwen/` - Small parameter Qwen3 fine-tuning
- `WeiboSentiment_MachineLearning/` - Traditional ML approaches

### Model Implementation Pattern
✅ DO: Follow consistent model interface:
```python
# Example pattern for all sentiment models
class SentimentModel:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        """Load model and tokenizer"""
        pass
    
    def predict(self, text: str, **kwargs):
        """Predict sentiment for given text"""
        pass
    
    def predict_batch(self, texts: list, **kwargs):
        """Predict sentiment for batch of texts"""
        pass
    
    def evaluate(self, test_data: list):
        """Evaluate model performance"""
        pass
```

❌ DON'T: Implement models without consistent interface:
```python
# Avoid this pattern
def analyze_sentiment(text):
    # Direct analysis without proper model structure
    return "positive"
```

### Fine-tuning Implementation
✅ DO: Use structured fine-tuning approach:
```python
# Example from WeiboSentiment_Finetuned/BertChinese-Lora/train.py
class SentimentTrainer:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.dataset = None
    
    def prepare_data(self, data_path: str):
        """Prepare and tokenize training data"""
        # Load and preprocess data
        # Create train/val splits
        # Tokenize with proper padding
        pass
    
    def setup_model(self):
        """Setup model with LoRA adapters"""
        # Load base model
        # Configure LoRA parameters
        # Setup training arguments
        pass
    
    def train(self):
        """Execute training loop"""
        # Setup trainer
        # Train with evaluation
        # Save best model
        pass
```

### Prediction Interface
✅ DO: Provide consistent prediction interface:
```python
# Example from WeiboMultilingualSentiment/predict.py
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, required=True)
    parser.add_argument('--lang', type=str, default='zh')
    parser.add_argument('--model_path', type=str, default='models/best_model')
    
    args = parser.parse_args()
    
    # Initialize model
    model = SentimentModel(args.model_path)
    
    # Make prediction
    result = model.predict(args.text, lang=args.lang)
    
    # Print result in consistent format
    print(f"Text: {args.text}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Confidence: {result['confidence']:.4f}")
```

## Touch Points / Key Files

- BERT fine-tuning: `WeiboSentiment_Finetuned/BertChinese-Lora/` - BERT Chinese sentiment analysis
- GPT-2 fine-tuning: `WeiboSentiment_Finetuned/GPT2-Lora/` - GPT-2 sentiment generation
- Multilingual model: `WeiboMultilingualSentiment/` - Multi-language sentiment analysis
- Qwen fine-tuning: `WeiboSentiment_SmallQwen/` - Small parameter Qwen3 model
- ML approaches: `WeiboSentiment_MachineLearning/` - Traditional ML methods

## JIT Index Hints

- Find BERT models: `rg -n "class.*BERT\|BertModel" WeiboSentiment_Finetuned/BertChinese-Lora/`
- Find GPT-2 models: `rg -n "class.*GPT2\|GPT2Model" WeiboSentiment_Finetuned/GPT2-Lora/`
- Find multilingual models: `rg -n "multilingual\|translate\|lang" WeiboMultilingualSentiment/`
- Find Qwen models: `rg -n "class.*Qwen\|QwenModel" WeiboSentiment_SmallQwen/`
- Find ML models: `rg -n "SVM\|RandomForest\|LogisticRegression" WeiboSentiment_MachineLearning/`
- Find training scripts: `rg -n "def.*train\|Trainer" */train.py`
- Find prediction scripts: `rg -n "def.*predict\|main" */predict.py`

## Common Gotchas

- Model paths must be properly configured before running predictions
- Different models require different input formats (tokenized vs. raw text)
- GPU availability affects model loading and inference speed
- Multilingual models require proper language detection
- Fine-tuned models need proper tokenizer matching
- ML models require feature extraction before prediction

## Pre-PR Checks

```bash
# Test BERT model
cd WeiboSentiment_Finetuned/BertChinese-Lora && python predict.py --text "测试文本"

# Test GPT-2 model
cd WeiboSentiment_Finetuned/GPT2-Lora && python predict.py --text "测试文本"

# Test multilingual model
cd WeiboMultilingualSentiment && python predict.py --text "This is great!" --lang "en"

# Test Qwen model
cd WeiboSentiment_SmallQwen && python predict_universal.py --text "测试文本"

# Test ML models
cd WeiboSentiment_MachineLearning && python predict.py --model_type "svm" --text "测试文本"