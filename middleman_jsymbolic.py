import requests
import json
import time

#note: the workflow to be used needs to be loaded in rodan manually before starting to use the following script
def get_rodan_token(username, password):
    token = requests.post('https://rodan.simssa.ca/auth/token/', data={'username': username, 'password': password})
    return token


def get_from_elvis(file_path, username, password):
    resp = requests.get('http://database.elvisproject.ca/media/attachments/'+file_path, auth = (username, password))
    return resp


def push_to_elvis(file_path, feature_files):
    files = {}
    for item in feature_files:
        files.update({'files': item.content})
    resp = requests.patch('http://127.0.0.1:8000/media/attachments'+file_path, files=files)
    return resp

def get_from_rodan(resource_id):
    result = requests.get('https://rodan.simssa.ca/resources/?result_of_workflow_run='+str(resource_id), headers={})
    result_files = json.loads(result.text)['results']
    actual_files = []
    for results in result_files:
        file_location = results['resource_file']
        print(file_location)
        actual_files.append(requests.get(file_location, headers={}))
    return actual_files

def push_to_rodan(file_name, username, password, project_url, resourcetype):
    files={'files': file_name}
    resource_data={'project': project_url, 'type': resourcetype}
    #token = get_rodan_token(username, password)
    resource_upload = requests.post('https://rodan.simssa.ca/resources/', files=files, data=resource_data, headers={})
    if 200 <= resource_upload.status_code < 300:
        workflow_data = {"created": "null", "updated": "null", "workflow": "https://rodan.simssa.ca/workflow/4f07a022-3a73-4446-809f-78b32fa4df96/", "resource_assignments":
            {"https://rodan.simssa.ca/inputport/629be587-7530-4db7-ac9b-29c3c4682de4/": [json.loads(resource_upload.text)[0]['url']]},
            "name": "untitled", "description": "Run of Workflow untitled"}
        workflow_run = requests.post('https://rodan.simssa.ca/workflowruns/', data=json.dumps(workflow_data), headers={'Content-Type': 'application/json', })
        return workflow_run
    else:
        print("Could not upload resource")


if __name__ == "__main__":
    #fill in as appropriate(file name, username, password, etc) for testing purposes
    symbolic_file = get_from_elvis('05/05/000000000000005/Absalon-fili-mi_Josquin-Des-Prez_file5.mei',)
    print(symbolic_file.headers)
    r = push_to_rodan(symbolic_file.content, , ,
             'https://rodan.simssa.ca/project/a1b64324-d8d6-4b8f-b4d2-88b68a6be2eb/', 'https://rodan.simssa.ca/resourcetype/fe6b475c-7fa7-4659-9239-e86edeea7efa/')
    time.sleep(2)
    parsed_url = json.loads(r.text)['url'].split('/')
    s = get_from_rodan(parsed_url[4])
    print(s)



