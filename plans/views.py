from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, UpdateView
from datetime import datetime
from collections import namedtuple
from datetime import timedelta, date
import json
import time
import ast
import requests


from slackclient import SlackClient

from io import BytesIO
from plans.print import PdfPrint

from .forms import PlanForm
from .models import MediaPlan, Design, Week, WeeklyMediaPlacement, DailyMediaPlacement, FullMediaPlacement, Expense
from setup.models import Client, TargetGroup, Image, Publication, Rate

# Media Plans
class MediaPlansView(ListView):
    model = MediaPlan
    context_object_name = 'plans'
    template_name = 'media_plans.html'

def newPlanView(request):
    clients = Client.objects.all()
    groups = TargetGroup.objects.all()
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit = False)
            plan.save()

            audience = request.POST.getlist('audience')
            for group in audience:
                plan.audience.add(TargetGroup.objects.get(pk=group))

            dates = []
            weeks = []
            dates.append(plan.startDate)
            dates.append(plan.endDate)

            def daterange(date1, date2, intv):
                diff = (date2 - date1) / intv
                for i in range(intv):
                    yield (date1 + diff  * i)
                yield date2

            for dt in daterange(dates[0], dates[1], 2):
                week = Week()
                week.start=dt
                week.end=(dt + timedelta(days=7))
                week.plan=plan
                week.save()
                pubs = []
                for group in plan.audience.all():
                    print(group.publications)
                    for pub in group.publications.all():
                        pubs.append(pub)
                        print (pub)
                week.selectedPubs.set(pubs)
                week.save()

            return JsonResponse({'code': '200', 'message': 'Successfully submitted', 'plan': plan.pk})
        else:
            return JsonResponse({'code': '300', 'message': 'Validation errors', 'errors': form.errors})
    else: 
        form = PlanForm()
    return render(request, 'new_plan.html', {'form': form, 'clients': clients, 'groups': groups, 'date': datetime.now()});

def editPlanView(request, pk):
    plan = get_object_or_404(MediaPlan, pk=pk)
    clients = Client.objects.all()
    groups = TargetGroup.objects.all()
    data = {'name': plan.name, 'client': plan.client, 'budget': plan.budget, 'dates': str(plan.startDate) + ' to ' + str(plan.endDate), 'audience': plan.audience, 'designer': plan.designer}
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            plan = form.save(commit = False)
            plan.save()

            audience = request.POST.getlist('audience')
            for group in audience:
                plan.audience.add(TargetGroup.objects.get(pk=group))

            dateStr = str(plan.dates).split(' to ')
            dates = []
            weeks = []
            for date in dateStr:
                dates.append(datetime.strptime(date,"%A %b %d, %Y").date())

            def daterange(date1, date2, intv):
                diff = (date2 - date1) / intv
                for i in range(intv):
                    yield (date1 + diff  * i)
                yield date2

            for dt in daterange(dates[0], dates[1], 2):
                week = Week()
                week.start=dt
                week.end=(dt + timedelta(days=7))
                week.plan=plan
                week.save()
                pubs = []
                for group in plan.audience.all():
                    print(group.publications)
                    for pub in group.publications.all():
                        pubs.append(pub)
                        print (pub)
                week.selectedPubs.set(pubs)
                week.save()

            return JsonResponse({'code': '200', 'message': 'Successfully submitted', 'plan': plan.pk})
        else:
            return JsonResponse({'code': '300', 'message': 'Validation errors', 'errors': form.errors})
    else: 
        form = PlanForm(instance=plan)
    return render(request, 'edit_plan.html', {'form': form, 'clients': clients, 'groups': groups, 'date': datetime.now(), 'plan': plan});

