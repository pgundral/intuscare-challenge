import requests
import json
import itertools

# OPTIMIZED SOLUTION
# (1) Using requests.Session() to keep a consistent session and reduce slowdown from SSL/TLS handshake
# (2) Use itertools and map() to vectorize functions instead of using
#     for loops and/or list comprehension

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

    # NOTE: Used itertools to extract codes
    all_codes = set(itertools.chain.from_iterable(patient["diagnoses"] for patient in data))

    code_descriptions, malformed_codes, priority_codes  = {}, [], []
    priority_keywords = ["respiratory failure", "covid"]

    ## FETCH all of the code descriptions from ICD-10... ##
        
    for code in all_codes:
        if not isinstance(code, str):
            malformed_codes.append(code)
            continue

        if code in code_descriptions:
            continue

        search_url = base_url.format(search_fields = "code,desc", search_term = code, max_list = 1)
        icd_endpoint = session.get(search_url)
        
        # SUCCESSFUL call (status 200)
        if icd_endpoint.status_code == 200:
            response = icd_endpoint.json()

            # NOT MALFORMED
            if response[0] > 0:
                description = response[3][0][1]
                # Add to our dictionary
                code_descriptions[code] = description

                # NOTE: Using map() to apply function to many items
                if any(map(description.lower().__contains__, priority_keywords)):
                    priority_codes.append(code)

            # MALFORMED
            else:
                malformed_codes.append(code)

            # NOT SUCCESSFUL (other status codes)
        else:
            malformed_codes.append(code)

    ## UPDATE DATA with our new descriptions ##

    # NOTE: Defining a custom function that can be applied later using map()
    # This function constructs an updated entry for each patient
    def construct_new_entry(patient):
        # Get ID and DIAGNOSES
        id = patient["patient_id"]
        all_diagnoses = patient["diagnoses"]

        described_diagnoses, malformed_diagnoses, priority_diagnoses = [], [], []

        # NOTE: Defining a custom function to transform a single code
        def transform_diagnoses(code):
            if code in malformed_codes:
                return["malform", code]
            elif code in code_descriptions:
                description = code_descriptions[code]
                return["described", (code, description)]

        # NOTE: Use map() to transform each code
        transformed_diagnoses = list(map(transform_diagnoses, all_diagnoses))

        # NOTE: Extract the codes in the right format
        described_diagnoses = [entry[1] for entry in transformed_diagnoses if entry[0] == "described"]
        malformed_diagnoses = [entry[1] for entry in transformed_diagnoses if entry[0] == "malform"]
        priority_diagnoses = [code_descriptions[code] for code in all_diagnoses if code in priority_codes]

        # Construct the final entry 
        transformed_data = {
        "patient_id": id,
        "diagnoses": described_diagnoses,
        "priority_diagnoses": priority_diagnoses,
        "malformed_diagnoses": malformed_diagnoses
        }

        return transformed_data
    
    # NOTE: Use map() to construct the entry for each patient and make into a list
    final_data = list(map(construct_new_entry, data))
    
    ## RETURN our result ##
    final_data.sort(key=lambda x: len(x["priority_diagnoses"]), reverse=True)

    return final_data

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
