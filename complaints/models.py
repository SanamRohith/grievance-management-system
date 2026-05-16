from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('student', 'Student'), ('staff', 'Staff')])
    department = models.CharField(max_length=20, choices=[('cse', 'CSE'),('cst', 'CST'), ('ece', 'ECE'),('ect', 'ECT'), ('cai', 'CAI'),('aiml', 'AIML'),('mech', 'MECH'), ('civil', 'CIVIL'), ('eee', 'EEE'),('mba', 'MBA'),('diploma', 'Diploma')])
    contact_number = models.CharField(max_length=15)
    year_of_study = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')], null=True, blank=True)  # Optional field for staff
    
    def __str__(self):
        return self.user.username


class Complaint(models.Model):
    STATUS_CHOICES = [ 
        ('Filed','Filed'),
        ('In progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected','Rejected'),
    ]

    COMPLAINT_TYPE_CHOICES = [
                ('Infrastructure','Infrastructure'),
                ('Faculty','Faculty'),
                ('Women Grievance','Women Grievance'),
                ('Ragging', 'Ragging'),
                ('Hostel', 'Hostel'),
                ('Transport', 'Transport'),
                ('Canteen', 'Canteen'),
                ('Other', 'Other'),

    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, default="")
    type = models.CharField(max_length=255, choices=COMPLAINT_TYPE_CHOICES, default='')
    description = models.TextField(default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Filed')
    date_filed = models.DateTimeField(default=timezone.now)  # Automatically set to the current date and time
    image = models.ImageField(upload_to='complaint_images/', blank=True, null=True)  # Optional image
    file = models.FileField(upload_to='complaint_files/', blank=True, null=True)  # Optional file

    def __str__(self):
        return f"{self.subject} - {self.status}"






