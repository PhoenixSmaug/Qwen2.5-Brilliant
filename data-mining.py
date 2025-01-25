import os
import pandas as pd
import csv
from bs4 import BeautifulSoup
import concurrent.futures

# Maximum CSV entry length
MAX_ENTRY_LENGTH = 32000

def process_folder(folder, root_dir):
    data = []
    folder_path = os.path.join(root_dir, folder)
    
    if os.path.isdir(folder_path):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            
            if file.endswith(".html"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    soup = BeautifulSoup(content, 'html.parser')

                    # skip problems which rely on images
                    if 'brioche/upload' in content:
                        continue

                    script_block = soup.find('script', id='ir_template_holder')
                    if script_block:
                        data_has_multiple_options = script_block.get('data-has-multiple-options', 'false')

                        # skip multiple choice problems
                        if data_has_multiple_options.lower() == 'true':
                            continue

                        # extract the answer from data-answers-list
                        data_answers_list = script_block.get('data-answers-list', None)
                        if data_answers_list:
                            answer = data_answers_list.strip()

                            # extract the question
                            question_section = soup.find('div', class_='question-text latex')

                            # Find the reason section (second div with class 'text')
                            text_divs = soup.find_all('div', class_='text')
                            reason = text_divs[1].get_text(strip=True) if len(text_divs) > 1 else ""

                            if question_section:
                                # Extract and clean the question text
                                question_paragraphs = question_section.find_all('p')
                                
                                # Improved LaTeX extraction
                                question = ""
                                for p in question_paragraphs:
                                    # Initialize paragraph text
                                    para_text = p.get_text(strip=True)
                                    
                                    # Find all LaTeX spans
                                    latex_spans = p.find_all('span', class_='katex')
                                    for latex in latex_spans:
                                        # Extract pure LaTeX from annotation
                                        latex_annotation = latex.find('annotation', encoding='application/x-tex')
                                        if latex_annotation:
                                            pure_latex = latex_annotation.text.strip()
                                            # Replace the entire LaTeX span with its pure LaTeX representation
                                            para_text = para_text.replace(latex.get_text(strip=True), f" ${pure_latex}$ ")
                                            para_text = para_text.replace("\displaystyle ", "")
                                    
                                    question += para_text + " "
                                
                                question = question.strip()

                                # truncate if it exceeds max length
                                if len(question) > 32000:
                                    question = question[:32000] + "... [truncated]"
                                if len(reason) > 32000:
                                    reason = reason[:32000] + "... [truncated]"

                                answer = f"{reason} Thus, the final answer is \\boxed{{{answer}}}."

                                data.append({
                                    'question': question,
                                    'answer': answer
                                })
    
    return data

# Directory containing the folders with HTML files
root_dir = "problems"

# Parallel processing
with concurrent.futures.ProcessPoolExecutor() as executor:
    future_to_folder = {executor.submit(process_folder, folder, root_dir): folder for folder in os.listdir(root_dir)}
    
    all_data = []
    for future in concurrent.futures.as_completed(future_to_folder):
        all_data.extend(future.result())

df = pd.DataFrame(all_data)

df.to_csv('brilliant-community.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
print(df)