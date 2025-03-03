import requests
import json
import itertools

base_url = ("https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
            "?sf={search_fields}&terms={search_term}&maxList={max_list}")

# NOTE: Created an initial session connection to speed up the SSL/TLS handshakes
session = requests.Session()

patient_data = [
    {"patient_id": 0,
     "diagnoses": ["I10", "K21.9"]},
    {"patient_id": 1,
     "diagnoses": ["E78.5", "ABC.123", "U07.1", "J96.00"]},
    {"patient_id": 2,
     "diagnoses": []},
    {"patient_id": 3,
     "diagnoses": ["U07.1", "N18.30"]},
    {"patient_id": 4,
     "diagnoses": ["I10", "E66.9", "745.902"]},
    {"patient_id": 5,
     "diagnoses": ["G47.33", "I73.9", "N18.30", 1]}
]

def solution(data):

    ## EXTRACT all of the codes from our data ##
    # For each patients in data, get each code in "diagnoses" indx
    all_codes = set(itertools.chain.from_iterable(patient["diagnoses"] for patient in data))

    ## INSTANTIATE lists ##
    # Lets make caches of all the descriptions, and malformed/priority codes we find 
    code_descriptions, malformed_codes, priority_codes  = {}, [], []
    # Lets also define our priority diagnoses
    priority_keywords = ["respiratory failure", "covid"]

    ## FETCH all of the code descriptions from ICD-10... ##
        
    for code in all_codes:
        # First, let's ensure that the code is a string
        if not isinstance(code, str):
            # If not, then it is malformed
            malformed_codes.append(code)
            continue

        # Let's check if the code already exists in our dictionary
        if code in code_descriptions:
            continue

        # If not, then call the API and get the description of the diagnosis
        search_url = base_url.format(search_fields = "code,desc", search_term = code, max_list = 1)
        icd_endpoint = session.get(search_url)
        
        # SUCCESSFUL call (status 200)
        if icd_endpoint.status_code == 200:
            # Get the JSON object
            response = icd_endpoint.json()

            # NOT MALFORMED: we get at least one row
            if response[0] > 0:
                # Get the description
                description = response[3][0][1]
                # Add to our dictionary
                code_descriptions[code] = description

                # NOTE: Using map() to apply function to many items
                # Also, check if any word appears in the priority keywords
                if any(map(description.lower().__contains__, priority_keywords)):
                    priority_codes.append(code)

            # MALFORMED: no matches
            else:
                # Add to our malformed codes
                malformed_codes.append(code)

            # NOT SUCCESSFUL (other status codes)
        else:
            # Also add to our malformed codes
            malformed_codes.append(code)

    ## UPDATE DATA with our new descriptions ##
    transformed_data = []

    # FOR each patient in our original data
    for patient in data:
        # Get their id and current diagnosis codes
        id = patient["patient_id"]
        all_diagnoses = patient["diagnoses"]

        # Lists to store diagnoses with descriptions or malformed
        described_diagnoses = []
        malformed_diagnoses = []
        # List for priority diagnoses
        priority_diagnoses = []

        # TRANSFORM diagnoses
        # FOR each code in our diagnoses
        for code in all_diagnoses:

            # Check if it was in our list of malformed codes
            if code in malformed_codes:
                malformed_diagnoses.append(code)
            # Otherwise, check if we have a description
            elif code in code_descriptions:
                # Add that to our diagnoses for the patient
                description = code_descriptions[code]
                described_diagnoses.append((code, description))

                # Finally, check if this diagnosis is a priority one (COVID, Respiratory)
                if code in priority_codes:
                    # Add the description to our priority_diagnoses
                    priority_diagnoses.append(description)
        
        # STRUCTURE our data into a dictionary for the response
        transformed_data.append({
            "patient_id": id,
            "diagnoses": described_diagnoses,
            "priority_diagnoses": priority_diagnoses,
            "malformed_diagnoses": malformed_diagnoses
        })
    
    ## RETURN our result ##
    transformed_data.sort(key=lambda x: len(x["priority_diagnoses"]), reverse=True)

    return transformed_data


output = solution(patient_data)

expected_output = [
        {'patient_id': 1,
         'diagnoses': [
             ('E78.5', 'Hyperlipidemia, unspecified'),
             ('U07.1', 'COVID-19'),
             ('J96.00', 'Acute respiratory failure, unspecified whether with hypoxia or hypercapnia')],
         'priority_diagnoses': [
             'COVID-19', 'Acute respiratory failure, unspecified whether with hypoxia or hypercapnia'],
         'malformed_diagnoses': ['ABC.123']
        },
        {'patient_id': 3,
         'diagnoses': [
             ('U07.1', 'COVID-19'),
             ('N18.30', 'Chronic kidney disease, stage 3 unspecified')],
         'priority_diagnoses': ['COVID-19'],
         'malformed_diagnoses': []
        },
        {'patient_id': 0,
         'diagnoses': [
             ('I10', 'Essential (primary) hypertension'),
             ('K21.9', 'Gastro-esophageal reflux disease without esophagitis')],
         'priority_diagnoses': [],
         'malformed_diagnoses': []
        },
        {'patient_id': 2, 'diagnoses': [],
         'priority_diagnoses': [],
         'malformed_diagnoses': []
        },
        {'patient_id': 4,
         'diagnoses': [
             ('I10', 'Essential (primary) hypertension'),
             ('E66.9', 'Obesity, unspecified')],
         'priority_diagnoses': [],
         'malformed_diagnoses': ['745.902']
        },
        {'patient_id': 5,
         'diagnoses': [
             ('G47.33', 'Obstructive sleep apnea (adult) (pediatric)'),
             ('I73.9', 'Peripheral vascular disease, unspecified'),
             ('N18.30', 'Chronic kidney disease, stage 3 unspecified')],
         'priority_diagnoses': [],
         'malformed_diagnoses': [1]
        }
    ]
try:
    assert(output == expected_output)
except AssertionError:
    print('error: your output does not match the expected output')
else:
    print('success!')
