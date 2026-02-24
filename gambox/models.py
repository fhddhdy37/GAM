import uuid
from pathlib import Path

from django.conf import settings
from django.db import models


def _folder_path_parts(folder):
    parts = []
    current = folder
    while current:
        parts.append(current.name)
        current = current.parent
    return list(reversed(parts))


def _owner_dir_name(owner):
    username = (owner.username or "").strip()
    safe = "".join("_" if ch in "/\\" else ch for ch in username)
    if not safe:
        safe = f"user_{owner.pk}"
    return safe


def _owner_storage_root(owner):
    return Path(settings.MEDIA_ROOT) / _owner_dir_name(owner)


def user_upload_path(instance, filename):
    """Store files under <username>/<folder...>/<uuid>_<filename> relative to MEDIA_ROOT."""
    safe_name = Path(filename).name
    path_parts = [_owner_dir_name(instance.owner)]
    if instance.folder:
        path_parts.extend(_folder_path_parts(instance.folder))
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    path_parts.append(unique_name)
    return "/".join(path_parts)


class StorageFolder(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gambox_folders",
    )
    name = models.CharField(max_length=80)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "parent", "name")
        ordering = ["name"]

    def __str__(self):
        return self.full_path

    @property
    def full_path(self):
        return "/".join(self.path_components)

    @property
    def path_components(self):
        return _folder_path_parts(self)

    def ensure_directory(self):
        target = _owner_storage_root(self.owner)
        for part in self.path_components:
            target /= part
        target.mkdir(parents=True, exist_ok=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ensure_directory()


class StorageItem(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gambox_files",
    )
    folder = models.ForeignKey(
        StorageFolder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="files",
    )
    file = models.FileField(upload_to=user_upload_path)
    original_name = models.CharField(max_length=255, blank=True)
    note = models.CharField(max_length=120, blank=True)
    size = models.PositiveBigIntegerField(default=0, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.filename} ({self.owner})"

    def save(self, *args, **kwargs):
        if self.file:
            self.original_name = self.original_name or Path(self.file.name).name
            try:
                self.size = self.file.size
            except Exception:
                pass
        # Ensure owner root directory exists
        base_dir = _owner_storage_root(self.owner)
        base_dir.mkdir(parents=True, exist_ok=True)
        if self.folder:
            self.folder.ensure_directory()
        super().save(*args, **kwargs)

    @property
    def filename(self):
        return self.original_name or Path(self.file.name).name
