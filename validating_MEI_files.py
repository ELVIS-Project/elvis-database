import os
import os.path
def validation(rngpath, meipath):
    for dirpath, dirnames, filenames in os.walk(meipath):
        for filename in [f for f in filenames if f.endswith(".mei")]:  # find all MEI files in the current folder and subfolders
            print
            os.path.join(dirpath, filename)
            print('xmllint --noout --relaxng ' + rngpath + ' ' +
                  os.path.join(dirpath, filename) +
                  '>> ./downloaded_files/MEI/validation_log.txt 2>> ./downloaded_files/MEI/validation_error_log.txt')
            os.system('xmllint --noout --relaxng ' + rngpath + ' ' +
                  os.path.join(dirpath, filename) +
                  '>> ./downloaded_files/MEI/validation_log.txt 2>> ./downloaded_files/MEI/validation_error_log.txt')

if __name__ == "__main__":
    #rng_path = input('please input the schema file you want to validate the MEI files')
    rng_path = './MEI_schemata_files/mei-all.rng'
    #mei_path = './downloaded_files/MEI/'
    mei_path = '/Users/yaolongju/Documents/Projects/mei-test-set/MEI-test-set'
    validation(rng_path, mei_path)