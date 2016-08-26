from lxml import etree
import requests
import json
import pickle



#note: the workflow to be used needs to be loaded in rodan manually before starting to use the following script
def get_rodan_token(username, password):
    token = requests.post('https://rodan.simssa.ca/auth/token/', data={'username': username, 'password': password})
    return token


def get_from_elvis(username, password):
    midi_files_urls = []
    # resp = requests.get('http://dev.database.elvisproject.ca/search/?filefilt=.midi&filefilt=.midi', auth = (username, password))
    # pages = json.loads(resp.text)['paginator']['total_pages']
    for page in range(1,39):
        print(page)
        search = requests.get('http://dev.database.elvisproject.ca/search/?filefilt[]=.midi&filefilt[]=.capx&page='+str(page), auth = (username, password))
        for object in json.loads(search.text)['object_list']:
            if 'pieces_searchable' in object.keys():
                piece = requests.get('http://dev.database.elvisproject.ca/piece/'+str(object['id'])+'?format=json', auth=(username, password))
                for attachment in json.loads(piece.text)['attachments']:
                    if attachment['extension']==".midi":
                        midi_files_urls.append(attachment['url'])
            else:
                movement = requests.get('http://dev.database.elvisproject.ca/movement/'+str(object['id'])+'?format=json', auth=(username, password))
                for attachment in json.loads(movement.text)['attachments']:
                    if attachment['extension']==".midi":
                        midi_files_urls.append(attachment['url'])
    with open('midi_urls', 'wb') as out_file:
            pickle.dump(midi_files_urls, out_file)


def push_to_elvis(token):
    results = pickle.load(open('rodan_results_urls', 'rb'))

    for page in results:
        for result in page:
            file_path = '/'.join(result['name'].split('@', 3)[:3])
            if result['resource_type'] == 'https://rodan.simssa.ca/resourcetype/f6c9e1a1-dd34-40f1-a898-c15914aa00d3/':
                file_name = ''.join((result['name'].split('@', 3)[3]+'.arff').split())
            elif result['resource_type']== 'https://rodan.simssa.ca/resourcetype/f4ba139d-6596-4ebd-861c-1ada8c4653df/':
                file_name = ''.join((result['name'].split('@', 3)[3]+'.csv').split())
            else:
                root = etree.XML(requests.get(result['resource_file'], headers={'Authorization': "Token "+token}).text)
                tree = etree.ElementTree(root)
                if 'feature_vector_file' in tree.docinfo.doctype:
                    file_name = ''.join((result['name'].split('@', 3)[3]+'_values'+'.xml').split())
                elif 'feature_key_file' in tree.docinfo.doctype:
                    file_name = ''.join((result['name'].split('@', 3)[3]+'_definitions'+'.xml').split())
                else:
                    print("Bad XML")
                    break
            files = {'files': requests.get(result['resource_file'], headers={'Authorization': "Token "+token}).content}
            resp = requests.put('http://127.0.0.1:8000'+'/media/attachments/'+file_path+'/', files=files, data={'file_path':'/'+file_path+'/', 'file_name': file_name}, auth=('', ''))

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

def push_to_rodan(filename, file, project_url, resourcetype, token):
    files={'files': (filename, file)}
    print(filename)
    resource_data={'project': project_url, 'type': resourcetype}
    resource_upload = requests.post('https://rodan.simssa.ca/resources/', files=files, data=resource_data, headers={'Authorization': "Token "+token})
    return resource_upload

def run_workflow(token, workflow_url, input_url):
    resourcelist = []
    for pageno in range(1,json.loads(requests.get('https://rodan.simssa.ca/',
                                                headers={'Authorization': "Token "+token}).text)['number_of_pages']+1):
        resources = requests.get(''.format(str(pageno)),
                                 headers={'Authorization': "Token "+token})
        for i in json.loads(resources.text)['results']:
            print(i)
            resourcelist.append(i['url'])
        workflow_data = {"created": "null", "updated": "null", "workflow": workflow_url, "resource_assignments":
            {input_url: resourcelist},
            "name": "jsymbolic_elvis", "description": "Run of Workflow jsymbolic_elvis"}
        workflow_run = requests.post('https://rodan.simssa.ca/workflowruns/', data=json.dumps(workflow_data), headers={'Content-Type': 'application/json','Authorization': "Token "+token})

    json.loads(workflow_run.text)['url']
    all_results = []
    initial_result = requests.get("https://rodan.simssa.ca/resources/?result_of_workflow_run={0}".format(""), headers={'Authorization': "Token "+token})
    for page in range(1, json.loads(initial_result.text)['total_pages']+1):
        results = requests.get("https://rodan.simssa.ca/resources/?page={0}&result_of_workflow_run={1}".format(str(page),""), headers={'Authorization': "Token "+token})
        print(results.text)
        all_results.append(json.loads(results.text)['results'])
    with open('rodan_results_urls', 'wb') as out_file:
        pickle.dump(all_results, out_file)



if __name__ == "__main__":

    #get_from_elvis('','')
    # midi_urls = pickle.load(open('midi_urls','rb'))
    # for url in midi_urls:
    #     elvis = requests.get('http://dev.database.elvisproject.ca'+str(url), auth=('', ''))
    #     result = push_to_rodan(url.split("/", 3)[3].replace('/', '@'), elvis.content, '', '')
    #     print(result.content)
    #print(get_rodan_token('', '').content)





