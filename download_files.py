import requests
import json
import pickle
import argparse
import re
import os
# The code between ''' and ''' is not used at this moment, but preserved for the future usage.

'''
"""
Pushes the resulting feature files from the jsymbolic run into the appropriate places in the database
(entry corresponding to where the original file came from).
TODO: figure out what is preventing uploads to what should be the proper media file location on the backend.
"""


def push_to_elvis(token, elvis_username, elvis_password):
    results = pickle.load(open('rodan_results_urls', 'rb'))

    for page in results:
        for result in page:
            file_path = '/'.join(result['name'].split('@', 3)[:3])
            if result['resource_type'] == 'https://api.rodan.simssa.ca/resourcetype/f6c9e1a1-dd34-40f1-a898-c15914aa00d3/':
                file_name = ''.join((result['name'].split('@', 3)[3]+'.arff').split())
            elif result['resource_type'] == 'https://api.rodan.simssa.ca/resourcetype/f4ba139d-6596-4ebd-861c-1ada8c4653df/':
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
            resp = requests.put('http://127.0.0.1:8000'+'/media/attachments/'+file_path+'/', files=files, data={'file_path':'/'+file_path+'/', 'file_name': file_name}, auth=(elvis_username, elvis_password))

    return resp


"""
Download the files from the provided url list  and upload them into the appropriate rodan project as resources.

"""
def push_to_rodan(elvis_username, elvis_password, file_url_array, project_url, resourcetype, token):
    resources = []

    for url in file_url_array:

        files={'files': ('@'.join(url.split('/')[3:]),
                         requests.get('http://132.206.14.132'+url, auth=(elvis_username, elvis_password)))}

        resource_data={'project': project_url, 'type': resourcetype}
        resource_upload = requests.post('https://api.rodan.simssa.ca/resources/', files=files, data=resource_data, headers={'Authorization': "Token "+token})
        resources.append(json.loads(resource_upload.text['url']))
    return resources



"""
Load up the appropriate resources into the jsymbolic workflow, then run it, logging what goes wrong if it does.
TODO: re-create a proper logging mechanism
"""
def run_workflow(token, workflow_url, inputport_url):
    resourcelist = []
    for pageno in range(1,json.loads(requests.get(inputport_url,
                                                  headers={'Authorization': "Token "+token}).text)['number_of_pages']+1):
        resources = requests.get(''.format(str(pageno)),
                                 headers={'Authorization': "Token "+token})
        for i in json.loads(resources.text)['results']:
            print(i)
            resourcelist.append(i['url'])
    workflow_data = {"created": "null", "updated": "null", "workflow": workflow_url, "resource_assignments":
        {inputport_url: resourcelist},
                         "name": "jsymbolic_elvis", "description": "Run of Workflow jsymbolic_elvis"}
    workflow_run = requests.post('https://api.rodan.simssa.ca/workflowruns/', data=json.dumps(workflow_data), headers={'Content-Type': 'application/json','Authorization': "Token "+token})

    #wait for the workflow to be done. TODO: reinstate logging for errors (where status = -1)
    while(True):
        time.sleep(1)
        status = json.loads(requests.get(json.loads(workflow_run.text)['url'], headers={'Authorization': "Token "+token}).text)['results'][0]['status']
        if status != 1:
            break

    #once the workflow is done, get the results

    json.loads(workflow_run.text)['url']
    all_results = []
    initial_result = requests.get("https://api.rodan.simssa.ca/resources/?result_of_workflow_run={0}".format(""), headers={'Authorization': "Token "+token})
    for page in range(1, json.loads(initial_result.text)['total_pages']+1):
        results = requests.get("https://api.rodan.simssa.ca/resources/?page={0}&result_of_workflow_run={1}".format(str(page),""), headers={'Authorization': "Token "+token})
        print(results.text)
        all_results.append(json.loads(results.text)['results'])
    with open('rodan_results_urls', 'wb') as out_file:
        pickle.dump(all_results, out_file)
    return all_results


"""
Get the results from the jsymbolic workflow run  of all the previously uploaded files
"""
def get_from_rodan(resource_id):
    result = requests.get('https://api.rodan.simssa.ca/resources/?result_of_workflow_run='+str(resource_id), headers={})
    result_files = json.loads(result.text)['results']
    actual_files = []
    for results in result_files:
        file_location = results['resource_file']
        print(file_location)
        actual_files.append(requests.get(file_location, headers={}))
    return actual_files





#note: the workflow to be used needs to be loaded in rodan manually before starting to use the following script
def get_rodan_token(username, password):
    token = requests.post('https://api.rodan.simssa.ca/auth/token/', data={'username': username, 'password': password})
    print(token.text)
    return json.loads(token.text)['token']


def get_from_elvis_dev(username, password):
    midimei_files_urls = []
    resp = requests.get('http://132.206.14.132/search/?filefilt=.midi&filefilt=.mei&filefilt=.mid&filefilt=.xml', auth = (username, password))
    pages = json.loads(resp.text)['paginator']['total_pages']
    for page in range(1,pages + 1):
        print(page)
        search = requests.get('http://132.206.14.132/search/?filefilt[]=.midi&filefilt[]=.mei&filefilt[]=.xml&filefilt[]=.mid&page='+str(page), auth = (username, password))
        for object in json.loads(search.text)['object_list']:
            if 'pieces_searchable' in object.keys():
                piece = requests.get('http://132.206.14.132/piece/'+str(object['id'])+'?format=json', auth=(username, password))
                for attachment in json.loads(piece.text)['attachments']:
                    if attachment['extension'] == ".midi" or attachment['extension'] == ".mei" or attachment['extension'] == ".xml" or attachment['extension'] == ".mid":
                        midimei_files_urls.append(attachment['url'])
            else:
                movement = requests.get('http://132.206.14.132/movement/'+str(object['id'])+'?format=json', auth=(username, password))
                for attachment in json.loads(movement.text)['attachments']:
                    if attachment['extension'] == ".midi" or attachment['extension'] == ".mei" or attachment['extension'] == ".xml" or attachment['extension'] == ".mid":
                        midimei_files_urls.append([attachment['url'], attachment['extension']])
    with open('midi_urls', 'wb') as out_file:
            pickle.dump(midimei_files_urls, out_file)
    pattern = re.compile(r'\d/[A-Za-z]')
    for url in midimei_files_urls:  # download the files
        if(type(url) == str):
            match = pattern.search(url)
            ptr = int((match.span()[0] + match.span()[1]) /2)
            download_with_requests('http://132.206.14.132'+url, './downloaded_files/' + url[ptr + 1:], username, password)
        else:
            urll = url[0]
            match = pattern.search(urll)
            if(match != None):
                ptr = int((match.regs[0][0] + match.regs[0][1]) / 2)
                download_with_requests('http://132.206.14.132' + urll, './downloaded_files/' + urll[ptr + 1:], username, password)
            else:
                download_with_requests('http://132.206.14.132' + urll, './downloaded_files/' + urll[41:], username, password)  # exceptions: the file name begin with a digit

    return midimei_files_urls

'''


