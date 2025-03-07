from django.urls import path
from .apis import seeExperimentApi,chooseExperimentApi,exitExperimentApi,myExperimentApi,seeExperimentHistoryApi,adminSeeExperimentApi,adminAddExp,adminModifyExp,adminDeleteExp
from .apis import CreateProtocolAPIView,DeleteProtocolAPIView,UpdateProtocolAPIView,UserProtocolAPIView,CreateExperimentAPIView,UpdateExperimentAPIView
from .apis import ExperimentDetailAPIView,DeleteExperimentAPIView,UserExperimentListAPIView,ProtocolDetailAPIView,SurveyUpdateAPI
urlpatterns = [
    path('seeExp/', seeExperimentApi.as_view(),name="seeExperiment"),
    path('chooseExp/', chooseExperimentApi.as_view(),name='chooseExperiment'),
    path('exitExp/', exitExperimentApi.as_view(),name='exitExperiment'),
    path('myExp/', myExperimentApi.as_view(),name='myExperiment'),
    path('seeExpHistory/', seeExperimentHistoryApi.as_view(),name='seeExperimentHistory'),
    path('adminSeeExp/', adminSeeExperimentApi.as_view(),name='adminSeeExperiment'),
    path('adminAddExp/', adminAddExp.as_view(),name='adminAddExp'),
    path('adminModifyExp/', adminModifyExp.as_view(),name='adminModifyExp'),
    path('adminDeleteExp/', adminDeleteExp.as_view(),name='adminDeleteExp'),
    path('protocols/create/', CreateProtocolAPIView.as_view(),name='add_protocol'),
    path('protocols/delete/', DeleteProtocolAPIView.as_view(), name='delete-protocol'),
    path('protocols/update/', UpdateProtocolAPIView.as_view()),
    path('protocols/list/', UserProtocolAPIView.as_view(), name='user-protocols'),
    path('protocols/get/<int:protocol_id>/', ProtocolDetailAPIView.as_view(), name='protocolDetail'),
    path('create/',CreateExperimentAPIView.as_view(),name='add_expt'),
    path('delete/',DeleteExperimentAPIView.as_view(),name='delete_expt'),
    path('update/',UpdateExperimentAPIView.as_view(),name='update_expt'),
    path('get/',ExperimentDetailAPIView.as_view(),name='get_expt'),
    path('list/',UserExperimentListAPIView.as_view(),name='expt_list'),
    path('surveys/update/',SurveyUpdateAPI.as_view(),name='update_survey'),
]

