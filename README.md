elvis-site
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