def download_with_requests(url, filename, username, password):
    r = requests.get(url, auth=(username, password))
    with open(filename, "wb") as code:
        code.write(r.content)

"""
Gets the urls of midi and mei and xml files currently in the elvis database.
"""


def get_from_elvis_prod(username, password):
    save_dir = 'downloaded_files'
    if os.path.exists(save_dir) is False:
        os.mkdir(save_dir)
    flog = open('./' + save_dir + '/' + 'download_log.txt','w')
    midimei_files_urls = []
    resp = requests.get('http://database.elvisproject.ca/search/?filefilt=.midi&filefilt=.mei&filefilt=.mid&filefilt=.xml'
                        '&filefilt=.MIDI&filefilt=.MEI&filefilt=.MID&filefilt=.XML', auth = (username, password))
    # just in case there are files with upper case extensions
    pages = json.loads(resp.text)['paginator']['total_pages']
    for page in range(1, pages+1):
        print(page)
        if(page == 5):
            print('debug')
        search = requests.get('http://database.elvisproject.ca/search/?filefilt[]=.midi&filefilt[]=.mei&filefilt[]=.xml&filefilt[]=.mid'
                              '&filefilt[]=.MID&filefilt[]=.MIDI&filefilt[]=.MEI&filefilt[]=.XML&page='+str(page), auth = (username, password))  #
        # just in case there are files with upper case extensions
        for object in json.loads(search.text)['object_list']:
            if 'pieces_searchable' in object.keys():
                piece = requests.get('http://database.elvisproject.ca/piece/'+str(object['id'])+'?format=json', auth=(username, password))
                if(piece.text.find('Not found') != -1):  # need to write in a log file, though
                    print('-------------------------' , end='\n', file=flog)
                    print('Title: ' + object['title'], end='\n', file=flog)
                    print('Status code: ' + str(piece.status_code), end='\n', file=flog)
                    print('-------------------------')
                    print('Title: ' + object['title'])
                    print('Status code: ' + str(piece.status_code))
                    continue
                for attachment in json.loads(piece.text)['attachments']:
                    if attachment['extension'] == ".midi" or attachment['extension'] == ".mei" or attachment['extension'] == ".xml" or attachment['extension'] == ".mid":
                        midimei_files_urls.append(attachment['url'])
            else:
                movement = requests.get('http://database.elvisproject.ca/movement/'+str(object['id'])+'?format=json', auth=(username, password))
                for attachment in json.loads(movement.text)['attachments']:
                    if attachment['extension'] == ".midi" or attachment['extension'] == ".mei" or attachment['extension'] == ".xml" or attachment['extension'] == ".mid":
                        midimei_files_urls.append([attachment['url'], attachment['extension']])
    with open('midi_urls', 'wb') as out_file:
            pickle.dump(midimei_files_urls, out_file)
    pattern = re.compile(r'\d/[A-Za-z]')
    for url in midimei_files_urls:
        if(type(url) == str):
            match = pattern.search(url)
            ptr = int((match.span()[0] + match.span()[1]) /2)
            download_with_requests('http://database.elvisproject.ca'+url, './' + save_dir + '/' + url[ptr + 1:], username, password)
        else:
            urll = url[0]
            match = pattern.search(urll)
            if(match != None):
                ptr = int((match.regs[0][0] + match.regs[0][1]) / 2)
                download_with_requests('http://database.elvisproject.ca' + urll, './' + save_dir + '/' + urll[ptr + 1:], username, password)
            else:
                download_with_requests('http://database.elvisproject.ca' + urll, './' + save_dir + '/' + urll[41:], username, password)
    flog.close()
    return midimei_files_urls


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("elvis_username")
    parser.add_argument("elvis_password")
    args = parser.parse_args()
    elvis_urls = get_from_elvis_prod(args.elvis_username, args.elvis_password)
    print('the number of files found:', len(elvis_urls))
    for i in elvis_urls:
        print(i)













