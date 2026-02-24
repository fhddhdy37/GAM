from django import forms
from django.conf import settings

from .models import StorageFolder, StorageItem


class FileUploadForm(forms.ModelForm):
    folder = forms.ModelChoiceField(
        queryset=StorageFolder.objects.none(),
        required=False,
        label="저장 위치",
    )

    def __init__(self, owner=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        self.fields["file"].widget.attrs.update(
            {"class": "gambox-input", "accept": "*/*"}
        )
        queryset = StorageFolder.objects.filter(owner=owner) if owner else StorageFolder.objects.none()
        self.fields["folder"].queryset = queryset
        self.fields["folder"].widget.attrs.update({"class": "gambox-input"})
        self.fields["folder"].empty_label = "루트 폴더"

    class Meta:
        model = StorageItem
        fields = ["file", "note", "folder"]
        widgets = {
            "note": forms.TextInput(
                attrs={
                    "placeholder": "파일에 대한 간단한 메모 (선택)",
                    "class": "gambox-input",
                }
            )
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")
        if not uploaded_file:
            return uploaded_file

        max_gb = getattr(settings, "GAMBOX_MAX_FILE_SIZE_GB", 1)
        max_bytes = max_gb * 1024 * 1024 * 1024
        if uploaded_file.size > max_bytes:
            raise forms.ValidationError(
                f"파일 최대 크기 {max_gb}GB를 초과했습니다."
            )
        return uploaded_file

    def save(self, owner=None, commit=True):
        instance = super().save(commit=False)
        instance.owner = owner or self.owner
        if commit:
            instance.save()
        return instance


class FolderForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=StorageFolder.objects.none(),
        required=False,
        label="상위 폴더",
    )

    class Meta:
        model = StorageFolder
        fields = ["name", "parent"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "새 폴더 이름",
                    "class": "gambox-input",
                }
            )
        }

    def __init__(self, owner=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        queryset = StorageFolder.objects.filter(owner=owner) if owner else StorageFolder.objects.none()
        self.fields["parent"].queryset = queryset
        self.fields["parent"].widget.attrs.update({"class": "gambox-input"})

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("폴더 이름을 입력하세요.")
        if any(sep in name for sep in ("/", "\\")):
            raise forms.ValidationError("폴더 이름에는 / 또는 \\ 문자를 사용할 수 없습니다.")
        return name

    def save(self, owner=None, commit=True):
        folder = super().save(commit=False)
        folder.owner = owner or self.owner
        if commit:
            folder.save()
        return folder
