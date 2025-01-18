import pdfplumber
import re
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI, OpenAIError
import APIKeys

# Initialize OpenAI
client = OpenAI(api_key=APIKeys.OPENAI)

##########################################################
# Functions

### Defining functions
# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "".join(page.extract_text() for page in pdf.pages)
    return text

# Extract financial data using regex and pandas
def extract_financial_data(text):
    patterns = {
        "Service Revenue": r"Service revenue\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        "Sales Revenue": r"Sales revenue\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        "Net Income": r"Net income\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        "Operating Expenses": r"Total\s*operating\s*expenses\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        "Total Assets": r"Total\s*assets\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        "Current Assets": r"Total current assets\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        "Liabilities": r"Total Current Liabilities\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        "Retained Earnings": r"Retained earnings\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
    }

    financial_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            value = float(match.group(1).replace(",", ""))
            financial_data[key] = value
        else:
            financial_data[key] = None

    return pd.DataFrame([financial_data])

# Analyze with OpenAI
def analyze_with_openai(financial_data_df):
    formatted_data = financial_data_df.to_string(index=False)
    prompt = f"""
    Imagine you are a professional in finance. Analyze the following financial data, 
    calculate simple key ratios (don't show calculations, just raw results) such as 
    Net Income Ratio, Asset-to-Liability Ratio, and Current Ratio. Also,
    provide a brief summary highlighting strengths, risks, and insights:

    {formatted_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a finance professional."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        return f"Error interacting with OpenAI API: {e}"

# Plot financial data
def plot_financial_data(financial_data_df, plot_file):
    financial_data_dict = financial_data_df.iloc[0].dropna().to_dict()  # Convert first row to dictionary
    labels = list(financial_data_dict.keys())
    values = list(financial_data_dict.values())

    # Create bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color='skyblue')

    # Add exact values as labels on top of the bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f"${yval:,.2f}", ha='center', va='bottom')

    plt.title("Financial Data Overview")
    plt.ylabel("Amount (USD)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()

def generate_html_snippet(analysis, plot_file, financial_data_df):
    """
    Returns an HTML string containing the analysis text and
    an <img> tag to display the financial data plot.
    Wrapped in a <div></div> so you can embed it elsewhere.
    """
    # You can parse the analysis if you want to separate strengths, risks, insights, etc.
    # Example: (very simplistic approach, adapt to your actual analysis format)
    strengths_text, risks_text, insights_text = "", "", ""
    if "Strengths:" in analysis and "Risks:" in analysis and "Insights:" in analysis:
        strengths_text = analysis.split("Strengths:")[1].split("Risks:")[0].strip()
        risks_text = analysis.split("Risks:")[1].split("Insights:")[0].strip()
        insights_text = analysis.split("Insights:")[1].strip()
    else:
        # If the analysis doesn't contain those exact words,
        # fallback to the entire text
        strengths_text = analysis

    # Convert DataFrame to HTML table (basic example)
    financial_table_html = financial_data_df.to_html(index=False)

    # Build HTML snippet
    html_snippet = f"""
    <div style="margin: 20px;">
      <h2>Financial Data Plot</h2>
      <img src="{plot_file}" alt="Financial Data Plot" style="max-width: 80%; height: auto;" />
      
      <h2>Analysis and Key Ratios</h2>
      <h3>Strengths</h3>
      <p>{strengths_text}</p>
      <h3>Risks</h3>
      <p>{risks_text}</p>
      <h3>Insights</h3>
      <p>{insights_text}</p>
      
      <h2>Financial Data</h2>
      {financial_table_html}
    </div>
    """.strip()

    return html_snippet


##########################################################
# Main script

def main():
    pdf_path = "Sample_Financial_Statements.pdf"
    plot_file = "financial_plot.png"

    # Step 1: Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Step 2: Extract financial data
    financial_data_df = extract_financial_data(text)
    print("Financial Data:")
    print(financial_data_df)

    # Step 3: Analyze with OpenAI
    print("\nAnalysis from OpenAI:")
    analysis = analyze_with_openai(financial_data_df)
    print(analysis)

    # Step 4: Plot the financial data
    plot_financial_data(financial_data_df, plot_file)

    # Step 5: Generate an HTML snippet (instead of LaTeX)
    html_snippet = generate_html_snippet(analysis, plot_file, financial_data_df)

    # For demonstration, just print the HTML to console;
    # in practice, you might return it from a function or write it to a file
    print("\nHTML Snippet:\n")
    return html_snippet
