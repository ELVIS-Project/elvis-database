import os
from music21 import *
import sys
import subprocess
from log import logger


def convert_xml_into_midi():
    logger.info("monitor running")
    flog = open('./downloaded_files/xml_to_midi_log.txt', 'w')
    for id, fn in enumerate(os.listdir('./downloaded_files/')):
        if (fn[-3:] != 'xml'):
            continue  # only convert xml into midi
        print(fn)
        try:
            s = converter.parse('./downloaded_files/' + fn)
            s.write('midi', fp = fn + '.midi')
        except:
            print(fn, file=flog)
            print(sys.exc_info()[0], file=flog)


def extract_features():
    #sys.stdout = open('./downloaded_files_extracted_features/extract_features_log.txt', 'w')
    for id, fn in enumerate(os.listdir('./downloaded_files/')):
        if(fn[-3:] == 'xml'):
            continue  # skip xml at this point
        else:
            os.system('java -Xmx3072m -jar /Users/yaolongju/Downloads/jMIR_3_0_developer/jSymbolic2/dist/jSymbolic2.jar -configrun jSymbolicDefaultConfigs.txt ./downloaded_files/' + fn +
                      ' ./downloaded_files_extracted_features/' + fn + '_feature_values.xml'
                      ' ./downloaded_files_extracted_features/' + fn + '_feature_descriptions.xml' )


if __name__ == "__main__":
    extract_features()
    #convert_xml_into_midi()