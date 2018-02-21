ELVIS Database
==========

The Django Elvis Web Application

## Overview
Welcome to the ELVIS Django database of symbolic music. This application is intended to allow for _uploading_, _searching_, and _downloading_ symbolic music files for use in music analysis frameworks, such as the VIS Web App.

## Structure
Models in the Django app include composers, movements, collections, and many more. Here are some comments on what some of these models are meant for:
+ The _attachment_ model contains files associated with each piece or movement of music. A movement may have multiple attachments if its been transcribed by different people.
+ The _collection_ model is to be used for keeping or sharing sets of pieces/movements that are of particular interest. These collections used to be called corpora but were since renamed.
+ The _download_ model is a "shopping cart" of attachments associated with each user. A user would query the database for pieces/movements, add relevant attachments to their downloads "cart", and "checkout" the files by downloading them when needed. This was vaguely inspired by online shopping sites.
+ The _genre_, _instrumentation_, _language_, _location_, and _source_ models will enhance the old tagging system. Pieces/movements will be tagged with particular instances of these models for easy searching and to structure the metadata associated with the musical content. 

## Dependencies
We plug the Django app into Apache Solr to speed up text-based searches and to allow for queries with complex logical structure. It lets us use a faceted search UI as well. We also use Celery with Rabbitmq as broker to coordinate downloading. At checkout, attachments in a cart is zipped into a temporary file and served via a call to a Celery job. A Celery beat job periodically cleans out the zipped files after they've been downloaded.

## Deployment
A deployment guide is including in the docs of this repository with details as to how we deployed the database on Fedora 19.

## Future Directions
See GitHub issues.

