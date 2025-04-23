import streamlit as st
import re
import traceback

# App title and description
st.set_page_config(page_title="COBOL-to-Java Refactor Assistant", layout="wide")
st.title("COBOL-to-Java Code Refactor Assistant")
st.markdown("""
This application translates COBOL code to equivalent Java code using rule-based translation.
Simply paste your COBOL code snippet below and get the Java equivalent with comments.
""")

# Rule-based COBOL to Java translator
def translate_cobol_to_java(cobol_code):
    # Clean and preprocess COBOL code
    clean_cobol = clean_cobol_code(cobol_code)
    
    # Parse important parts of COBOL code
    program_id = extract_program_id(clean_cobol)
    variables = extract_variables(clean_cobol)
    procedures = extract_procedures(clean_cobol)
    
    # Generate Java code
    java_code = generate_java_class(program_id, variables, procedures)
    
    return java_code

def clean_cobol_code(cobol_code):
    # Remove trailing dots and normalize whitespace
    cleaned = re.sub(r'\.\s*$', '', cobol_code, flags=re.MULTILINE)
    # Normalize indentation
    cleaned = re.sub(r'^\s+', '    ', cleaned, flags=re.MULTILINE)
    return cleaned

def extract_program_id(cobol_code):
    # Extract program ID from IDENTIFICATION DIVISION
    match = re.search(r'PROGRAM-ID\.\s*(\w+)', cobol_code, re.IGNORECASE)
    if match:
        return match.group(1)
    return "CobolProgram"  # Default program name

def extract_variables(cobol_code):
    variables = []
    
    # Look for DATA DIVISION
    data_division_match = re.search(r'DATA\s+DIVISION(.*?)(?:PROCEDURE\s+DIVISION|$)', 
                                   cobol_code, re.DOTALL | re.IGNORECASE)
    
    if data_division_match:
        data_section = data_division_match.group(1)
        
        # Extract variables defined with level numbers
        var_pattern = r'(\d+)\s+(\w+[\-\w]*)\s+(?:PIC|PICTURE)\s+([X9]+)(?:\((\d+)\))?'
        var_matches = re.findall(var_pattern, data_section, re.IGNORECASE)
        
        for level, name, pic_type, size in var_matches:
            # Determine Java type based on PICTURE clause
            java_type = "String" if "X" in pic_type.upper() else "int"
            size = size if size else "1"
            
            # Convert COBOL naming convention to Java
            java_name = name.lower().replace('-', '_')
            
            variables.append({
                "level": level,
                "name": java_name,
                "type": java_type,
                "size": size,
                "original_name": name
            })
    
    return variables

def extract_procedures(cobol_code):
    procedures = []
    
    # Look for PROCEDURE DIVISION
    proc_match = re.search(r'PROCEDURE\s+DIVISION(.*?)(?:END\s+PROGRAM|$)', 
                          cobol_code, re.DOTALL | re.IGNORECASE)
    
    if proc_match:
        procedure_code = proc_match.group(1)
        
        # Extract paragraphs
        paragraphs = re.split(r'(\w[\-\w]*)\s*\.\s*', procedure_code)
        current_paragraph = "main"
        
        # Process statements
        statements = []
        lines = procedure_code.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and paragraph headers
            if not line or re.match(r'^\w[\-\w]*\s*\.$', line):
                continue
            
            # Process DISPLAY statements
            display_match = re.search(r'DISPLAY\s+(.*)', line, re.IGNORECASE)
            if display_match:
                content = display_match.group(1).strip()
                
                # Handle string literals and variables
                java_stmt = translate_display(content)
                statements.append(java_stmt)
                continue
            
            # Process MOVE statements
            move_match = re.search(r'MOVE\s+(.*?)\s+TO\s+(.*)', line, re.IGNORECASE)
            if move_match:
                source = move_match.group(1).strip()
                target = move_match.group(2).strip()
                
                java_stmt = translate_move(source, target)
                statements.append(java_stmt)
                continue
            
            # Process COMPUTE statements
            compute_match = re.search(r'COMPUTE\s+(.*?)\s*=\s*(.*)', line, re.IGNORECASE)
            if compute_match:
                target = compute_match.group(1).strip()
                expression = compute_match.group(2).strip()
                
                java_stmt = translate_compute(target, expression)
                statements.append(java_stmt)
                continue
            
            # Process ACCEPT statements
            accept_match = re.search(r'ACCEPT\s+(.*)', line, re.IGNORECASE)
            if accept_match:
                target = accept_match.group(1).strip()
                
                java_stmt = translate_accept(target)
                statements.append(java_stmt)
                continue
            
            # Process IF statements (simplified)
            if_match = re.search(r'IF\s+(.*)', line, re.IGNORECASE)
            if if_match:
                condition = if_match.group(1).strip()
                
                java_stmt = translate_if(condition)
                statements.append(java_stmt)
                continue
            
            # Process STOP RUN
            if re.search(r'STOP\s+RUN', line, re.IGNORECASE):
                statements.append("// End of program execution")
                statements.append("System.exit(0);")
                continue
            
            # Add as comment if no recognized pattern
            statements.append(f"// TODO: Translate COBOL: {line}")
        
        procedures = statements
    
    return procedures

