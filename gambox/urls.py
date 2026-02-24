from django.urls import path

from .views import (
    CreateFolderView,
    DeleteStorageItemView,
    DownloadStorageItemView,
    StorageDashboardView,
)

app_name = "gambox"

urlpatterns = [
    path("", StorageDashboardView.as_view(), name="dashboard"),
    path("folders/create/", CreateFolderView.as_view(), name="folder-create"),
    path("files/<int:pk>/download/", DownloadStorageItemView.as_view(), name="download"),
    path("files/<int:pk>/delete/", DeleteStorageItemView.as_view(), name="delete"),
]
