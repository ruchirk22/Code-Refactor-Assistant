# Architecture: COBOL-to-Java Code Refactor Assistant

## System Architecture

```
┌───────────────────┐     ┌────────────────────────┐     ┌───────────────────┐
│                   │     │                        │     │                   │
│  Streamlit UI     │────▶│  Transformer Pipeline  │────▶│  Output Display   │
│                   │     │                        │     │                   │
└───────────────────┘     └────────────────────────┘     └───────────────────┘
         │                            │                            │
         │                            │                            │
         ▼                            ▼                            ▼
┌───────────────────┐     ┌────────────────────────┐     ┌───────────────────┐
│                   │     │                        │     │                   │
│  COBOL Input      │     │  Hugging Face Models   │     │  Java Output      │
│                   │     │                        │     │                   │
└───────────────────┘     └────────────────────────┘     └───────────────────┘
                                      │
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │                        │
                          │  Rule-based Fallback   │
                          │                        │
                          └────────────────────────┘
```

## Component Breakdown

### 1. User Interface (Streamlit)
- **Input Area**: Text field for COBOL code input
- **Control Panel**: Options for comments and optimization
- **Output Display**: Syntax-highlighted Java code display
- **Example Section**: Sample COBOL code for testing

### 2. Translation Engine
- **Primary Translator**: Hugging Face's CodeT5 model
- **Prompt Engineering**: Specialized prompts for different tasks
- **Fallback System**: Rule-based translation for basic COBOL constructs

### 3. Post-Processing
- **Code Commenting**: AI-generated explanatory comments
- **Optimization Suggestions**: AI-recommended improvements
- **Format Cleaning**: Extraction of clean Java code from model output

## Data Flow

1. **Input Collection**
   - User enters COBOL code in the text area
   - Input is validated for basic COBOL structure

2. **Translation Process**
   - COBOL code is formatted into a prompt
   - Prompt is sent to the transformer model
   - Model generates initial Java translation

3. **Enhancement Steps**
   - If requested, additional prompts generate comments
   - If requested, optimization suggestions are generated
   - Output is extracted and cleaned

4. **Presentation**
   - Translated Java code is displayed with syntax highlighting
   - Optimization tips are presented in an organized format
   - Download option is provided for the generated code

## Technical Design Decisions

### Model Selection
- **CodeT5** was chosen because:
  - It's specialized for code translation tasks
  - Completely free to use with Hugging Face
  - No API key or authentication required
  - Decent performance for small code snippets

### Fallback Mechanism
- Rule-based translation provides basic functionality when:
  - The model fails to load or generate
  - Network connectivity issues occur
  - Translation requires less computational resources

### Performance Considerations
- Model is cached to prevent repeated loading
- Translation is performed on-demand to save resources
- Streamlit's session state preserves context between interactions

## Security Considerations

- No external API keys or credentials required
- All processing happens locally in the user's session
- No data is stored or transmitted to external services
- Code generation is sandboxed within the application

## Deployment Architecture

The application is designed to be easily deployable on free platforms:

- **Hugging Face Spaces**: Free hosting with GPU support
- **Streamlit Community Cloud**: Free tier available
- **Local Deployment**: Run on any machine with Python

The architecture ensures zero-cost operation while delivering functional translation capabilities for demonstration purposes.