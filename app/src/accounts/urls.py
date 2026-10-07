from django.urls import path
from .views.LoginTempView import LoginTempView
from .views.LoguoutRedView import LogoutRedView
from .views.ProfileTempView import ProfileTempView
from .views.ProfileUpdtView import ProfileUpdtView
from .views.ChangePassUpdtView import ChangePassUpdtView
from .views.PasswordResetFormView import PasswordResetFormView
from .views.PasswordResetDoneTempView import PasswordResetDoneTempView
from .views.PasswordResetConfirmUpdtView import PasswordResetConfirmUpdtView
from .views.PasswordResetCompleteTempView import PasswordResetCompleteTempView


app_name = 'accounts'

urlpatterns = [
    path('login/', LoginTempView.as_view(), name='login'),
    path('logout/', LogoutRedView.as_view(), name='logout'),
    path('profile/', ProfileTempView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdtView.as_view(), name='profile_edit'),
    path('profile/change-password/', ChangePassUpdtView.as_view(),name='change_password'),
    path('password-reset/', PasswordResetFormView.as_view(), name='password_reset'),
    path('password-reset/sent/', PasswordResetDoneTempView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmUpdtView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteTempView.as_view(), name='password_reset_complete'),
]
