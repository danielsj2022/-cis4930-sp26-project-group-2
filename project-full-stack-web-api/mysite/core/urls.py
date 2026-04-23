from django.urls import path
from . import views
from core.views import RecordListView, RecordDetailView


urlpatterns = [
    path("", views.home, name = "home"),
    path("records/", RecordListView.as_view(), name = "records"),
    path("records/<int:pk>/", RecordDetailView.as_view(), name = "record_detail"),

    path("records/add/", views.create_record, name = "create_record"),
    path("records/<int:pk>/edit/", views.update_record, name = "record_edit"),
    path("records/<int:pk>/delete/", views.delete_record, name = "record_delete"),

    path("analytics/", views.analytics, name="analytics"),
    path("fetch/", views.fetch_weather, name="fetch_weather"),
    path('analytics/', views.analytics, name='analytics'),
    path('fetch/', views.fetch_weather, name='fetch_weather'),
]
