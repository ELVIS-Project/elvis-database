import requests
import json
import pickle


#note: the workflow to be used needs to be loaded in rodan manually before starting to use the following script
def get_rodan_token(username, password):
    token = requests.post('https://rodan.simssa.ca/auth/token/', data={'username': username, 'password': password})
    return token


def get_from_elvis(username, password):
    mei_files_urls = []
    # resp = requests.get('http://dev.database.elvisproject.ca/search/?filefilt=.mei&filefilt=.midi', auth = (username, password))
    # pages = json.loads(resp.text)['paginator']['total_pages']
    for page in range(1,48):
        print(page)
        search = requests.get('http://dev.database.elvisproject.ca/search/?filefilt[]=.mei&filefilt[]=.capx&page='+str(page), auth = (username, password))
        for object in json.loads(search.text)['object_list']:
            if 'pieces_searchable' in object.keys():
                piece = requests.get('http://dev.database.elvisproject.ca/piece/'+str(object['id'])+'?format=json', auth=(username, password))
                for attachment in json.loads(piece.text)['attachments']:
                    if attachment['extension']==".mei":
                        mei_files_urls.append(attachment['url'])
            else:
                movement = requests.get('http://dev.database.elvisproject.ca/movement/'+str(object['id'])+'?format=json', auth=(username, password))
                for attachment in json.loads(movement.text)['attachments']:
                    if attachment['extension']==".mei":
                        mei_files_urls.append(attachment['url'])
    with open('mei_urls', 'wb') as out_file:
            pickle.dump(mei_files_urls, out_file)


def push_to_elvis(file_path, feature_files):
    files = {}
    for item in feature_files:
        print(item.content)
    #     files.update({'xmlValue': item.content})
    # resp = requests.patch('http://127.0.0.1:8000/media/attachments'+file_path, files=files)
    # return resp

def get_from_rodan(resource_id):
    result = requests.get('https://rodan.simssa.ca/resources/?result_of_workflow_run='+str(resource_id), headers={})
    result_files = json.loads(result.text)['results']
    actual_files = []
    for results in result_files:
        file_location = results['resource_file']
        print(file_location)
        actual_files.append(requests.get(file_location, headers={}))
    return actual_files

def push_to_rodan(file, token, project_url, resourcetype):
    files={'files': file}
    resource_data={'project': project_url, 'type': resourcetype}
    resource_upload = requests.post('https://rodan.simssa.ca/resources/', files=files, data=resource_data, headers={'Authorization': ""})
    # if 200 <= resource_upload.status_code < 300:
    #     workflow_data = {"created": "null", "updated": "null", "workflow": "https://rodan.simssa.ca/workflow/4f07a022-3a73-4446-809f-78b32fa4df96/", "resource_assignments":
    #         {"https://rodan.simssa.ca/inputport/629be587-7530-4db7-ac9b-29c3c4682de4/": [json.loads(resource_upload.text)[0]['url']]},
    #         "name": "untitled", "description": "Run of Workflow untitled"}
    #     workflow_run = requests.post('https://rodan.simssa.ca/workflowruns/', data=json.dumps(workflow_data), headers={'Content-Type': 'application/json','Authorization': "" })
    #     return workflow_run
    # else:
    #     print("Could not upload resource")
    return resource_upload.text

def run_workflow(resource, token):
    resource_url = json.loads(resource)[0]['url']
    workflow_data = {"created": "null", "updated": "null", "workflow": "https://rodan.simssa.ca/workflow/4f07a022-3a73-4446-809f-78b32fa4df96/", "resource_assignments":
            {"https://rodan.simssa.ca/inputport/629be587-7530-4db7-ac9b-29c3c4682de4/": [resource_url]},
            "name": "untitled", "description": "Run of Workflow untitled"}
    workflow_run = requests.post('https://rodan.simssa.ca/workflowruns/', data=json.dumps(workflow_data), headers={'Content-Type': 'application/json','Authorization': "Token "+token })
    return workflow_run


if __name__ == "__main__":
    #fill in as appropriate(file name, username, password, etc) for testing purposes
    # symbolic_file = get_from_elvis('05/05/000000000000005/Absalon-fili-mi_Josquin-Des-Prez_file5.mei',)
    # print(symbolic_file.headers)
    # r = push_to_rodan(symbolic_file.content, '', '',
    #          'https://rodan-dev.simssa.ca/project/a1b64324-d8d6-4b8f-b4d2-88b68a6be2eb/', 'https://rodan-dev.simssa.ca/resourcetype/fe6b475c-7fa7-4659-9239-e86edeea7efa/')
    # time.sleep(2)
    # parsed_url = json.loads(r.text)['url'].split('/')
    # s = get_from_rodan(parsed_url[4])
    # print(s)
    #get_from_elvis(, )
    # mei_urls = pickle.load(open('mei_urls','rb'))
    # elvis = requests.get('http://dev.database.elvisproject.ca'+str(mei_urls[0]), auth=('', ''))
    # push_to_rodan(elvis.content, , , 'https://rodan.simssa.ca/project/a1b64324-d8d6-4b8f-b4d2-88b68a6be2eb/', 'https://rodan.simssa.ca/resourcetype/37041509-ff21-4870-bce9-045bec057596/')



