from django.db import models

class Query(models.Model):
    '''
        TODO: query should be re-query-able, so should store more than just a string 
    '''
    query = models.CharField(max_length=255)
    #user = models.ForeignKey(UserProfile)
    created = models.DateTimeField(auto_now_add=True, blank=True)

    def __unicode__(self):
        return u"{0}".format(self.query)

    class Meta:
        app_label = "elvis"
