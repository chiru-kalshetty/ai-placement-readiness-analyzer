from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    BRANCH_CHOICES = [
        ('Engineering', 'Engineering'),
        ('Commerce', 'Commerce'),
        ('Arts', 'Arts'),
        ('Others', 'Others'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES, default='Engineering')
    cgpa = models.FloatField()
    technical_skills = models.CharField(max_length=200)
    soft_skills = models.CharField(max_length=200, blank=True)
    projects = models.IntegerField()
    internships = models.IntegerField()
    certifications = models.IntegerField(default=0)
    aptitude = models.IntegerField(default=0)
    communication = models.IntegerField(default=0)
    leadership = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name