import os

def validation(rngpath):
    if os.path.exists('./downloaded_files/MEI/') is False:
        os.mkdir('./downloaded_files/MEI/')
    for id, fn in enumerate(os.listdir('./downloaded_files/MEI/')):
        print(fn)
        print('xmllint --noout --relaxng ' + rngpath +
                       ' ./downloaded_files/MEI/' + fn +
              '>> ./downloaded_files/MEI/validation_log.txt 2>> ./downloaded_files/MEI/validation_error_log.txt')
        if (fn[-3:] == 'mei'):
            os.system('xmllint --noout --relaxng ' + rngpath
                      + ' ./downloaded_files/MEI/' + fn + '>> ./downloaded_files/MEI/validation_log.txt 2>> ./downloaded_files/MEI/validation_error_log.txt')


if __name__ == "__main__":
    #rng_path = input('please input the schema file you want to validate the MEI files')
    rng_path = '/Users/yaolongju/Documents/Projects/mei-all.rng'
    validation(rng_path)