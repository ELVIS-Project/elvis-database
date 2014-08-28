from django.contrib import admin
import shutil, os

from elvis import settings

from elvis.models.project import Project
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.models.tag import Tag
from elvis.models.tag_hierarchy import TagHierarchy
from elvis.models.attachment import Attachment
from elvis.models.movement import Movement
from elvis.models.userprofile import UserProfile
from elvis.models.download import Download
from elvis.models.collection import Collection

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


class ProjectAdmin(admin.ModelAdmin):
    pass
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class PieceAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "date_of_composition", "number_of_voices", "uploader", "old_id", "piece_collections", "piece_genres", "piece_instruments_voices", "piece_languages", "piece_locations", "piece_sources")
    # Other things for interest: , "attached_files", "tagged_as"
    filter_horizontal = ("tags",)
    readonly_fields = ("attachments",)
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class MovementAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "date_of_composition", "number_of_voices", "uploader", "old_id", "piece", "movement_collections", "movement_genres", "movement_instruments_voices", "movement_languages", "movement_locations", "movement_sources")
    # Other things for interest , "attached_files", "tagged_as"
    filter_horizontal = ("tags",)
    readonly_fields = ("attachments",)
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class CollectionAdmin(admin.ModelAdmin):
    #pass
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall

class ComposerAdmin(admin.ModelAdmin):
    list_display = ("name", "birth_date", "death_date")
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "old_id")
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class TagHierarchyAdmin(admin.ModelAdmin):
    list_display = ("tag", "parent")
    actions = [reindex_in_solr, delete_in_solr]
    list_per_page = listperpage
    list_max_show_all = listmaxshowall


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('attachment', 'description', 'pk', 'attached_to', 'file_name')
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
    #pass
    #actions = [reindex_in_solr, delete_in_solr]

    


admin.site.register(Download, DownloadAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(TagHierarchy, TagHierarchyAdmin)
admin.site.register(Piece, PieceAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Composer, ComposerAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Movement, MovementAdmin)
