from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Min
from Users.models import *
from Questions.models import *
from Questions.services import *
# Create your views here.

def create_question_set_view(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        subject = Subject.objects.get(code=code)
        unit = request.POST.get('unit')
        unit_title = request.POST.get('unit_title')
        co = request.POST.get('co')
        co_title = request.POST.get('co_title')

        if QuestionSet.objects.filter(subject=subject, unit=int(unit)).exists():
            return JsonResponse({'status':'error', 'message':f'Question set for Unit :{unit} already exists'})
        if QuestionSet.objects.filter(subject=subject, co=int(co)).exists():
            return JsonResponse({'status':'error', 'message':f'Question set for Co :{co} already exists'})

        question_set = QuestionSet.objects.create(
            subject = subject,
            unit = int(unit),
            unit_title = unit_title,
            co = int(co),
            co_title = co_title
        )

        messages.success(request, f'Question set for {question_set} created successfully.')
        return JsonResponse({'status':'success', 'success_url':f'/teacher/create/questions/{question_set.id}/'})
    subjects = request.user.profile.subjects.all()
    return render(request, 'question_sets/create_question_set.html', context={'subjects':subjects})

def update_question_set_view(request, question_set_id):
    question_set = QuestionSet.objects.get(id=question_set_id)   
    
    if request.method == 'POST':
        code = request.POST.get('code')
        subject = Subject.objects.get(code=code)
        unit = request.POST.get('unit')
        unit_title = request.POST.get('unit_title')
        co = request.POST.get('co')
        co_title = request.POST.get('co_title')

        unit_question_sets = QuestionSet.objects.filter(subject=subject, unit=int(unit))
        if unit_question_sets.exists() and unit_question_sets[0] != question_set:
                return JsonResponse({'status':'error', 'message':f'Question set for Unit :{unit} already exists'})
        co_question_sets = QuestionSet.objects.filter(subject=subject, co=int(co))
        if co_question_sets.exists() and co_question_sets[0] != question_set:
            return JsonResponse({'status':'error', 'message':f'Question set for Co :{co} already exists'})

        question_set.subject = subject
        question_set.unit = int(unit)
        question_set.unit_title = unit_title
        question_set.co = int(co)
        question_set.co_title = co_title
        question_set.save()

        messages.success(request, f'Question set for {question_set} saved successfuully.')
        return JsonResponse({'status':'success', 'success_url':f'/teacher/update/question-set/{question_set.id}/'})
    subjects = request.user.profile.subjects.all()
    return render(request, 'question_sets/update_question_set.html', context={'question_set':question_set,'subjects':subjects})

def list_question_sets_view(request):
    distinct_question_set_subjects = request.user.profile.subjects.filter(
        question_sets__in=QuestionSet.objects.all()
    ).distinct().annotate(min_unit=Min('question_sets__unit'))
    return render(request, 'question_sets/list_question_sets.html', context={'subjects':distinct_question_set_subjects})

def delete_question_set_view(request, subject_id, unit):
    subject = Subject.objects.get(id=subject_id)
    question_set = QuestionSet.objects.get(subject=subject, unit=int(unit))
    for question in question_set.questions.all():
        question.delete()
    question_set.delete()
    messages.success(request, f'Question set for {question_set} deleted successfully.')
    existing_question_sets = QuestionSet.objects.filter(subject=subject).values_list('unit', flat=True)
    if existing_question_sets:
        existing_question_sets = sorted([int(u) for u in existing_question_sets])
        unit = int(unit)
        closest_unit = min(existing_question_sets, key=lambda x: abs(x - unit))
        return redirect('update-questions-view', subject_id=subject.id, unit=closest_unit)
    else:
        return redirect('list-question-set-view')

def delete_question_sets_view(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    question_sets = QuestionSet.objects.filter(subject=subject)
    for question_set in question_sets:
        for question in question_set.questions.all():
            question.delete()
    question_sets.delete()
    messages.success(request, f'Question sets for {subject} deleted successfully.')
    return redirect('list-question-sets-view')

def create_questions_view(request, question_set_id):
    question_set = QuestionSet.objects.get(id=question_set_id)
    if request.method == 'POST':
        created_questions = []
        question_titles = request.POST.getlist('question_title[]')
        marks = request.POST.getlist('mark[]')

        for title, mark in zip(question_titles, marks):
            levels = classify_blooms_taxonomy(title)
            question = Question.objects.create(title=title, mark=int(mark), levels=levels)
            created_questions.append(question)
        question_set.questions.add(*created_questions)

        messages.success(request, f'Questions added for {question_set}.')
        return JsonResponse({'status':'success', 'success_url':f'/teacher/update/questions/{question_set.subject.id}/{question_set.unit}/'})
    return render(request, 'question_sets/questions/create_questions.html', context={'question_set':question_set})

def update_questions_view(request, subject_id, unit):
    subject = Subject.objects.get(id=subject_id)
    question_set = QuestionSet.objects.get(subject=subject, unit=unit)
    
    if request.method == 'POST':
        existing_question_ids = request.POST.getlist('existing_question_id[]')
        existing_question_titles = request.POST.getlist('existing_question_title[]')
        existing_marks = request.POST.getlist('existing_mark[]')

        question_titles = request.POST.getlist('question_title[]')
        marks = request.POST.getlist('mark[]')

        existing_questions = []
        updated_question_ids = set()
        for id, title, mark in zip(existing_question_ids, existing_question_titles, existing_marks):
            levels = classify_blooms_taxonomy(title)
            question = Question.objects.get(id=int(id))
            question.title = title
            question.mark = int(mark)
            question.levels = levels
            question.save()
            existing_questions.append(question)
            updated_question_ids.add(int(id))
  
        for question in question_set.questions.all():
            if question.id not in updated_question_ids:
                question.delete()

        created_questions = []
        for title, mark in zip(question_titles, marks):
            levels = classify_blooms_taxonomy(title)
            question = Question.objects.create(title=title, mark=int(mark), levels=levels)
            created_questions.append(question)

        question_set.questions.clear()
        questions = existing_questions + created_questions
        question_set.questions.add(*questions)

        messages.success(request, f'Question updated for Question set for {question_set}.')
        return JsonResponse({'status':'success', 'success_url':f'/teacher/update/questions/{question_set.subject.id}/{question_set.unit}/'})

    question_sets =QuestionSet.objects.filter(subject=question_set.subject)
    units = question_sets.values_list('unit', flat=True).order_by('unit')
    questions = question_set.questions.all().order_by('mark','levels')
    return render(request, 'question_sets/questions/update_questions.html', context={'question_set':question_set,'questions':questions, 'units':units, 'current_unit':question_set.unit})