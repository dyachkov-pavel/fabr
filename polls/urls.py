from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CreateAnswerView, PollCreateUpdateDestroyView,
                    PollRetrieveView, PollView,
                    QuestionCreateUpdateDestroyView, UserAnswerView)

admin_router_v1 = DefaultRouter()
admin_router_v1.register('polls', PollCreateUpdateDestroyView)
admin_router_v1.register('polls/(?P<poll_id>.+)/questions',
                        QuestionCreateUpdateDestroyView)


urlpatterns = [
    path('admin/', include(admin_router_v1.urls)),
    path('polls/', PollView.as_view(), name='poll_view'),
    path('polls/<int:pk>/',
         PollRetrieveView.as_view(),
         name='poll_detail_view'),
    path('polls/<int:poll_id>/answer/',
         CreateAnswerView.as_view(),
         name='create_answer_view'),
    path('users/<int:user_id>/answers/',
         UserAnswerView.as_view(),
         name='user_answer_view')
]
