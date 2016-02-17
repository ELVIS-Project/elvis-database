import os
import shutil
from django.conf import settings
from django.contrib import admin
from elvis.models import *
from elvis.tasks import rebuild_suggester_dicts
from django.contrib.contenttypes.admin import GenericTabularInline

# method for admin reindex all entries to solr
def reindex_in_solr(modeladmin, request, queryset):
    for item in queryset:
        item.save()

def rebuild_dicts(modeladmin, request):
    rebuild_suggester_dicts()

reindex_in_solr.short_description = "Reindex selected in Solr"


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
    actions = [reindex_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class PieceInline(admin.TabularInline):
    model = Collection.pieces.through

class PieceAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "uploader", "created")
    # Other things for interest: , "attached_files", "tagged_as"
    filter_horizontal = ("tags",)
    ordering = ("-created",)
    readonly_fields = ("attachments",)
    actions = [reindex_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class MovementAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "uploader", "created", "updated")
    # Other things for interest , "attached_files", "tagged_as"
    filter_horizontal = ("tags",)
    readonly_fields = ("attachments",)
    actions = [reindex_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class CollectionAdmin(admin.ModelAdmin):
    inlines = [PieceInline]
    actions = [reindex_in_solr]
    ordering = ("-created",)
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class ComposerAdmin(admin.ModelAdmin):
    list_display = ("title",)
    actions = [reindex_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class TagAdmin(admin.ModelAdmin):
    list_display = ("title",)
    actions = [reindex_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class TagHierarchyAdmin(admin.ModelAdmin):
    list_display = ("tag", "parent")
    actions = [reindex_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('attachment', 'pk', 'attached_to', 'file_name')
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
