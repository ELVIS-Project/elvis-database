import requests

def get_from_elvis(file_path, username, password):
    resp = requests.get('http://127.0.0.1:8000/media/attachments'+file_path, auth = (username, password))
    return resp


def push_to_elvis(file_name, file_path):
    files={file_name, open(file_path, 'rb')}
    resp = requests.patch('http://127.0.0.1:8000/media/attachments'+file_path, files=files)
    return resp

def push_to_rodan(file_name, username, password, project_url, resourcetype):
    files={'files': open(file_name, 'rb')}
    data={'project':project_url, 'type':resourcetype }
    token = requests.post('https://rodan.simssa.ca/auth/token/', data={'username': username, 'password': password})
    test = requests.post('https://rodan.simssa.ca/resources/', files=files, data=data, headers={'Authorization':'Token '+str(token)})
    return test

if __name__ == "__main__":
    #fill in as appropriate(file name, username, password, etc) for testing purposes
    r = push_to_rodan()
    print(r.text)