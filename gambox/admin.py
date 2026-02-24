from django.contrib import admin

from .models import StorageFolder, StorageItem


@admin.register(StorageFolder)
class StorageFolderAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "parent", "created_at")
    search_fields = ("name", "owner__username")
    list_filter = ("created_at",)


@admin.register(StorageItem)
class StorageItemAdmin(admin.ModelAdmin):
    list_display = ("filename", "owner", "folder", "size", "uploaded_at")
    search_fields = ("original_name", "note", "owner__username")
    list_filter = ("uploaded_at", "folder")
