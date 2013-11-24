from django.db import models


class TagHierarchy(models.Model):
    tag = models.ForeignKey("elvis.Tag", related_name="in_hierarchy")
    parent = models.ForeignKey("elvis.Tag", related_name="has_hierarchy", blank=True, null=True)

    def __unicode__(self):
    	parent = self.parent.name if self.parent else ""
        return u"{0}:{1}".format(self.tag.name, parent)

    class Meta:
        app_label = "elvis"
        verbose_name_plural = "Tag Hierarchies"
