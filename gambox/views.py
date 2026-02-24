from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from .forms import FileUploadForm, FolderForm
from .models import StorageFolder, StorageItem


class StorageDashboardView(LoginRequiredMixin, FormView):
    form_class = FileUploadForm
    template_name = "gambox/dashboard.html"
    success_url = reverse_lazy("gambox:dashboard")

    def dispatch(self, request, *args, **kwargs):
        self.current_folder = self.get_current_folder()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if self.current_folder:
            initial["folder"] = self.current_folder
        return initial

    def get_success_url(self):
        if self.current_folder:
            return f"{reverse_lazy('gambox:dashboard')}?folder={self.current_folder.id}"
        return super().get_success_url()

    def get_current_folder(self):
        folder_id = self.request.GET.get("folder") or self.request.POST.get("folder")
        if not folder_id:
            return None
        try:
            return StorageFolder.objects.get(id=folder_id, owner=self.request.user)
        except StorageFolder.DoesNotExist:
            return None

    def get_quota_gb(self):
        return getattr(settings, "GAMBOX_STORAGE_QUOTA_GB", 10)

    def get_quota_bytes(self):
        quota_gb = self.get_quota_gb()
        return quota_gb * 1024 * 1024 * 1024 if quota_gb else 0

    def get_user_files(self):
        files = StorageItem.objects.filter(owner=self.request.user)
        if self.current_folder:
            files = files.filter(folder=self.current_folder)
        else:
            files = files.filter(folder__isnull=True)
        return files

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        files = self.get_user_files()
        all_files_qs = StorageItem.objects.filter(owner=self.request.user)
        total_bytes = all_files_qs.aggregate(total=Sum("size"))["total"] or 0
        total_count = all_files_qs.count()
        quota_gb = self.get_quota_gb()
        quota_bytes = self.get_quota_bytes()
        percent = (
            min(100, round((total_bytes / quota_bytes) * 100, 1)) if quota_bytes else 0
        )

        folders = StorageFolder.objects.filter(
            owner=self.request.user, parent=self.current_folder
        )
        breadcrumbs = self.build_breadcrumbs()

        context.update(
            {
                "files": files,
                "folders": folders,
                "current_folder": self.current_folder,
                "breadcrumbs": breadcrumbs,
                "folder_form": FolderForm(owner=self.request.user, initial={"parent": self.current_folder}),
                "usage": {
                    "bytes": total_bytes,
                    "quota_bytes": quota_bytes,
                    "quota_gb": quota_gb,
                    "percent": percent,
                    "file_count": total_count,
                },
                "max_file_size_gb": getattr(settings, "GAMBOX_MAX_FILE_SIZE_GB", 1),
            }
        )
        return context

    def build_breadcrumbs(self):
        crumbs = []
        folder = self.current_folder
        while folder:
            crumbs.append(folder)
            folder = folder.parent
        return list(reversed(crumbs))

    def form_valid(self, form):
        total_bytes = (
            StorageItem.objects.filter(owner=self.request.user).aggregate(total=Sum("size"))[
                "total"
            ]
            or 0
        )
        quota_bytes = self.get_quota_bytes()
        new_file = form.cleaned_data["file"]

        if quota_bytes and total_bytes + new_file.size > quota_bytes:
            form.add_error(
                "file",
                "남은 저장 용량이 부족합니다. 기존 파일을 정리하거나 관리자에게 문의하세요.",
            )
            return self.form_invalid(form)

        storage_item = form.save(owner=self.request.user)
        messages.success(self.request, f"'{storage_item.filename}' 업로드 완료")
        return super().form_valid(form)


class DownloadStorageItemView(LoginRequiredMixin, View):
    def get(self, request, pk):
        item = get_object_or_404(StorageItem, pk=pk, owner=request.user)
        if not item.file:
            raise Http404("파일을 찾을 수 없습니다.")
        response = FileResponse(
            item.file.open("rb"),
            as_attachment=True,
            filename=item.filename,
        )
        return response


class DeleteStorageItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(StorageItem, pk=pk, owner=request.user)
        filename = item.filename
        item.file.delete(save=False)
        item.delete()
        messages.info(request, f"'{filename}' 파일을 삭제했습니다.")
        redirect_url = reverse_lazy("gambox:dashboard")
        folder_id = request.POST.get("current_folder")
        if folder_id:
            redirect_url = f"{redirect_url}?folder={folder_id}"
        return redirect(redirect_url)


class CreateFolderView(LoginRequiredMixin, View):
    def post(self, request):
        form = FolderForm(owner=request.user, data=request.POST)
        if form.is_valid():
            folder = form.save(owner=request.user)
            messages.success(request, f"폴더 '{folder.full_path}'가 생성되었습니다.")
        else:
            messages.error(request, "폴더 생성에 실패했습니다.")
        redirect_url = reverse_lazy("gambox:dashboard")
        target = (
            form.cleaned_data.get("parent")
            if form.is_valid()
            else request.POST.get("parent")
        )
        folder_id = target.id if hasattr(target, "id") else target
        if folder_id:
            redirect_url = f"{redirect_url}?folder={folder_id}"
        return redirect(redirect_url)


class LogoutView(View):
    """간단한 세션 로그아웃 핸들러"""

    redirect_to = getattr(settings, "LOGOUT_REDIRECT_URL", "index")

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return redirect(self.redirect_to)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class SignupView(View):
    template_name = "registration/signup.html"
    form_class = UserCreationForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("gambox:dashboard")
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("gambox:dashboard")
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "가입이 완료되었습니다. Gambox를 바로 이용할 수 있어요.")
            return redirect("gambox:dashboard")
        return render(request, self.template_name, {"form": form})