def designsPlanView(request, pk):
    plan = get_object_or_404(MediaPlan, pk=pk)
    if request.method == 'POST':
        designs = request.POST.getlist('designs[]')
        for design in designs:
            designJson = json.loads(design, object_hook=lambda d:namedtuple('X', d.keys())(*d.values()))
            if designJson.pk != '':
                existing = plan.designs.get(pk=designJson.pk)
                existing.name = designJson.filename
                if designJson.image != '':
                    existing.thumbnail = Image.objects.get(pk=designJson.image)
                existing.order = designJson.order
                existing.save()
            else:
                item = Design(name=designJson.filename, order=designJson.order, campaign=plan)
                if designJson.image != '':
                    item.thumbnail = Image.objects.get(pk=designJson.image)
                item.save()
        deleted = json.loads(request.POST['deleted'], object_hook=lambda d:namedtuple('X', d.keys())(*d.values()))
        for delete in deleted:
            plan.designs.get(pk=delete).delete()

        deletedImages = json.loads(request.POST['deletedImages'], object_hook=lambda d:namedtuple('X', d.keys())(*d.values()))
        for delete in deletedImages:
            Image.objects.get(pk=delete).delete()

        return JsonResponse({'code': '200', 'message': 'Successfully submitted', 'plan': plan.pk})
    return render(request, 'new_plan_designs.html', {'plan': plan})

def uploadThumbnail(request):
    if request.method == 'POST':
        file = Image(image = request.FILES['file'])
        file.save()
        return JsonResponse({'code': '200', 'message': 'success', 'image': file.pk, 'url': file.image.url})
    return JsonResponse({'code': '500', 'message': 'error'})

