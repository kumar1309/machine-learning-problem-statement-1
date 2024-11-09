from flask import Flask, render_template, request
import spacy
import csv
import nltk
from nltk.corpus import stopwords

app = Flask(__name__)

# Load spaCy model and NLTK stopwords
nlp = spacy.load("en_core_web_sm")
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Load medical terms, treatments, remedies, and other relevant data from CSV file
def load_medical_data(csv_file):
    terms = set()
    treatments = {}
    remedies = {}
    biological_names = {}
    prevention_methods = {}
    symptoms = {}
    lab_results = {}
    
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            disease = row['Disease'].lower()
            biological_name = row['Biological Name'].lower()
            drugs = [drug.strip().lower() for drug in row['Drugs'].split(',')]
            treatment = row['Treatment Duration']
            remedy = row['Remedy']
            prevention = row['Prevention Methods']
            symptom = row['Symptoms']
            lab_result = row['Lab Research']
            
            terms.update([disease] + drugs)
            for drug in drugs:
                treatments[drug] = treatment
                remedies[drug] = remedy
                symptoms[drug] = symptom
                lab_results[drug] = lab_result

            treatments[disease] = treatment
            remedies[disease] = remedy
            biological_names[disease] = biological_name
            prevention_methods[disease] = prevention
            symptoms[disease] = symptom
            lab_results[disease] = lab_result
            
    return terms, treatments, remedies, biological_names, prevention_methods, symptoms, lab_results

# Load the CSV data
CSV_FILE_NAME = 'C:/Users/user/python practice/data.csv'
MEDICAL_TERMS, TREATMENTS, REMEDIES, BIOLOGICAL_NAMES, PREVENTION_METHODS, SYMPTOMS, LAB_RESULTS = load_medical_data(CSV_FILE_NAME)

# Helper function to check if a term is a Boolean operator
def is_boolean_operator(token):
    return token.lower() in {"and", "or", "not"}

def preprocess_text(text):
    """
    Preprocesses input text by tokenizing, removing stopwords, and extracting relevant medical terms.
    """
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_punct]
    return tokens

@app.route('/', methods=['GET', 'POST'])
def index():
    boolean_query = ""
    treatment_solutions = []
    remedy_solutions = []
    show_treatment_and_remedy = False
    biological_name_result = ""
    prevention_methods_result = ""
    show_biological_and_prevention = False
    symptoms_result = ""
    show_symptoms = False
    lab_results_result = ""
    show_lab_results = False

    if request.method == 'POST':
        user_input = request.form.get('query')
        tokens = preprocess_text(user_input)
        
        query_terms = []
        skip_next_term = False
        
        for token in tokens:
            if skip_next_term:
                query_terms.append(f"{token}")
                skip_next_term = False
                continue
            
            if is_boolean_operator(token):
                operator = token.upper()
                query_terms.append(operator)
                if operator == "NOT":
                    skip_next_term = True
            elif token in MEDICAL_TERMS:
                if 'treatment' in user_input or 'drug' in user_input:
                    show_treatment_and_remedy = True
                    if skip_next_term:
                        skip_next_term = False
                        continue
                    if token in TREATMENTS:
                        treatment_solutions.append(f"{token.capitalize()}: {TREATMENTS[token]}")
                    if token in REMEDIES:
                        remedy_solutions.append(f"{token.capitalize()}: {REMEDIES[token]}")
                if 'research' in user_input or 'studies' in user_input:
                    show_biological_and_prevention = True
                    if token in BIOLOGICAL_NAMES:
                        biological_name_result = f"{token.capitalize()}: {BIOLOGICAL_NAMES[token]}"
                    if token in PREVENTION_METHODS:
                        prevention_methods_result = f"{token.capitalize()}: {PREVENTION_METHODS[token]}"
                if 'medical' in user_input or 'records' in user_input:
                    show_symptoms = True
                    if token in SYMPTOMS:
                        symptoms_result = f"{token.capitalize()}: {SYMPTOMS[token]}"
                if 'diagnostic' in user_input:
                    show_lab_results = True
                    if token in LAB_RESULTS:
                        lab_results_result = f"{token.capitalize()}: {LAB_RESULTS[token]}"
                    if token in SYMPTOMS:
                        symptoms_result = f"{token.capitalize()}: {SYMPTOMS[token]}"
                query_terms.append(token)

        boolean_query = " ".join(query_terms)

    return render_template("index.html", boolean_query=boolean_query, treatment_solutions=treatment_solutions, remedy_solutions=remedy_solutions, show_treatment_and_remedy=show_treatment_and_remedy, biological_name_result=biological_name_result, prevention_methods_result=prevention_methods_result, show_biological_and_prevention=show_biological_and_prevention, symptoms_result=symptoms_result, show_symptoms=show_symptoms, lab_results_result=lab_results_result, show_lab_results=show_lab_results)

if __name__ == '__main__':
    app.run(debug=True)