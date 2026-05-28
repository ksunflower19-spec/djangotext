from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = '나의 반려쓰레기 해방일지 — 관리자'
admin.site.site_title = '해방일지 관리'
admin.site.index_title = '관리 페이지'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('board/', include('noticeboard.urls')),
    path('', include('contents.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
