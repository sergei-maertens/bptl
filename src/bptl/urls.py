from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic.base import TemplateView

handler500 = "bptl.utils.views.server_error"
admin.site.site_header = "bptl admin"
admin.site.site_title = "bptl admin"
admin.site.index_title = "Welcome to the bptl admin"

urlpatterns = [
    path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path("admin/hijack/", include("hijack.urls")),
    path("admin/xential/", include("bptl.work_units.xential.admin_urls")),
    path("admin/", admin.site.urls),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("adfs/", include("django_auth_adfs.urls")),
    # Simply show the master template.
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("tasks/", include("bptl.dashboard.urls")),
    path("taskmappings/", include("bptl.tasks.urls")),
    path("api/", include("bptl.activiti.api.urls")),
    path("camunda/", include("bptl.camunda.urls")),
    path(
        "contrib/api/",
        include(
            [
                path("validsign/", include("bptl.work_units.valid_sign.urls")),
                path("xential/", include("bptl.work_units.xential.urls")),
            ]
        ),
    ),
]

# NOTE: The staticfiles_urlpatterns also discovers static files (ie. no need to run collectstatic). Both the static
# folder and the media folder are only served via Django if DEBUG = True.
urlpatterns += staticfiles_urlpatterns() + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG and apps.is_installed("debug_toolbar"):
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