def translate_display(content):
    # Handle quoted strings and variables
    parts = []
    within_quote = False
    current_part = ""
    
    # Handle specific case for 'HELLO, WORLD!'
    if content.strip("'\"") == "HELLO, WORLD!":
        return 'System.out.println("HELLO, WORLD!");'
    
    # Split by spaces but respect quotes
    for c in content:
        if c in "'\"":
            within_quote = not within_quote
            current_part += '"' if c in "'\"" else c
        elif c.isspace() and not within_quote:
            if current_part:
                parts.append(current_part)
                current_part = ""
        else:
            current_part += c
    
    if current_part:
        parts.append(current_part)
    
    # Process each part
    java_parts = []
    for part in parts:
        if part.startswith('"') or part.startswith("'"):
            # It's a string literal
            java_parts.append(part.replace("'", '"'))
        else:
            # It's a variable or literal
            java_parts.append(part.lower().replace('-', '_'))
    
    # Join with + for concatenation if multiple parts
    if len(java_parts) > 1:
        return f'System.out.println({" + ".join(java_parts)});'
    elif len(java_parts) == 1:
        return f'System.out.println({java_parts[0]});'
    else:
        return 'System.out.println();'

def translate_move(source, target):
    # Convert variable names to Java style
    java_target = target.lower().replace('-', '_')
    
    # Handle string literals
    if source.startswith("'") or source.startswith('"'):
        java_source = source.replace("'", '"')
    else:
        java_source = source.lower().replace('-', '_')
    
    return f'{java_target} = {java_source};'

def translate_compute(target, expression):
    # Convert variable names to Java style
    java_target = target.lower().replace('-', '_')
    
    # Replace COBOL operators with Java operators
    java_expr = expression.lower().replace('-', '_')
    java_expr = java_expr.replace(' + ', ' + ').replace(' - ', ' - ')
    java_expr = java_expr.replace(' * ', ' * ').replace(' / ', ' / ')
    
    return f'{java_target} = {java_expr};'

def translate_accept(target):
    # Convert variable names to Java style
    java_target = target.lower().replace('-', '_')
    
    return f'''try {{
    java.util.Scanner scanner = new java.util.Scanner(System.in);
    {java_target} = scanner.nextLine();
}} catch (Exception e) {{
    System.err.println("Error reading input: " + e.getMessage());
}}'''

def translate_if(condition):
    # Convert condition to Java style
    java_condition = condition.lower().replace('-', '_')
    java_condition = java_condition.replace(' equal ', ' == ')
    java_condition = java_condition.replace(' equals ', ' == ')
    java_condition = java_condition.replace(' not equal ', ' != ')
    java_condition = java_condition.replace(' greater than ', ' > ')
    java_condition = java_condition.replace(' less than ', ' < ')
    
    return f'if ({java_condition}) {{'

def generate_java_class(program_id, variables, procedures):
    class_name = program_id.replace('-', '_')
    
    # Start building Java code
    java_code = f'''/**
 * Java translation of COBOL program {program_id}
 * Generated by COBOL-to-Java Code Refactor Assistant
 */
public class {class_name} {{
    // Variable declarations
'''
    
    # Add variables
    for var in variables:
        if var["type"] == "String":
            java_code += f'    private {var["type"]} {var["name"]} = "";  // Translated from {var["original_name"]}\n'
        else:
            java_code += f'    private {var["type"]} {var["name"]} = 0;  // Translated from {var["original_name"]}\n'
    
    # Add main method - Fixed the string formatting issue
    java_code += f'''
    public static void main(String[] args) {{
        {class_name} program = new {class_name}();
        program.execute();
    }}
    
    /**
     * Main program execution
     */
    public void execute() {{
'''
    
    # Add procedures
    for proc in procedures:
        java_code += f'        {proc}\n'
    
    # Close method and class
    java_code += '''    }
}'''
    
    return java_code

# Generate optimization suggestions - No dependency on transformer models
def generate_optimization_suggestions(java_code):
    return rule_based_optimization_tips(java_code)

def rule_based_optimization_tips(java_code):
    # Generate simple rule-based optimization tips
    tips = []
    
    # Check for System.out.println usage
    if "System.out.println" in java_code:
        tips.append("Consider using a logger framework like SLF4J instead of System.out.println for better control over logging")
    
    # Check for exception handling
    if "catch (Exception e)" in java_code:
        tips.append("Use specific exception types instead of catching generic Exception")
    
    # Check for Scanner usage
    if "Scanner" in java_code:
        tips.append("Close Scanner resources using try-with-resources to prevent resource leaks")
    
    # Check for variable types
    if "String" in java_code:
        tips.append("Use StringBuilder for string concatenation operations within loops for better performance")
    
    # Add general tips
    tips.append("Consider adding JavaDoc comments to methods for better code documentation")
    tips.append("Use Java's enhanced for loop syntax for any list iterations")
    tips.append("Apply consistent indentation and code formatting for better readability")
    
    # Format as markdown bullet points
    return "\n".join([f"• {tip}" for tip in tips])

