from __future__ import absolute_import

from elvis.celery import app

from django.conf import settings

# LM: 
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
@app.task()
def do_work():
    """ Get some rest, asynchronously, and update the state all the time """
    for i in range(100):
        sleep(0.1)
        current_task.update_state(state='PROGRESS',
            meta={'current': i, 'total': 100})


def poll_state(request):
    """ A view to report the progress to the user """
    if 'job' in request.GET:
        job_id = request.GET['job']
    else:
        return HttpResponse('No job id given.')

    job = AsyncResult(job_id)
    data = job.result or job.state
    return HttpResponse(json.dumps(data), mimetype='application/json')


def init_work(request):
    """ A view to start a background job and redirect to the status page """
    job = do_work.delay()
    return HttpResponseRedirect(reverse('poll_state') + '?job=' + job.id)


urlpatterns = patterns('webapp.modules.asynctasks.progress_bar_demo',
    url(r'^init_work$', init_work),
    url(r'^poll_state$', poll_state, name="poll_state"),
)
'''