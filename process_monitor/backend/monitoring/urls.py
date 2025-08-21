from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    # API endpoints
    path('api/hosts/', views.HostListView.as_view(), name='host-list'),
    path('api/hosts/<str:hostname>/snapshots/', views.ProcessSnapshotListView.as_view(), name='host-snapshots'),
    path('api/hosts/<str:hostname>/latest/', views.LatestProcessesView.as_view(), name='host-latest'),
    path('api/hosts/<str:hostname>/processes/', views.get_process_tree, name='process-tree'),
    path('api/hosts/<str:hostname>/resources/', views.get_system_resources, name='system-resources'),
    path('api/submit/', views.submit_process_data, name='submit-data'),
    
    # Frontend
    path('', views.frontend_view, name='frontend'),
] 