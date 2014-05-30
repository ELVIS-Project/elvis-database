from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elvis.settings')

app = Celery('elvis', broker='amqp://', backend='amqp://')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if __name__ == '__main__':
    app.start()

'''
MOVED TO tasks.py


# LM: For elvis' purposes and the one task of serving a zipped file, just defining it here is convenient
# Check this out: http://massivescale.blogspot.ca/2011/09/celery-task-queue-with-php.html
# TODO: Change unicode encoding to utf for terminal commands
@app.task(name='elvis.celery.zip_files')
def zip_files(paths, username):
	import uuid, subprocess, string, os, shutil, datetime

	# Create unique dummy folder in user_downloads using uuid
	dummy_folder = str(uuid.uuid4())
	dummy_root_dir = os.path.join(settings.MEDIA_ROOT, 'user_downloads', username)
	dummy_path = os.path.join(dummy_root_dir, dummy_folder)
	print(dummy_path)

	#if not os.path.exists(dummy_path):
    #        os.makedirs(dummy_path)

	# cp the requested files into dummy_folder
	# could use shutil.copy2, but there are warnings about missing metadata that I won't risk in a database like this \
	for item in paths:
		# tokenise to remove the actual file name from path name
		print(item)
		file_name = os.path.basename(item)
		##cp_command = ["cp", item, os.path.join(dummy_path, file_name)]
		##print(cp_command)
		##cp_process = subprocess.Popen(cp_command, stdout=PIPE, stderr=STDOUT).communicate()
		##cp_process.wait()

		#if we decide to use shutil, here it is:
		#shutil.copy2(item, os.path.join(dummy_path, file_name))

	# Now create the zip
	zip_name = username+"-"+datetime.datetime.utcnow().date().isoformat()
	# Have to cd to directory for archive output... don't know why make_archive has a root_dir argument that doesn't do this
	#os.chdir(dummy_root_dir)
	#zip_path = shutil.make_archive(zip_name, "zip", dummy_root_dir, dummy_path)
	##zip_command = ["zip", "-r", zip_name, dummy_path]
	print(zip_name)
	print(dummy_root_dir, dummy_path)

	#return zip_path
'''