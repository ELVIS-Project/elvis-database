from django.db import models


class TagHierarchy(models.Model):
    tag = models.ForeignKey("elvis.Tag", related_name="in_hierarchy")
    parent = models.ForeignKey("elvis.Tag", related_name="has_hierarchy", blank=True, null=True)

    def __unicode__(self):
        if self.parent:
            return u"{0}:{1}".format(self.parent.name, self.tag.name)
        else:
            return u"NO-PARENT:{0}".format(self.tag.name)

    class Meta:
        app_label = "elvis"
        verbose_name_plural = "Tag Hierarchies"
