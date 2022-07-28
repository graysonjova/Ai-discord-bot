import json

import requests



def query(payload, API_URL,headers):
    data = json.dumps(payload)
    response = requests.request('POST',API_URL, headers=headers,
                                    data=data)
    ret = json.loads(response.content.decode('utf-8'))
    return ret


