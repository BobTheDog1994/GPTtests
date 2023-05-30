import openai
import re
from bs4 import BeautifulSoup
import requests
import PyPDF2
import textract

# Set up OpenAI API
openai.api_key = "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"

# Function to read text content from different file formats
def read_file_content(file_path):
    try:
        file_extension = file_path.split(".")[-1].lower()
        if file_extension == "txt":
            with open(file_path, 'r', encoding='utf-8') as file:
                file_contents = file.read()
                return file_contents
        elif file_extension == "html":
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                text_content = soup.get_text()
                return text_content
        elif file_extension == "pdf":
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text()
                return text_content
        elif file_extension in ["doc", "docx", "xls", "xlsx", "csv"]:
            text_content = textract.process(file_path).decode('utf-8')
            return text_content
        else:
            print("Unsupported file format.")
            return None
    except FileNotFoundError:
        return None

# Function to fetch web page content
def fetch_web_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print("Failed to fetch web page:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Error occurred while fetching web page:", e)
        return None

# Function to generate AI response
def generate_response(user_query, context):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": user_query}
        ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Main interaction loop
file_contents = ""
context = ""

while True:
    user_input = input("User: ")

    # Check if user wants to access file contents
    file_match = re.search(r'file\s+"([^"]+)"', user_input)
    if file_match:
        file_path = file_match.group(1)
        file_content = read_file_content(file_path)

        if file_content is not None:
            file_contents = file_content
            context = user_input + "\n" + file_contents
            ai_response = generate_response(user_input, context)
            print("ChatGPT:", ai_response)
        else:
            print("File not found or could not be accessed.")
    else:
        # Check if user input contains a URL
        url_match = re.search(r'(https?:\/\/\S+)', user_input)
        if url_match:
            url = url_match.group(1)
            web_page_content = fetch_web_page(url)
            if web_page_content is not None:
                context = user_input + "\n" + web_page_content
                ai_response = generate_response(user_input, context)
                print("ChatGPT:", ai_response)
        else:
            # Generate AI response for user queries
            if context:
                ai_response = generate_response(user_input, context)
            else:
                ai_response = generate_response(user_input, "")
            print("ChatGPT:", ai_response)
