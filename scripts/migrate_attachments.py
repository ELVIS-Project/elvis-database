def att():
	for a in Attachment.objects.all():
    		path = '/usr/local/elvis-database/media_root' + a.__str__().split('media_root')[1]
    		try:
        		with open(path, 'r+b') as f:
        			att = File(f)
        			a.attachment = att
        			a.save()
    		except IOError:
        		with open('/usr/local/elvis-database/missed_attachments.txt', 'a') as file:
            			file.write(path)
        		continue
