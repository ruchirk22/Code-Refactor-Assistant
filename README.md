# COBOL-to-Java Code Refactor Assistant

A web-based AI assistant that translates COBOL code snippets to equivalent Java code using transformer models from Hugging Face.

## Features

- **Code Translation**: Convert COBOL code to Java
- **Explanatory Comments**: Add comprehensive documentation to the translated code
- **Optimization Tips**: Suggest modernization and performance improvements
- **Rule-based Fallback**: Simple translation even when AI model is unavailable
- **Download Option**: Save translated code directly

## Technology Stack

- **Frontend**: Streamlit (fast development, easy deployment)
- **Backend/Translation Engine**: Python + Hugging Face Transformers
- **Models**: CodeT5 (free to use, no API key required)
- **Storage**: Session-based (no database required)

## How It Works

1. The application uses CodeT5, a pre-trained transformer model specialized for code-related tasks
2. COBOL code is submitted as a prompt to the model
3. The model generates equivalent Java code
4. Additional prompts are used to add comments and optimization suggestions
5. A rule-based fallback system provides basic translation when the AI model is unavailable

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cobol-to-java-refactor.git
   cd cobol-to-java-refactor
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

4. Open your browser and navigate to `http://localhost:8501`

## Deployment Options

- **Local**: Run on your local machine
- **Hugging Face Spaces**: Deploy for free on Hugging Face (fully free)
- **Streamlit Community Cloud**: Free hosting for Streamlit apps
- **Heroku/Railway**: Deploy with free tiers (limited usage)

## Limitations

- The translation quality depends on the model's training
- Complex COBOL structures may require manual adjustments
- First-time loading might be slow as the model is downloaded

## Future Enhancements

- Support for translating entire COBOL programs with multiple divisions
- Fine-tuning on a dedicated COBOL-to-Java dataset
- Translation history tracking
- Export options for multiple files