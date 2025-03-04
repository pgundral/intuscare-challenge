import requests
import aiohttp
import asyncio
import ssl

# ASYNCH ("Batch" API calling) SOLUTION
# (1) Using asyncio and aiohttp to make async API calls, lowering the wait time between responses/calls

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

base_url = ("https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
            "?sf={search_fields}&terms={search_term}&maxList={max_list}")

# NOTE: Define an async function for API calling
async def get_icd_description(session, code):
    search_url = base_url.format(search_fields="code,desc", search_term=code, max_list=1)
    async with session.get(search_url) as response:  # Disable SSL verification
        result = await response.json()
        # print(f"Fetched {code}: {result}")  # Debug print
        return code, result

# NOTE: Define our solution as async
async def solution(data):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    all_codes = {code for patient in data for code in patient["diagnoses"]}
    code_descriptions, malformed_codes, priority_codes = {}, [], []
    priority_keywords = ["respiratory failure", "covid"]

    # NOTE: Gather responses asyncronously using our custom function
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        tasks = [get_icd_description(session, code) for code in all_codes]
        responses = await asyncio.gather(*tasks)

        for code, result in responses:
            try:
                if result[0] > 0:
                    description = result[3][0][1]
                    code_descriptions[code] = description
                    if any(keyword in description.lower() for keyword in priority_keywords):
                        priority_codes.append(code)
                else:
                    malformed_codes.append(code)
            except (IndexError, KeyError) as e:
                print(f"Error processing code {code}: {e}")
                malformed_codes.append(code)

    transformed_data = []

    ## TRANSFORM and update our data
    for patient in data:
        described_diagnoses, malformed_diagnoses, priority_diagnoses = [], [], []
        for code in patient["diagnoses"]:
            if code in malformed_codes:
                malformed_diagnoses.append(code)
            elif code in code_descriptions:
                description = code_descriptions[code]
                described_diagnoses.append((code, description))
                if code in priority_codes:
                    priority_diagnoses.append(description)

        transformed_data.append({
            "patient_id": patient["patient_id"],
            "diagnoses": described_diagnoses,
            "priority_diagnoses": priority_diagnoses,
            "malformed_diagnoses": malformed_diagnoses
        })

    ## CLEAN, SORT, and RETURN
    transformed_data.sort(key=lambda x: len(x["priority_diagnoses"]), reverse=True)
    return transformed_data

# NOTE: Using asyncio.run() to run our async solution function
output = asyncio.run(solution(patient_data))

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
