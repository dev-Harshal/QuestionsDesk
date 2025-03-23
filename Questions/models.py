from django.db import models
from Users.models import *
# Create your models here.

class Question(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    mark = models.PositiveIntegerField(null=False, blank=False, default=0)
    levels = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Questions'

class QuestionSet(models.Model):
    id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(Subject, related_name='question_sets', on_delete=models.CASCADE)
    unit = models.PositiveIntegerField(null=False, blank=False, default=0)
    unit_title = models.CharField(max_length=255, null=False, blank=False)
    co = models.PositiveIntegerField(null=False, blank=False, default=0)
    co_title = models.CharField(max_length=255, null=False, blank=False)
    questions = models.ManyToManyField(Question, related_name='question_sets', blank=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.subject.code} :{self.subject.name} - Unit: {self.unit}'

    class Meta:
        db_table = 'Question Sets'

class Division(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    marks = models.PositiveIntegerField(null=False, blank=False, default=0)
    question_mark = models.PositiveIntegerField(null=False, blank=False) 
    extras = models.PositiveIntegerField(null=False, blank=False)
    questions = models.ManyToManyField(Question, related_name='divisions', blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'Divisions'

class QuestionPaper(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=20, null=False, blank=False)
    title = models.CharField(max_length=255, null=False, blank=False)
    subject = models.ForeignKey(Subject, related_name='question_papers', on_delete=models.CASCADE)
    marks = models.PositiveIntegerField(null=False, blank=False, default=0)
    academic_year = models.CharField(max_length=10, null=False, blank=False)
    date = models.DateField(null=True, blank=False)
    time = models.CharField(max_length=100, null=True, blank=False)
    divisions = models.ManyToManyField(Division, related_name='question_papers')
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} ({self.academic_year})'

    class Meta:
        db_table = 'Question Papers'




    




