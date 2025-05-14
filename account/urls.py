from django.urls import path
from .apis import UserRegisterApi,UserLoginApi
from .apis import modifyPasswordApi,modifyEmailApi,modifyPhoneApi,modifyGenderApi,modifyNameApi,getUserInfoApi,AllUserNameApi,adminGetUserInfoApi
from .apis import Is_PasswordApi,ResetPasswordApi,checkphoneApi,AdminLoginApi,CreateInvitationCodeApi, ManageExperimentParticipantsApi,GetUserInfoByNameApi
from .apis import callDeepSeekApi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .apis import AdminUpdateProfileApi
urlpatterns = [
    path("register/", UserRegisterApi.as_view(), name="register"),
    path("login/", UserLoginApi.as_view(), name="Login"),
    path("token_obtain/", TokenObtainPairView.as_view(), name="obtain"),
    path("token_refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("token_verify/", TokenVerifyView.as_view(), name="verify"),
    path("isPassword/",Is_PasswordApi.as_view(),name="isPassword"),
    path("resetPassword/",ResetPasswordApi.as_view(),name="resetPassword"),
    path("modify/password/",modifyPasswordApi.as_view(),name="modifyPassword"),
    path("modify/email/",modifyEmailApi.as_view(),name="modifyEmail"),
    path("modify/phone_number/",modifyPhoneApi.as_view(),name="modifyPhone"),
    path("modify/gender/",modifyGenderApi.as_view(),name="modifyGender"),
    path("modify/name/",modifyNameApi.as_view(),name="modifyName"),
    path("getUserInfo/",getUserInfoApi.as_view(),name="getUserInfo"),
    path("checkphone/",checkphoneApi.as_view(),name="checkphone"),
    path("allUserName/",AllUserNameApi.as_view(),name="allUserName"),
    path("adminGetUserInfo/",adminGetUserInfoApi.as_view(),name="adminGetUserInfo"),
    path("adminlogin/", AdminLoginApi.as_view(), name="adminLogin"),
    path("invitation/create/", CreateInvitationCodeApi.as_view(), name="create-invitation"),
    path("experiment/participants/", ManageExperimentParticipantsApi.as_view(), name="list-participants"),
    path("experiment/participants/<int:user_id>/", ManageExperimentParticipantsApi.as_view(), name="manage-participant"),
    path("profile/update/", AdminUpdateProfileApi.as_view(), name="admin-profile-update"),
    path("getByName/",GetUserInfoByNameApi.as_view(),name="getInfoByName"),
    path("callds/",callDeepSeekApi.as_view(),name="calldeepseek")
]
