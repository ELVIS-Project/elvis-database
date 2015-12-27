
1. Fix templates. Movements/pieces are largely broken by new serializers.
2. Fix download buttons. The JS buttons are working, but the HTML buttons
   are still checking the user download, rather than the session.
3. Add uuid field to all models, so they can be identified easily. Would
   also be good to refactor solr so that the solr primary key is 
   called UUID and corresponds to the UUID in the database.
4. Rewrite zipping view/script. With a dict of ID's instead of the list
   of attachments, it should be much easier to implement directories
   and metadata files in the zip (also, real progress bar using the 
   celery meta like on misirlou would be sweet).
   
Once the above are done, it would make sense to write better unit
tests, and brainstorm/prioritize new feature additions.