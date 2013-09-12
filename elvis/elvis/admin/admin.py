from django.contrib import admin

from elvis.models.piece import Piece
from elvis.models.corpus import Corpus
from elvis.models.composer import Composer
from elvis.models.tag import Tag
from elvis.models.tag_hierarchy import TagHierarchy
from elvis.models.attachment import Attachment
from elvis.models.movement import Movement


class PieceAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "date_of_composition", "number_of_voices", "uploader", "old_id", "corpus")
    filter_horizontal = ("tags",)
    readonly_fields = ("attachments",)


class MovementAdmin(admin.ModelAdmin):
    list_display = ("title", "composer", "date_of_composition", "number_of_voices", "uploader", "old_id", "piece", "corpus")
    filter_horizontal = ("tags",)
    readonly_fields = ("attachments",)


class CorpusAdmin(admin.ModelAdmin):
    pass


class ComposerAdmin(admin.ModelAdmin):
    list_display = ("name", "birth_date", "death_date")


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "old_id")


class TagHierarchyAdmin(admin.ModelAdmin):
    list_display = ("tag", "parent")


class AttachmentAdmin(admin.ModelAdmin):
    pass

admin.site.register(TagHierarchy, TagHierarchyAdmin)
admin.site.register(Piece, PieceAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Corpus, CorpusAdmin)
admin.site.register(Composer, ComposerAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Movement, MovementAdmin)
