import json, requests
import google.generativeai as palm

SYS_PROMPT = '''
You are a chatbot that is designed to help individuals and businesses determine whether their new technology might infringe any intellectual property. Your answer should describe any patents related to the identified technology. Include a brief explanation as to the subject matter of the patent, and as to why the patent is relevant to the identified technology. You should also identify any companies that own patents relevant to the subject matter of the identified technology, and you should provide the user with resources to conduct further research. If there are any lawsuits or litigation related to the identified technology, identify the lawsuit and provide a brief summary of the litigation, including the parties, the allegations, and the patents at issue in the case.  Finally, you must offer an assessment of whether there is a risk that the technology infringes one of the patents you list. 

Following the above instructions, use the context being provided and give me a summary of all the relvant patents:
'''

palm.configure(api_key='')
i=1
while i>0:
    i-=1
    usr_query = str(input())
    api_key_header = {
        "customer-id": '',
        "x-api-key": ''
    }
    
    data_dict = {
        "query": [
        {
        "query": usr_query,
        "queryContext": "",
        "start": 0,
        "numResults": 5,
        "contextConfig": {
            "charsBefore": 0,
            "charsAfter": 0,
            "sentencesBefore": 2,
            "sentencesAfter": 2,
            "startTag": "%START_SNIPPET%",
            "endTag": "%END_SNIPPET%"
        },
        "corpusKey": [
            {
            "customerId": 1292512071,
            "corpusId": 2,
            "semantics": 0,
            "metadataFilter": "",
            "lexicalInterpolationConfig": {
                "lambda": 0.025
            },
            "dim": []
            }
        ],
        "summary": [
            {
            "maxSummarizedResults": 5,
            "responseLang": "eng",
            "summarizerPromptName": "vectara-summary-ext-v1.2.0"
            }
        ]
        }
    ]
    }

    payload = json.dumps(data_dict)
    response = requests.post(
        "https://api.vectara.io/v1/query",
        data=payload,
        verify=True,
        headers=api_key_header)
    growing_prompt = SYS_PROMPT + '\n\nThe user query is: \n\n' + usr_query + '\n\n And the relevant context for patents is: \n\n'
    vectara_response = response.json()
    rag_contexts = []
    for r in vectara_response['responseSet'][0]['response']:
        rag_contexts.append(r['text'])
    rag_context_str = " ".join(rag_contexts)
    growing_prompt+=rag_context_str
    palm_response = palm.chat(messages = growing_prompt)
    print(palm_response.last)


    