def planView(request, pk):
    plan = get_object_or_404(MediaPlan, pk=pk)
    groups = TargetGroup.objects.all()
    publications = {};
    publications['full'] = []
    for group in plan.audience.all():
        publications['full'] += group.publications.filter(recurrence='full campaign')
    publications['all'] = Publication.objects.all()
    publications['weekly'] = []
    publications['daily'] = []
    publications['allFull'] = []
    for group in groups:
        pubs = []
        pubsDaily = []
        pubsFull = []
        weekly = False
        daily = False
        full = False
        for pub in group.publications.all():
            if pub.recurrence == 'weekly':
                pubs.append(pub)
                weekly = True
            if pub.recurrence == 'daily':
                pubsDaily.append(pub)
                daily = True
            if pub.recurrence == 'full campaign':
                pubsFull.append(pub)
                full = True
        if weekly == True:
            publications['weekly'].append({'group': group, 'publications': pubs})
        if daily == True:
            publications['daily'].append({'group': group, 'publications': pubsDaily})
        if full == True:
            publications['allFull'].append({'group': group, 'publications': pubsFull})

    weeklyBudget = int(plan.budget) / plan.weeks.count()
    weekBudgets = []
    extra = {'full': [], 'expenses': {'ads': plan.expenses.all(), 'total': 0}, 'total': 0}
    for pub in publications['full']:
        rates = []
        total = 0
        adCount = 0
        for ad in plan.full_ads.filter(rate__publication = pub):
            adCount += 1
            rates.append(ad)
            total += int(ad.rate.price)
            extra['total'] += int(ad.rate.price)
        if adCount > 0:
            extra['full'].append({'pub': pub, 'rates': rates, 'total': total})
    for ad in plan.expenses.all():
        extra['expenses']['total'] += int(ad.total)
        extra['total'] += int(ad.total)


    if plan.weekly_ads.count() > 0 or plan.daily_ads.count() > 0 or plan.full_ads.count() > 0 or plan.expenses.count() > 0:
        for week in plan.weeks.all():
            budget = 0
            singleWeek = {'week': week, 'budget': budget, 'pubsdaily': [], 'pubsweekly': []}
            for pub in week.selectedPubs.filter(recurrence = 'weekly'):
                pubSingle = {'pub': pub, 'rates': [], 'total': 0}
                for ad in plan.weekly_ads.filter(rate__publication = pub, week = week):
                    pubSingle['rates'].append(ad)
                    pubSingle['total'] += int(ad.rate.price)
                singleWeek['pubsweekly'].append(pubSingle)
            for pub in week.selectedPubs.filter(recurrence = 'daily'):
                pubSingle = {'pub': pub, 'rates': [], 'total': 0}
                for ad in plan.daily_ads.filter(rate__publication = pub, week = week):
                    pubSingle['rates'].append(ad)
                    pubSingle['total'] += int(ad.rate.price)
                singleWeek['pubsdaily'].append(pubSingle)
            weekBudgets.append(singleWeek)
    else:
        weekCount = 0
        designs = plan.designs.all()
        for week in plan.weeks.all():
            pubCount = 0
            budget = 0
            if (week.selectedPubs.count() > 0):
                budget = weeklyBudget / week.selectedPubs.count()
            singleWeek = {'week': week, 'budget': budget, 'pubsdaily': [], 'pubsweekly': []}
            for pub in week.selectedPubs.all():
                difference = 0
                diffSet = False
                lowestRate = ''
                pubCount += 1
                for rate in pub.rates.all():
                    if rate.client == plan.client or rate.client == None:
                        diff = abs(float(rate.price) - budget)
                        if diff < difference or diffSet == False:
                            difference = diff
                            lowestRate = rate
                            diffSet = True
                if pub.recurrence == 'weekly':
                    if plan.shuffle == True:
                        design = designs[(pubCount - 1) % len(designs)]
                    else:
                        design = designs[(weekCount - 1) % len(designs)]
                    if lowestRate:
                        ad = WeeklyMediaPlacement.objects.create(rate = lowestRate, design = design, plan = plan, week = week, deadline=datetime.now())
                        singleWeek['pubsweekly'].append({'pub': pub, 'rates': [ad], 'total': lowestRate.price})

                if pub.recurrence == 'daily':
                    if plan.shuffle == True:
                        design = designs[(pubCount - 1) % len(designs)]
                    else:
                        design = designs[(weekCount - 1) % len(designs)]
                    if lowestRate:
                        ad = DailyMediaPlacement.objects.create(rate = lowestRate, design = design, plan = plan, week = week, days='')
                        singleWeek['pubsdaily'].append({'pub': pub, 'rates': [ad], 'total': lowestRate.price})
            weekBudgets.append(singleWeek)
            weekCount += 1

        for group in plan.audience.all():
            for pub in group.publications.filter(recurrence = 'full campaign'):
                extra['full'].append({'pub': pub, 'rates': [], 'total': 0})

        print ('FULL : ' )
        print(extra['full'])


    if request.method == 'POST':
        # update existing ads
        # delete deleted ads
        new = request.POST['new']
        newAds = json.loads(new, object_hook=lambda d:namedtuple('X', d.keys())(*d.values()))
        weekly = newAds.weekly
        for ad in weekly:
            placement = WeeklyMediaPlacement(rate = Rate.objects.get(pk=ad.rate))
            placement.design=Design.objects.get(pk=ad.design)
            placement.deadline=ad.deadline
            placement.week=Week.objects.get(pk=ad.week)
            placement.plan=plan
            plan.weeks.get(pk=ad.week).selectedPubs.add(Rate.objects.get(pk=ad.rate).publication)
            placement.save()
        daily = newAds.daily
        for ad in daily:
            placement = DailyMediaPlacement(rate = Rate.objects.get(pk=ad.rate))
            placement.design=Design.objects.get(pk=ad.design)
            placement.days=ad.days
            placement.week=Week.objects.get(pk=ad.week)
            placement.plan=plan
            plan.weeks.get(pk=ad.week).selectedPubs.add(Rate.objects.get(pk=ad.rate).publication)
            placement.save()
        full = newAds.full
        for ad in full:
            placement = FullMediaPlacement(rate = Rate.objects.get(pk=ad.rate))
            placement.design=Design.objects.get(pk=ad.design)
            placement.deadline=ad.deadline
            placement.plan=plan
            placement.save()
        extra = newAds.extra
        for ad in extra:
            placement = Expense(name = ad.name)
            placement.total=ad.price
            placement.deadline=ad.deadline
            placement.plan=plan
            placement.save()

        edit = request.POST['edit']
        editAds = json.loads(edit, object_hook=lambda d:namedtuple('X', d.keys())(*d.values()))
        weekly = editAds.weekly
        for ad in weekly:
            placement = WeeklyMediaPlacement.objects.get(pk = ad.pk)
            placement.rate = Rate.objects.get(pk=ad.rate)
            placement.design=Design.objects.get(pk=ad.design)
            placement.deadline=ad.deadline
            placement.save()
        daily = editAds.daily
        for ad in daily:
            placement = DailyMediaPlacement.objects.get(pk = ad.pk)
            placement.rate = Rate.objects.get(pk=ad.rate)
            placement.design=Design.objects.get(pk=ad.design)
            placement.days=ad.days
            placement.save()
        full = editAds.full
        for ad in full:
            placement = FullMediaPlacement.objects.get(pk = ad.pk)
            placement.rate = Rate.objects.get(pk=ad.rate)
            placement.design=Design.objects.get(pk=ad.design)
            placement.deadline=ad.deadline
            placement.save()
        extra = editAds.extra
        for ad in extra:
            placement = Expense.objects.get(pk = ad.pk)
            placement.name = ad.name
            placement.total=ad.price
            placement.deadline=ad.deadline
            placement.save()

        delete = request.POST['delete']
        deleteAds = json.loads(delete, object_hook=lambda d:namedtuple('X', d.keys())(*d.values()))
        for ad in deleteAds.weekly:
            WeeklyMediaPlacement.objects.get(pk=ad).delete()
        for ad in deleteAds.daily:
            DailyMediaPlacement.objects.get(pk=ad).delete()
        for ad in deleteAds.full:
            FullMediaPlacement.objects.get(pk=ad).delete()
        for ad in deleteAds.extra:
            Expense.objects.get(pk=ad).delete()

        return JsonResponse({'code': '200', 'message': 'Successfully submitted', 'plan': plan.pk})

    return render(request, 'media_plan.html', {'plan': plan, 'groups': groups, 'publications': publications, 'budget': weekBudgets, 'extra': extra})

