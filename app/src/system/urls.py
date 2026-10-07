from django.urls import path

from .views.DashboardTempView import DashboardTempView
from .views.ErrorLogListView import ErrorLogListView
from .views.ErrorLogDetailView import ErrorLogDetailView
from .views.ErrorLogResolveRedView import ErrorLogResolveRedView
from .views.EmailLogListView import EmailLogListView
from .views.EmailTestRedView import EmailTestRedView
from .views.ConnectedUsersTempView import (
    ConnectedUsersTempView, ConnectedUsersJsonView
)
from .views.SessionHistoryListView import SessionHistoryListView
from .views.SessionCloseRedView import SessionCloseRedView
from .views.RoleListView import RoleListView
from .views.RoleDeleteRedView import RoleDeleteRedView
from .views.RolePermissionsUpdtView import RolePermissionsUpdtView
from .views.UserPermissionsListView import UserPermissionsListView
from .views.UserPermissionsUpdtView import UserPermissionsUpdtView


app_name = 'system'

urlpatterns = [
    path('', DashboardTempView.as_view(), name='dashboard'),
    path('errors/', ErrorLogListView.as_view(), name='error_list'),
    path('errors/<int:pk>/', ErrorLogDetailView.as_view(), name='error_detail'),
    path('errors/<int:pk>/resolve/', ErrorLogResolveRedView.as_view(), name='error_resolve'),
    path('emails/', EmailLogListView.as_view(), name='email_list'),
    path('emails/test/', EmailTestRedView.as_view(), name='email_test'),
    path('sessions/', ConnectedUsersTempView.as_view(), name='connected_users'),
    path('sessions/data/', ConnectedUsersJsonView.as_view(), name='connected_users_data'),
    path('sessions/history/', SessionHistoryListView.as_view(), name='session_history'),
    path('sessions/<int:pk>/close/', SessionCloseRedView.as_view(), name='session_close'),
    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/<int:pk>/', RolePermissionsUpdtView.as_view(), name='role_permissions'),
    path('roles/<int:pk>/delete/', RoleDeleteRedView.as_view(), name='role_delete'),
    path('users/', UserPermissionsListView.as_view(), name='user_permissions_list'),
    path('users/<int:pk>/', UserPermissionsUpdtView.as_view(), name='user_permissions'),
]
