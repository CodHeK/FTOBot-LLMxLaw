import streamlit as st
import json, requests
import google.generativeai as palm

from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

from dotenv import load_dotenv

load_dotenv()


api_key_header = {
    "customer-id": '',
    "x-api-key": ''
}

def generate_response(message):

    data_dict = {
        "query": [
        {
        "query": message,
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

    page_contents_array = []
    for r in response.json()['responseSet'][0]['response']:
        page_contents_array.append(r['text'])

    patents_id_array = []
    patents_title_array = []
    for r in response.json()['responseSet'][0]['document']:
        metadata = r['metadata']
        for m in metadata:
            if m['name']=='patent-id':
                patents_id_array.append(m['value'])
            if m['name']=='title':
                patents_title_array.append(m['value'])


    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

    template = """
    You are a chatbot that is designed to help individuals and businesses determine whether their new technology might infringe any intellectual property. Your answer should describe any patents related to the identified technology. Include a brief explanation as to the subject matter of the patent, and as to why the patent is relevant to the identified technology. You should also identify any companies that own patents relevant to the subject matter of the identified technology, and you should provide the user with resources to conduct further research. If there are any lawsuits or litigation related to the identified technology, identify the lawsuit and provide a brief summary of the litigation, including the parties, the allegations, and the patents at issue in the case.  Finally, you must offer an assessment of whether there is a risk that the technology infringes one of the patents you list. 

    Following the above instructions, use the context being provided and give me a summary of all the relvant patents:

    Below is the input query:
    {message}

    Here is how the response should look like:
    {best_practice}

    Please write the best response that I should send to this prospect:
    """

    prompt = PromptTemplate(
        input_variables=["message", "best_practice"],
        template=template
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    best_practice = page_contents_array
    response = chain.run(message=message, best_practice=best_practice)

    response += "\n\nThe patents referenced for this search are: \n\n"
    for idx in range(len(patents_id_array)):
        response += patents_id_array[idx] + " : " + patents_title_array[idx] + "\n\n"

    return response


def main():
    st.set_page_config(
        page_title="FTOBot")

    st.header("FTOBot")
    message = st.text_area("Query")

    if message:
        st.write("Generating the best response...")

        result = generate_response(message)

        st.info(result)


if __name__ == '__main__':
    main()