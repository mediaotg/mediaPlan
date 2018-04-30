from django.db import models

class TargetGroup(models.Model):
    name = models.CharField(max_length=1024, unique=True)

    def __str__(self):
        return self.name

def recurrences(): 
    DAILY = 'daily'
    WEEKLY = 'weekly'
    FULL_CAMPAIGN = 'full campaign'
    RECURRENCES = (
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (FULL_CAMPAIGN, 'Full Campaign')
    );
    return RECURRENCES;

class Image(models.Model):
    image = models.ImageField(upload_to='%Y/%m/')

    def __str__(self):
        return self.image.url

class Publication(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    contactName = models.CharField(max_length=1024, null=True)
    email = models.EmailField(max_length=1024)
    phone = models.CharField(max_length=1024, null=True)
    logo = models.ForeignKey(Image, on_delete=models.CASCADE, default=77)
    recurrence = models.CharField(max_length=15, choices=recurrences(), default='weekly')
    targetGroups = models.ManyToManyField(TargetGroup, related_name='publications', blank=True)

    def __str__(self):
        return self.name

class Client(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    logo = models.ForeignKey(Image, on_delete=models.CASCADE, default=77)
    contactName = models.CharField(max_length=1024)
    email = models.EmailField(max_length=1024)
    phone = models.CharField(max_length=1024)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Rate(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="rates")
    rateName = models.CharField(max_length=1024)
    dimensions = models.CharField(max_length=1024)
    bleed = models.CharField(max_length=1024)
    price = models.CharField(max_length=1024)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, related_name="rates")

    def __str__(self):
        return self.rateName

