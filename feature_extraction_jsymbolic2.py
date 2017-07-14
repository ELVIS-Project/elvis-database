import os
from music21 import *
import sys
import subprocess
from log import logger
from contextlib import redirect_stderr


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
    #sys.stderr = open('./downloaded_files_extracted_features/extract_features_log.txt', 'w')
    #with open('./downloaded_files_extracted_features/extract_features_log.txt', 'w') as sys.stderr, redirect_stderr(sys.stderr):
        for id, fn in enumerate(os.listdir('./downloaded_files/')):
        #for id, fn in enumerate(os.listdir('./downloaded_files/xml_to_midi/')):
            if(fn.find('NEW') == -1):
                continue
            if(fn[-3:] == 'xml'):
                continue  # skip xml at this point
            else:
                print(fn)
                os.system('java -Xmx3072m -jar /Users/yaolongju/Downloads/jMIR_3_0_developer/jSymbolic2/dist/jSymbolic2.jar -configrun jSymbolicDefaultConfigs.txt ./downloaded_files/' + fn +
                          ' ./downloaded_files_extracted_features/NEW_MEI/' + fn + '_feature_values.xml'
                          ' ./downloaded_files_extracted_features/NEW_MEI/' + fn + '_feature_descriptions.xml >> ./downloaded_files_extracted_features/NEW_MEI/extract_features_log.txt 2>> ./downloaded_files_extracted_features/NEW_MEI/extract_features_error_log.txt' )
                #os.system(
                    #'java -Xmx3072m -jar /Users/yaolongju/Downloads/jMIR_3_0_developer/jSymbolic2/dist/jSymbolic2.jar -configrun jSymbolicDefaultConfigs.txt ./downloaded_files/xml_to_midi/' + fn +
                    #' ./downloaded_files_extracted_features/xml_to_midi/' + fn + '_feature_values.xml'
                    #' ./downloaded_files_extracted_features/xml_to_midi/' + fn + '_feature_descriptions.xml ')#>> '
                                                                                # './downloaded_files_extracted_features/xml_to_midi/extract_features_log.txt 2 >> ./downloaded_files_extracted_features/xml_to_midi/extract_features_error_log.txt')


if __name__ == "__main__":
    extract_features()
    #convert_xml_into_midi()