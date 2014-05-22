from django.contrib import admin

from elvis.models.project import Project
from elvis.models.piece import Piece
from elvis.models.corpus import Corpus
from elvis.models.composer import Composer
from elvis.models.tag import Tag
from elvis.models.tag_hierarchy import TagHierarchy
from elvis.models.attachment import Attachment
from elvis.models.movement import Movement
from elvis.models.userprofile import UserProfile
from elvis.models.download import Download


# LM: Wouldn't want to accidentally click on delete selected from django and have to re-drupal_dump everything... again...
admin.site.disable_action('delete_selected')

# method for admin reindex all entries to solr
def reindex_in_solr(modeladmin, request, queryset):
    for item in queryset:
        item.save()

reindex_in_solr.short_description = "Reindex selected in Solr"


# see above, delete all entries in solr
def delete_in_solr(modeladmin, request, queryset):
    for item in queryset:
        item.delete()

delete_in_solr.short_description = "Delete selected in Solr"

# summary of available actions: actions = [reindex_in_solr, delete_in_solr]


class DownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'created')
    filter_horizontal = ( 'attachments',)

class UserProfileAdmin(admin.ModelAdmin):
    pass
    actions = [reindex_in_solr, delete_in_solr]

class ProjectAdmin(admin.ModelAdmin):
    pass
    actions = [reindex_in_solr, delete_in_solr]

class PieceAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "date_of_composition", "number_of_voices", "uploader", "old_id", "corpus")
    filter_horizontal = ("tags",)
    readonly_fields = ("attachments",)
    actions = [reindex_in_solr, delete_in_solr]


class MovementAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "date_of_composition", "number_of_voices", "uploader", "old_id", "piece", "corpus")
    filter_horizontal = ("tags",)
    readonly_fields = ("attachments",)
    actions = [reindex_in_solr, delete_in_solr]

class CorpusAdmin(admin.ModelAdmin):
    pass
    actions = [reindex_in_solr, delete_in_solr]

class ComposerAdmin(admin.ModelAdmin):
    list_display = ("name", "birth_date", "death_date")
    actions = [reindex_in_solr, delete_in_solr]


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "old_id")
    actions = [reindex_in_solr, delete_in_solr]


class TagHierarchyAdmin(admin.ModelAdmin):
    list_display = ("tag", "parent")
    actions = [reindex_in_solr, delete_in_solr]


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('attachment', 'description', 'pk')
    #actions = ['delete_selected',]
    #pass
    #actions = [reindex_in_solr, delete_in_solr]

    


admin.site.register(Download, DownloadAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(TagHierarchy, TagHierarchyAdmin)
admin.site.register(Piece, PieceAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Corpus, CorpusAdmin)
admin.site.register(Composer, ComposerAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Movement, MovementAdmin)
