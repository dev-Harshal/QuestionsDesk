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
        return f'{self.subject.code}: {self.subject.name} (Unit {self.unit})'

    class Meta:
        db_table = 'Question Sets'

class Division(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    marks = models.PositiveIntegerField(null=False, blank=False, default=0)
    question_mark = models.PositiveIntegerField(null=False, blank=False) 
    extras = models.PositiveIntegerField(null=False, blank=False)
    questions = models.ManyToManyField(Question, related_name='divisions', blank=True)
    status = models.CharField(max_length=100, null=False, blank=False, default='Incomplete')

    def status_check(self ,*args, **kwargs):
        if self.questions.count() == (self.marks / self.question_mark) + (self.extras):
            self.status = "Complete"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'Divisions'

class QuestionPaper(models.Model):
    id = models.BigAutoField(primary_key=True)
    paper_type = models.CharField(max_length=20, null=False, blank=False)
    paper_title = models.CharField(max_length=255, null=False, blank=False)
    subject = models.ForeignKey(Subject, related_name='question_papers', on_delete=models.CASCADE)
    total_marks = models.PositiveIntegerField(null=False, blank=False, default=0)
    academic_year = models.CharField(max_length=10, null=False, blank=False)
    exam_date = models.DateField(null=True, blank=False)
    exam_time = models.CharField(max_length=100, null=True, blank=False)
    division = models.PositiveIntegerField(null=False, blank=False, default=1)
    divisions = models.ManyToManyField(Division, related_name='question_papers')
    status = models.CharField(max_length=100, null=False, blank=False, default='Incomplete')
    created_date = models.DateField(auto_now_add=True)

    def status_check(self ,*args, **kwargs):
        status = 'Complete'
        for division in self.divisions.all():
            if division.status == 'Incomplete':
                status = 'Incomplete'
        self.status = status
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.paper_title} ({self.academic_year})'

    class Meta:
        db_table = 'Question Papers'




    