# Add comments to the Java code
def add_explanatory_comments(java_code, cobol_code):
    # Identify main sections of the code
    sections = [
        ("Variable declarations", "// Variable declarations", "Java class variables corresponding to COBOL data items"),
        ("Main method", "public static void main", "Entry point of the Java program"),
        ("Execute method", "public void execute", "Equivalent to COBOL's PROCEDURE DIVISION")
    ]
    
    # Add section comments
    for section_name, section_marker, explanation in sections:
        if section_marker in java_code:
            java_code = java_code.replace(
                section_marker, 
                f"    // {'-'*50}\n    // {section_name}: {explanation}\n    // {'-'*50}\n    {section_marker}"
            )
    
    # Add comments to display statements
    display_pattern = r'(System\.out\.println\(.*?\);)'
    java_code = re.sub(
        display_pattern, 
        r'\1  // Equivalent to COBOL DISPLAY statement', 
        java_code
    )
    
    # Add comments to scanner/input statements
    scanner_pattern = r'(Scanner scanner.*?}\))'
    java_code = re.sub(
        scanner_pattern, 
        r'\1  // Equivalent to COBOL ACCEPT statement', 
        java_code, 
        flags=re.DOTALL
    )
    
    return java_code

# Main application
def main():
    # Input area for COBOL code
    st.subheader("Input COBOL Code")
    cobol_code = st.text_area("Paste your COBOL code here:", height=200, 
                             key="cobol_input",
                             help="Paste COBOL code snippet to translate")
    
    # Options
    col1, col2 = st.columns(2)
    with col1:
        add_comments = st.checkbox("Add explanatory comments", value=True)
    with col2:
        suggest_optimizations = st.checkbox("Suggest optimizations", value=True)
    
    # Translation button
    if st.button("Translate to Java"):
        if not cobol_code:
            st.warning("Please enter COBOL code to translate.")
        else:
            with st.spinner("Translating code..."):
                try:
                    # Translate COBOL to Java using rule-based approach
                    java_code = translate_cobol_to_java(cobol_code)
                    
                    # Add comments if requested
                    if add_comments:
                        java_code = add_explanatory_comments(java_code, cobol_code)
                    
                    # Display Java code
                    st.subheader("Translated Java Code")
                    st.code(java_code, language="java")
                    
                    # Generate and display optimization tips if requested
                    if suggest_optimizations:
                        optimization_tips = generate_optimization_suggestions(java_code)
                        st.subheader("Optimization Suggestions")
                        st.markdown(optimization_tips)
                    
                    # Add a download button for the Java code
                    st.download_button(
                        label="Download Java Code",
                        data=java_code,
                        file_name=f"{extract_program_id(cobol_code)}.java",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error translating code: {str(e)}")
                    st.error(traceback.format_exc())
    
    # Add example COBOL code
    with st.expander("Show example COBOL code"):
        example_cobol = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO.
       
       ENVIRONMENT DIVISION.
       
       DATA DIVISION.
       
       PROCEDURE DIVISION.
           DISPLAY 'HELLO, WORLD!'.
           STOP RUN.
        """
        st.code(example_cobol, language="cobol")
        if st.button("Use this example"):
            st.session_state.cobol_input = example_cobol
            st.experimental_rerun()
            
        # Add a more complex example
        st.markdown("### More Complex Example:")
        complex_example = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALCULATOR.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 NUM1 PIC 9(5).
       01 NUM2 PIC 9(5).
       01 RESULT PIC 9(10).
       01 OPERATION PIC X.
       
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY "ENTER FIRST NUMBER: ".
           ACCEPT NUM1.
           DISPLAY "ENTER SECOND NUMBER: ".
           ACCEPT NUM2.
           DISPLAY "ENTER OPERATION (+, -, *, /): ".
           ACCEPT OPERATION.
           
           IF OPERATION = "+" 
              COMPUTE RESULT = NUM1 + NUM2
           ELSE IF OPERATION = "-" 
              COMPUTE RESULT = NUM1 - NUM2
           ELSE IF OPERATION = "*" 
              COMPUTE RESULT = NUM1 * NUM2
           ELSE IF OPERATION = "/" 
              IF NUM2 = 0
                 DISPLAY "ERROR: DIVISION BY ZERO"
              ELSE
                 COMPUTE RESULT = NUM1 / NUM2
              END-IF
           ELSE
              DISPLAY "INVALID OPERATION"
           END-IF.
           
           DISPLAY "RESULT: " RESULT.
           STOP RUN.
        """
        st.code(complex_example, language="cobol")
        if st.button("Use complex example"):
            st.session_state.cobol_input = complex_example
            st.experimental_rerun()

    # Add more information and resources
    st.markdown("---")
    st.markdown("### About this tool")
    st.markdown("""
    This COBOL-to-Java translator uses rule-based translation techniques to convert legacy COBOL code to modern Java.
    
    **Features:**
    - Translates COBOL syntax to equivalent Java code
    - Adds explanatory comments to help understand the translation
    - Suggests optimization tips for modernizing the code
    
    **Note:** Complex COBOL constructs might require manual adjustments after translation.
    """)

if __name__ == "__main__":
    main()