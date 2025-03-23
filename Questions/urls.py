from django.urls import path
from Questions.views import *

urlpatterns = [
    path('create/question-set/', create_question_set_view, name='create-question-set-view'),
    path('update/question-set/<int:question_set_id>/', update_question_set_view, name='update-question-set-view'),
    path('list/question-sets/', list_question_sets_view, name='list-question-sets-view'),
    path('delete/question-sets/<int:subject_id>/', delete_question_sets_view, name='delete-question-sets-view'),
    path('delete/question-set/<int:subject_id>/<int:unit>/', delete_question_set_view, name='delete-question-set-view'),
    path('create/questions/<int:question_set_id>/', create_questions_view, name='create-questions-view'),
    path('update/questions/<int:subject_id>/<int:unit>/', update_questions_view, name='update-questions-view')
]
