import requests
import json
import os
import textract
from requests_ntlm import HttpNtlmAuth
from pprint import pprint

# Put your essex loggin credentials in fields 'username' and 'password'
essexUsername = ''
essexPassword = ''

# Open json file with scraped links and data
with open('modules.json') as data_file:
    data = json.load(data_file)

# Create empty exam list
exams = []

# Loop thrue module data to futher proccess links
for module in data:
    for examLink in module['exams']:
        print(examLink['url'])
        exam = module.copy()
        del exam['exams']
        exam['paperUrl'] = examLink['url']
        exam['year'] = examLink['year']
        download = requests.get(examLink['url'], auth=HttpNtlmAuth(essexUsername, essexPassword))
        download.raise_for_status()
        fileName = os.path.basename(examLink['url'])
        # Write PDF files to local storage
        with open('pdf/' + fileName, 'wb') as handle:
            for block in download.iter_content(1024):
                handle.write(block)
        # Using textract library to process from PDF to text format.
        text = textract.process("pdf/"+ fileName )
        # Appending json values for JSON local storage
        exam['content'] = text
        exam['moduleId'] = module['id']
        exam['id'] = module['id'] + '_' + fileName.replace('.', '')
        exams.append(exam)

# Write to file which is going to be used for Elastic database
with open('exams.json', 'w') as handle:
    for exam in exams:
        indexObject = { "index": { "_id": exam['id'] } }
        handle.write(json.dumps(indexObject) + '\n' + json.dumps(exam) + '\n')
