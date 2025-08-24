from django.urls import path
from .views.LoginTempView import LoginTempView
from .views.LoguoutRedView import LogoutRedView
from .views.ProfileTempView import ProfileTempView
from .views.ProfileUpdtView import ProfileUpdtView
from .views.ChangePassUpdtView import ChangePassUpdtView


app_name = 'accounts'

urlpatterns = [
    path('login/', LoginTempView.as_view(), name='login'),
    path('logout/', LogoutRedView.as_view(), name='logout'),
    path('profile/', ProfileTempView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdtView.as_view(), name='profile_edit'),
    path('profile/change-password/', ChangePassUpdtView.as_view(),name='change_password')
]
