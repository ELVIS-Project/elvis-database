from django.contrib import admin
from django.conf import settings
import shutil
import os

from elvis.elvis.tasks import rebuild_suggester_dicts
from elvis.models import Piece
from elvis.models import Composer
from elvis.models import Tag
from elvis.models import Attachment
from elvis.models import Movement
from elvis.models import Download
from elvis.models import Collection
from elvis.models import Genre
from elvis.models import InstrumentVoice
from elvis.models import Language
from elvis.models import Place
from elvis.models import Source

# summary of available actions: actions = [reindex_in_solr, delete_in_solr]

# LM: Wouldn't want to accidentally click on delete selected from django and have to re-drupal_dump everything... again...
admin.site.disable_action('delete_selected')

# method for admin reindex all entries to solr
def reindex_in_solr(modeladmin, request, queryset):
    for item in queryset:
        item.save()

reindex_in_solr.short_description = "Reindex selected in Solr"


# IMPORTANT: Misnomer - this actually deletes item from both Django AND Solr.... TODO Write method for solr deletion only
def delete_in_solr(modeladmin, request, queryset):
    for item in queryset:
        item.delete()
    rebuild_suggester_dicts.delay()

delete_in_solr.short_description = "Permanently delete selected"

# Items for each page / show all
listperpage = 200
listmaxshowall = 800


class DownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'created')
    filter_horizontal = ( 'attachments',)
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class UserProfileAdmin(admin.ModelAdmin):
    pass
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class PieceAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "uploader", "created", "updated")
    # Other things for interest: , "attached_files", "tagged_as"
    filter_horizontal = ("tags",)
    readonly_fields = ("attachments",)
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class MovementAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "uploader", "created", "updated")
    # Other things for interest , "attached_files", "tagged_as"
    filter_horizontal = ("tags",)
    readonly_fields = ("attachments",)
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class CollectionAdmin(admin.ModelAdmin):
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class ComposerAdmin(admin.ModelAdmin):
    list_display = ("title",)
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class TagAdmin(admin.ModelAdmin):
    list_display = ("title",)
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class TagHierarchyAdmin(admin.ModelAdmin):
    list_display = ("tag", "parent")
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('attachment', 'pk', 'attached_to', 'file_name')
    actions = [delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall

    # LM For some reason simply using the model deleter for querysets doesn't work correctly, so this is a solution.

    def delete_attachments_filesys(modeladmin, request, queryset):
        def attachment_path(item):
            try:
                return os.path.join(settings.MEDIA_ROOT,
                                    "attachments",
                                    "{0:0>2}".format(str(item.pk)[0:2]),
                                    "{0:0>2}".format(str(item.pk)[-2:]),
                                    "{0:0>15}".format(item.pk))
            except AttributeError:
                return os.path.join("attachments",
                                    "{0:0>2}".format(str(item.pk)[0:2]),
                                    "{0:0>2}".format(str(item.pk)[-2:]),
                                    "{0:0>15}".format(item.pk))
        for item in queryset:
            if os.path.exists(attachment_path(item)):
                shutil.rmtree(attachment_path(item))
                item.delete()
            else:
                print('Delete failure')

    delete_attachments_filesys.short_description = "Delete attachments from File System"


class GenericAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'updated')
    actions = [delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


admin.site.register(Download, DownloadAdmin)
admin.site.register(Piece, PieceAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Composer, ComposerAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Movement, MovementAdmin)
admin.site.register(Place, GenericAdmin)
admin.site.register(Genre, GenericAdmin)
admin.site.register(InstrumentVoice, GenericAdmin)
admin.site.register(Language, GenericAdmin)
admin.site.register(Source, GenericAdmin)
