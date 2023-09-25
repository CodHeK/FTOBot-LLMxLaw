# Helper to upload files to Vectara
import json, requests

def POST(payload):
    post_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'customer-id': '',
        'x-api-key': ''
    }
    response = requests.post(
        "https://api.vectara.io/v1/index",
        data=payload,
        verify=True,
        headers=post_headers)

    print(response)
    if response.status_code != 200:
        print("REST upload failed with code %d, reason %s, text %s",
                       response.status_code,
                       response.reason,
                       response.text)
        return response, False
    return response, True


with open('./data/response0_100.json') as f:
    results = json.load(f)
    idx = 0

    for result in results:
        document = {}

        document['document_id'] = "doc-id-" + str(result['patentApplicationNumber'])
        document['title'] = result['inventionTitle']
        document['metadata_json'] = json.dumps(
            {
                "patent-id": result['patentApplicationNumber'],
                "publicationDate": result['publicationDate'],
                "filingDate": result['filingDate'],
                "category": result['inventionSubjectMatterCategory'],
                # "authors": result['inventorNameArrayText'][0],
                "idx": idx,
            }
        )

        sections = []
        section = {}

        section['text'] = result['claimText'][0] + '||||' +  result['descriptionText'][0] + '||||' + result['abstractText'][0]

        sections.append(section)
        document['section'] = sections

        request = {}
        request['customer_id'] = ''
        request['corpus_id'] = 2
        request['document'] = document

        payload = json.dumps(request)

        POST(payload)

        idx += 1
    