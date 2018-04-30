from django.db import models
import datetime

def status():
    DRAFT = 'draft'
    APPROVE = 'approve'
    BOOK = 'book'
    DESIGN = 'design'
    SEND = 'send'
    COMPLETE = 'complete'
    CANCELLED = 'cancelled'

    STATUS = (
        (DRAFT, 'draft'),
        (APPROVE, 'awaiting approval'),
        (BOOK, 'book publications'),
        (DESIGN, 'awaiting design'),
        (SEND, 'sending to publications'),
        (COMPLETE, 'published'),
        (CANCELLED, 'cancelled')
    );
    return STATUS;

class MediaPlan(models.Model):
    name = models.CharField(max_length=2048, unique=True)
    budget = models.BigIntegerField()
    startDate = models.DateField(default=datetime.datetime.now)
    endDate = models.DateField(default=datetime.datetime.now)
    shuffle = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=status(), default='draft')
    designer = models.CharField(max_length=1024)
    starter = models.CharField(max_length=1024, null=True)
    client = models.ForeignKey('setup.Client', on_delete=models.CASCADE)
    audience = models.ManyToManyField('setup.TargetGroup', related_name='campaigns', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Design(models.Model):
    name = models.CharField(max_length=1024)
    thumbnail = models.ForeignKey('setup.Image', on_delete=models.CASCADE, null=True)
    campaign = models.ForeignKey(MediaPlan, on_delete=models.CASCADE, related_name='designs')
    order = models.CharField(max_length=24)
    def __str__(self):
        return self.name

class File(models.Model):
    file = models.FileField(upload_to='files/%Y/%m/')
    def __str__(self):
        return self.file.url

class Week(models.Model):
    start = models.DateField()
    end = models.DateField()
    plan = models.ForeignKey(MediaPlan, on_delete=models.CASCADE, related_name='weeks')
    selectedPubs = models.ManyToManyField('setup.Publication', related_name='weeks')

class WeeklyMediaPlacement(models.Model):
    rate = models.ForeignKey('setup.Rate', on_delete=models.CASCADE)
    deadline = models.DateField()
    plan = models.ForeignKey(MediaPlan, on_delete=models.CASCADE, related_name='weekly_ads')
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='weekly_ads')
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)
    memo = models.CharField(max_length=2048)
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name='weekly_ads')
    status = models.CharField(max_length=24)

class DailyMediaPlacement(models.Model):
    rate = models.ForeignKey('setup.Rate', on_delete=models.CASCADE)
    days = models.CharField(max_length=2048)
    plan = models.ForeignKey(MediaPlan, on_delete=models.CASCADE, related_name='daily_ads')
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='daily_ads')
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)
    memo = models.CharField(max_length=2048)
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name='daily_ads')
    status = models.CharField(max_length=24)

class FullMediaPlacement(models.Model):
    rate = models.ForeignKey('setup.Rate', on_delete=models.CASCADE)
    deadline = models.DateField()
    plan = models.ForeignKey(MediaPlan, on_delete=models.CASCADE, related_name='full_ads')
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='full_ads')
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)
    memo = models.CharField(max_length=2048)
    status = models.CharField(max_length=24)

class Expense(models.Model):
    name = models.CharField(max_length=2048)
    total = models.CharField(max_length=10)
    deadline = models.DateField(default=datetime.datetime.now)
    plan = models.ForeignKey(MediaPlan, on_delete=models.CASCADE, related_name='expenses')