def deletePlan(request, pk):
    plan = get_object_or_404(MediaPlan, pk=pk)
    plan.delete()
    return redirect('media_plans')

def createPdf(request, pk):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'

    buffer = BytesIO()
    report = PdfPrint(buffer, 'letter')
    plan = get_object_or_404(MediaPlan, pk=pk)
    weekList = []
    weekCount = 0
    for week in plan.weeks.all():
        weekItem = {'week': week, 'table': [], 'total': 0}
        weekCount += 1
        ads = []
        for ad in week.weekly_ads.all():
            ads.append([ad.rate.publication.name, ad.rate.rateName, ad.deadline, ad.design, '$' + ('%.2f' % int(ad.rate.price))])
            weekItem['total'] += int(ad.rate.price)
        for ad in week.daily_ads.all():
            x = ast.literal_eval(ad.days)
            daysString = ''
            adTotal = 0
            for day in x:
                adTotal += int(ad.rate.price)
                daysString += day + ', '
            ads.append([ad.rate.publication.name, ad.rate.rateName, daysString, ad.design, '$' + ('%.2f' % int(adTotal))])
            weekItem['total'] += int(ad.rate.price)
        weekItem['table'].append(['Week ' + str(weekCount), week.start, '', '', '$' + ('%.2f' % int(weekItem['total']))])
        weekItem['table'] = weekItem['table'] + ads
        weekList.append(weekItem)

    mylist = [['Publication', 'Page Type', 'Days', 'Price', 'Design']]
    for ad in plan.daily_ads.all():
        mylist.append([ad.rate.publication, ad.rate.rateName, ad.days, '$' + ad.rate.price, ad.design])
    pdf = report.planReport(weekList, plan.name, plan)
    response.write(pdf)
    return response


def designPdf(request, pk):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'

    buffer = BytesIO()
    report = PdfPrint(buffer, 'letter')
    plan = get_object_or_404(MediaPlan, pk=pk)
    pdf = report.designReport(plan)
    response.write(pdf)
    return response

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="mypdf.pdf"'

    buffer = BytesIO()
    report = PdfPrint(buffer, 'letter')
    plan = get_object_or_404(MediaPlan, pk=pk)
    pdf = report.designReport(plan)
    response.write(pdf)
    return response