## Content Related Issues
Please file content related issues at [https://github.com/ELVIS-Project/ELVIS-Database-Content](https://github.com/ELVIS-Project/ELVIS-Database-Content) (i.e. your Palestrina Mass is actually by Lassus).

## Extracting the features for the all symbolic files on ELVIS
This section contains three parts: (1) Downloading all the files from ELVIS (`download_files.py`) (2) Extracting features from the downloaded files (`feature_extraction_jsymbolic2.py`) (3) Upload all the feature files to ELVIS.

The scripts are fully test and run on masOS Sierra, version of 10.12.5. All required packages are specified in `requirements.txt`. You can install all the required packages in the terminal with `pip install -r [the path where you store requirements.txt]`, except for `pymei` which will be addressed in Section 3. 

All output of any executed step, including `stdout` and `stderr`, will be recorded into a log file, which will be explained in the last paragraph of each step. 

### Download files using 'download_files.py'

First, run `download_files.py` to get all the symbolic files from ELVIS database. To do this, you need to (1) First create an account on [ELVIS database](https://database.elvisproject.ca), then provide your username and password when running the script. An example would be: `python3 [the path of your script] [your username] [your password]`. (2) In your working directory where the script is stored, a folder called `downloaded_files` will be created, and this is the place where all the downloaded files will be saved. (3) Run the script to download all the files. When running the script, it will download all the symbolic files with `.mid`, `.midi`, `.mei` and `.xml` (musicxml) extensions. `.midi` and `.mid` files will be stored under `./downloaded_files/` directory, and `.mei` will be stored under `./downloaded_files/MEI/` directory, and `.xml` will stored under `./downloaded_files/XML/` directory. 

A log file, which records all the files that cannot be downloaded, is stored under `./downloaded_files/` directory, called `download_log.txt`. There is only one file which cannot be downloaded.

### Extracting features using 'feature_extraction_jsymbolic2.py'

`feature_extraction_jsymbolic2.py` has several functions to run in order to extract features properly from all the downloaded files, and each of them will be explained as follows. To run the script, just simply type `python3 [the path of your script]`.

#### 1.Converting XML into MIDI

Now, it is time to run `feature_extraction_jsymbolic2.py`. The script will ask you to provide the path you use to store jsymbolic jar file. Afterward, the script will first convert all xml files to midi using music21, and stored `.midi` files under `./downloaded_files/XML/MIDI/` directory.

A log file, which records all the files that cannot be converted, is stored under `./downloaded_files/XML/MIDI/` directory, called `xml_to_midi_log.txt`. There are 4/872 files which cannot be processed.

#### 2.Validating MEI files

At the same time, we are concerned that are those MEI file valid or not. The script runs `validation` function, where you have to specify the schemata file you use (the default file path will probably fail to work). To find a schemata file, there are several versions: [3.0.0](http://www.music-encoding.org/schema/current/mei-all.rng), [2013](http://music-encoding.org/schema/2.1.1/mei-all.rng), [2012 (it is a zip file, so you need to unzip it and use the `rng` file inside of it)](https://music-encoding.googlecode.com/files/MEI2012_v2.0.0.zip), [2011-05](http://music-encoding.org/wp-content/uploads/2015/04/MEI2011-05.zip), [2010-05](http://music-encoding.org/wp-content/uploads/2015/04/MEI2010-05.rng_.zip).

Since most of the MEI files from ELVIS uses `2011-05`, and since the schemata file does not support backward compatibility, using `2011-05` schemata file will be the optimal choice. If you want to validate a file from the terminal, simply run `xmllint --noout --relaxng [the path of the schemata file] [the path of the file you want to validate]`. FYI, you can also convert the old MEI file into the newer one using the [tool](https://github.com/music-encoding/encoding-tools).  

Two log files, which record all the files that cannot be converted, are stored under `./downloaded_files/MEI/` directory, called `validation_error_log.txt` and `validation_log.txt`. Surprisingly enough, none of the MEI files validates. There are 378 MEI files, none of them validates.

#### 3.Converting MEI into a version which jsymbolic2 can parse

Second, the script uses jsymbolic2 to extract features. Note that jsymbolic2 now can only extract features from valid `.mid`, `.midi` and `.mei` files. However, many `.mei` files on ELVIS database are not parsable by jsymbolic, since many of them use `breve` value as duration which is not supported by jsymbolic.

Third, in order to extract features from these `.mei` files, the script runs `modifying_MEI` function automatically. This function uses `pymei`, which is a library to create and modify `.mei` files. In order to install `pymei`, please follow the instructions [here](https://github.com/DDMAL/libmei/wiki). After installing `pymei`, you need to add the path where you install `pymei` to the script. Please see the line 2 of the script, this is an example of where my `pymei` is stored. Just replace with the path you use to store `pymei`. 

`modifying_MEI` function will find all the `.mei` files in the `./downloaded_files/MEI` folder, where the downloaded files are stored, and modify the `.mei` files which have `breve` value. The script will create a new `.mei` file, appending `NEW` to the end of file name, and these files can be parsed by jsymbolic2 now (Unfortunately, some of them still cannot be parsed, but we will deal with them later), and these files will be stored under the directory of `./downloaded_files/MEI/NEW`. 

#### 4. Extracting features from all symbolic files

After this, the script will extract features from all `.mid` and `.midi` files which are stored under `downloaded_files`, and all the `.midi` files from `downloaded_files/XML/MIDI`, which are converted from `.xml` files, and all `.mei` files which are stored under `downloaded_files/MEI/NEW`. The extracted feature will be stored under the directories of `downloaded_files/extracted_features`, `downloaded_files/XML/MIDI/extracted_features`, and `downloaded_files/MEI/NEW/extracted_features`, respectively.

In each folder, there are two log files: `extract_features_log.txt` and `extract_features_error_log.txt`, which records `stdout` and `stderr` of the feature extraction command.

##### Summary

There are 378 MEI files, 158 can manage to extract features; there are 4210 midi files, 4206 can manage to extract features; there are 872 MusicXML files, 868 manage to convert; 868 manage to extract features (These statistics are derived from all the error log files mentioned above). 
 
There are altogether 5460 symbolic files, downloaded from ELVIS database. 5232 managed to extract features.

#### 5. Converting MEI into midi

Since 220/378 of the `.mei` files still cannot be processed by jsymbolic2 to extract features, we are going to try to convert them into midi using music21, by calling `convert_MEI_into_midi` function. Unfortunately, none of them can be converted into midi and extract features. You can find the name of these 220 files under `./downloaded_files/MEI/NEW/extracted_features/` folder, and `extract_features_error_log.txt` file. 

After this step, all the files are extracted, and they are ready to upload to ELVIS database (to be continued).

#### NOTES

When running `feature_extraction_jsymbolic2.py`, the script will ask you to provide the paths of (1) Jsymbolic `.jar` file. This file exist in a zip file of jsymbolic, which can be downloaded from [here](https://sourceforge.net/projects/jmir/files/jSymbolic/jSymbolic%202.0/). Download `jSymbolic_2_0_developer.zip`, unzip the file, and the `.jar` file is located in `/jSymbolic_2_0_developer/jSymbolic2/dist/jSymbolic2.jar`. (2) Jsymbolic config file, which directs jsymbolic what kind of features to extract. It can be downloaded from [here](https://www.dropbox.com/s/cl4vyp516jh6p4h/jSymbolicDefaultConfigs.txt?dl=0). (3) MEI schemata file to validate MEI files, which can be downloaded from [3.0.0](http://www.music-encoding.org/schema/current/mei-all.rng).
