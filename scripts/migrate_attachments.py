
""" Unicode Remover script
Attempts to convert file-names to ascii, if they fail, then rename them
using only ascii. Needed because the django file static server view
does not always play nice with unicode in filenames.
"""
def rename_files_to_ascii():
    import os.path
    import unicodedata
    path_err = 0
    val_err = 0
    open_err = 0
    to_be_renamed = 0
    a1 = None
    for a in Attachment.objects.all():

        try:
            path, file_name = os.path.split(a.attachment.path)
        #catch Attachments which don't have files and delete them
        except ValueError:
            print("has no value" + str(a.id))
            a.delete()
            val_err += 1
            continue

        try:
            # if its already ascii, skip it
            file_name.encode('ascii')
            continue
        except UnicodeEncodeError:
            if not a1:
                a1 = a
            to_be_renamed += 1
            pass

        old_path = a.attachment.path
        with open(old_path, 'r+b') as f:
            pass
        new_name = unicodedata.normalize('NFKD', file_name).encode('ascii', 'ignore')
        new_name = new_name.decode('utf-8')
        new_path = os.path.join(path, new_name)

        with open('name_changes', 'a') as file:
            file.write(old_path + ", " + new_path)
            file.write("\n")

        new_name = os.path.splitext(new_name)
        a.rename(new_name[0])

    print("Path errors = " + str(path_err) + ", open errors = " + str(open_err)
          + ", to be renamed = " + str(to_be_renamed) + ", val_errs: " + str(val_err))