def publicationPdf(request, pk, pub):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'

    buffer = BytesIO()
    report = PdfPrint(buffer, 'letter')
    plan = get_object_or_404(MediaPlan, pk=pk)
    publication = get_object_or_404(Publication, pk=pub)

    ads = []
    for ad in plan.weekly_ads.all():
        if ad.rate.publication == publication:
            ads.append(ad)
    for ad in plan.daily_ads.all():
        if ad.rate.publication == publication:
            ads.append(ad)
    for ad in plan.full_ads.all():
        if ad.rate.publication == publication:
            ads.append(ad)

    pdf = report.publicationReport(plan, publication, ads)
    response.write(pdf)
    return response

def continuePlan(request, pk):
    plan = get_object_or_404(MediaPlan, pk=pk)
    publications = set()
    for ad in plan.weekly_ads.all():
        publications.add(ad.rate.publication)
    for ad in plan.daily_ads.all():
        publications.add(ad.rate.publication)
    for ad in plan.full_ads.all():
        publications.add(ad.rate.publication)

    currentPlan = {'weeks': [], 'full': {'ads': [], 'total': 0}, 'expenses': {'ads': [], 'total': 0}, 'total': 0}
    for week in plan.weeks.all():
        curWeek = {'week': week, 'daily': [], 'weekly': [], 'total': 0}
        for ad in week.weekly_ads.all():
            curWeek['weekly'].append(ad)
            curWeek['total'] += int(ad.rate.price)
            currentPlan['total'] += int(ad.rate.price)
        for ad in week.daily_ads.all():
            total = 0
            days = ast.literal_eval(ad.days)
            for day in days:
                total += int(ad.rate.price)
            curWeek['daily'].append({'ad': ad, 'total': total})
            curWeek['total'] += total
            currentPlan['total'] += total
        currentPlan['weeks'].append(curWeek)
    for ad in plan.full_ads.all():
        currentPlan['full']['ads'].append(ad)
        currentPlan['full']['total'] += int(ad.rate.price)
        currentPlan['total'] += int(ad.rate.price)
    for ad in plan.expenses.all():
        currentPlan['expenses']['ads'].append(ad)
        currentPlan['expenses']['total'] += int(ad.total)
        currentPlan['total'] += int(ad.total)


    return render(request, 'continue.html', {'plan': plan, 'pubs': publications, 'curPlan': currentPlan})

def updateStatus(request, pk):
    status = request.POST.get('status')
    plan = get_object_or_404(MediaPlan, pk=pk)
    plan.status = status
    print (status)
    plan.save()
    return JsonResponse({'code': '200', 'message': 'Successfully updated', 'plan': plan.status})

def updatePubStatus(request, pk):
    status = request.POST.get('status')
    pub = request.POST.get('pub')
    plan = get_object_or_404(MediaPlan, pk=pk)
    publication = get_object_or_404(Publication, pk=pub)
    booked = True
    sent = True
    for ad in plan.weekly_ads.all():
        if ad.rate.publication == publication:
            ad.status = status
            ad.save()
        if ad.status != 'booked':
            booked = False
        if ad.status != 'sent':
            sent = False
    for ad in plan.daily_ads.all():
        if ad.rate.publication == publication:
            ad.status = status
            ad.save()
        if ad.status != 'booked':
            booked = False
        if ad.status != 'sent':
            sent = False
    for ad in plan.full_ads.all():
        if ad.rate.publication == publication:
            ad.status = status
            ad.save()
        if ad.status != 'booked':
            booked = False
        if ad.status != 'sent':
            sent = False

    if booked == True:
        plan.status = 'send'
    if sent == True:
        plan.status = 'complete'

    return JsonResponse({'code': '200', 'message': 'Successfully updated'})

# Designs
class DesignsView(ListView):
    model = MediaPlan
    context_object_name = 'plans'
    template_name = 'designs.html'

def designsCampaign(request, pk):
    plan = get_object_or_404(MediaPlan, pk=pk)
    return render(request, 'designs_campaign.html', {'plan': plan})


