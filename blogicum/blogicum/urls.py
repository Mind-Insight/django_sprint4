from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("pages/", include("pages.urls")),
    path("", include("blog.urls")),
    path(
        "auth/registration/",
        CreateView.as_view(
            template_name="registration/registration_form.html",
            form_class=UserCreationForm,
            success_url=reverse_lazy("login"),
        ),
        name="registration",
    ),
    path("auth/", include("django.contrib.auth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "pages.views.page_not_found"
handler500 = "pages.views.server_error"
