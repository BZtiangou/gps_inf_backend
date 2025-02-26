from django.urls import path
from .apis import ShowQuestionApi,SendResApi,createSurveyApi,submitQuestionApi,getquestionsApi


urlpatterns = [
    path("createSurvey/",createSurveyApi.as_view(),name="createSurvey"),
    path("sendRes/",SendResApi.as_view(),name="sendRes"),
    path("showQuestion/<int:survey_id>",ShowQuestionApi.as_view(),name="showQuestion"),
    path("submitQuestion/",submitQuestionApi.as_view(),name="submitQuestion"),
    path("getquestions/",getquestionsApi.as_view(),name="getquestions"),
]