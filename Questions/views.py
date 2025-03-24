from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Min
from Users.models import *
from Questions.models import *
from Questions.services import *
from django.db.models import Prefetch
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
        question_sets__in=QuestionSet.objects.filter(subject__in=request.user.profile.subjects.all())
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
        return redirect('list-question-sets-view')

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
        question_titles = request.POST.getlist('question_title[]')
        marks = request.POST.getlist('mark[]')

        created_questions = []
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

        question_set.questions.add(*created_questions)

        messages.success(request, f'Questions updated for Question set of {question_set}.')
        return JsonResponse({'status':'success', 'success_url':f'/teacher/update/questions/{question_set.subject.id}/{question_set.unit}/'})
    else:
        question_sets =QuestionSet.objects.filter(subject=question_set.subject)
        units = list(set(question_sets.values_list('unit', flat=True).order_by('unit')))
        questions = question_set.questions.all().order_by('mark','levels')
        return render(request, 'question_sets/questions/update_questions.html', context={'question_set':question_set,'questions':questions, 'units':units, 'current_unit':question_set.unit})

def list_questions_view(request, question_set_id):
    question_set = QuestionSet.objects.get(id=question_set_id)
    questions = question_set.questions.all().order_by('mark', 'levels')
    return render(request, 'question_sets/questions/list_questions.html', context={'question_set':question_set,'questions':questions})


# QUESTION PAPERS VIEW

def create_question_paper_view(request):
    if request.method == 'POST':
        paper_type = request.POST.get('paper_type')
        paper_title = request.POST.get('paper_title')
        total_marks = request.POST.get('total_marks')
        division = request.POST.get('division')
        code = request.POST.get('code')
        subject = Subject.objects.get(code=code)

        start_year = request.POST.get('start_year')
        end_year = request.POST.get('end_year')
        academic_year = f'{start_year}-{end_year}'

        date = request.POST.get('date')
        hour = request.POST.get('hour', None)
        minute = request.POST.get('minute' , '')

        if int(end_year) - int(start_year) > 1:
            return JsonResponse({'status':'error', 'message':f'Academic year cannot be more than 1 Year.'})
        
        if paper_type != 'Assignment':
            if paper_type == 'Unit Test':
                if QuestionPaper.objects.filter(paper_type=paper_type, paper_title__iexact=paper_title ,subject=subject, academic_year=academic_year).exists():
                    return JsonResponse({'status':'error', 'message':f'{subject.name} {paper_title} paper for {academic_year} already exists.'})
            else:
                if QuestionPaper.objects.filter(paper_type=paper_type, paper_title__iexact=paper_title, subject=subject, academic_year=academic_year).exists():
                    return JsonResponse({'status':'error', 'message':f'Exam Paper for {subject.name} for {academic_year} already exists.'})
        else:
            if QuestionPaper.objects.filter(paper_type=paper_type, paper_title__iexact=paper_title ,subject=subject, academic_year=academic_year).exists():
                return JsonResponse({'status':'error', 'message':f'{paper_title} for {subject.name} for {academic_year} already exists.'})
        
        question_paper = QuestionPaper.objects.create(
            paper_type = paper_type,
            paper_title = paper_title,
            subject = subject,
            total_marks = int(total_marks),
            division = int(division),
            academic_year = f'{start_year}-{end_year}',
            exam_date = date if date else None,
            exam_time = f'{hour} Hour' if minute == '' else f'{hour} Hour {minute} Min' if hour else None
        )

        messages.success(request, f'Question Paper for {question_paper} created successfully.')
        return JsonResponse({'status':'success', 'success_url':f'/teacher/create/division/{question_paper.id}/'})
    else:
        question_sets_subjects = Subject.objects.filter(
            question_sets__in=QuestionSet.objects.filter(subject__in=request.user.profile.subjects.all())
        ).distinct()
        return render(request, 'question_papers/create_question_paper.html', context={'question_sets_subjects':question_sets_subjects})

def create_division_view(request, question_paper_id):

    question_paper = QuestionPaper.objects.get(id=question_paper_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        marks = request.POST.get('marks')
        question_mark = request.POST.get('question_mark')
        extras = request.POST.get('extras')

        if question_paper.divisions.all().count() == question_paper.division:
            return JsonResponse({'status':'error', 'message':f'{question_paper.paper_title} contains only {question_paper.division} divisions.'})

        divisons = question_paper.divisions.all().values_list('marks', flat=True)

        if sum(divisons) + int(marks) > question_paper.total_marks:
            return JsonResponse({'status':'error', 'message':f'{question_paper.paper_title} total mark limit exceeded.'})
        
        division = Division.objects.create(
            title=title,
            marks=int(marks),
            question_mark=int(question_mark),
            extras = int(extras)
        )
        question_paper.divisions.add(division)
        question_paper.status_check()

        messages.success(request, f'Division for {question_paper.paper_title} created successfully.')
        return JsonResponse({'status':'success', 'success_url':f'/teacher/add/questions/{division.id}/{question_paper.id}/'})
    return render(request, 'question_papers/create_division.html', context={'question_paper':question_paper})

def add_questions_view(request, division_id, question_paper_id):
    division = Division.objects.get(id=division_id)
    question_paper = QuestionPaper.objects.get(id=question_paper_id)
    
    if request.method == 'POST':
        question_ids = request.POST.getlist('question_id[]')
        selected_questions = []
        total = 0

        if len(question_ids) > (division.marks / division.question_mark) + (division.extras):
            return JsonResponse({'status':'error', 'message':f'Select only {int(division.marks / division.question_mark)} Questions and {division.extras} Extras. (Selected: {len(question_ids)})'})

        for id in question_ids:
            question = Question.objects.get(id=id)
            selected_questions.append(question)
        division.questions.add(*selected_questions)
        division.status_check()

        if question_paper.divisions.all().count() < question_paper.division:
            success_url = f'/teacher/create/division/{question_paper.id}/'
        else:
            success_url = f'/teacher/detail/question-paper/{question_paper.id}/'

        messages.success(request, f'Questions added for {question_paper.paper_title}, {question_paper.subject.name} created successfully.')
        return JsonResponse({'status':'success', 'success_url':success_url})
    subject = question_paper.subject
    question_mark = division.question_mark
    question_sets = QuestionSet.objects.filter(subject=subject)
    question_sets = question_sets.prefetch_related(
        Prefetch(
            'questions',
            queryset=Question.objects.filter(mark=question_mark),
            to_attr='filtered_questions'
        )
    )
    return render(request, 'question_papers/add_questions.html', context={'division':division, 'question_sets':question_sets, 'question_paper':question_paper})

def detail_question_paper_view(request, question_paper_id):
    question_paper = QuestionPaper.objects.get(id=question_paper_id)
    return render(request, 'question_papers/detail_question_paper.html', context={'question_paper':question_paper})

def list_question_papers_view(request):
    question_papers = 1
    return render(request, 'question_papers/list_question_papers.html', context={'question_paper':question_paper})

