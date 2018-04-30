from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import ListView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.core import serializers
from django.middleware.csrf import get_token
from tablib import Dataset
from collections import namedtuple
import json

from .resources import TargetGroupResource, PublicationResource, ClientResource
from .forms import GroupForm, PublicationForm, ClientForm
from .models import TargetGroup, Publication, Image, Client, Rate

# Target Groups
class TargetGroupsView(ListView):
    model = TargetGroup
    context_object_name = 'groups'
    template_name = 'target_groups.html'

def targetGroupView(request, pk):
    group = get_object_or_404(TargetGroup, pk=pk)
    return render(request, 'target_group.html', {'group': group})

def editTargetGroupView(request, pk):
    group = get_object_or_404(TargetGroup, pk=pk)
    publications = Publication.objects.all()
    data = {'name': group.name, 
                'publications': group.publications.all() }
    if request.method == 'POST':
        form = GroupForm(instance=group, data=request.POST)
        if form.is_valid():
            group = form.save(commit = False)
            group.save()
            group.publications.set(form.cleaned_data['publications'])
            return redirect('target_group', pk=pk)
    else:
        form = GroupForm(instance=group, data=data)
    return render(request, 'edit_target_group.html', {'group': group, 'publications': publications, 'form': form})

def newTargetGroupView(request):
    publications = Publication.objects.all()
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit = False)
            group.save()
            group.publications.set(form.cleaned_data['publications'])
            return redirect('target_group', pk=group.pk)
    else: 
        form = GroupForm()
    return render(request, 'new_target_group.html', {'publications': publications, 'form': form})

def deleteGroup(request, pk):
    group = get_object_or_404(TargetGroup, pk=pk)
    group.delete()
    return redirect('target_groups')

def uploadGroup(request):
    if request.method == 'POST':
        group_resource = TargetGroupResource()
        dataset = Dataset()
        new_groups = request.FILES['myfile']

        imported_data = dataset.load(new_groups.read().decode('utf-8'), format='csv')
        result = group_resource.import_data(dataset, dry_run=True)

        if not result.has_errors():
            group_resource.import_data(dataset, dry_run=False)
            return JsonResponse({'code': '200', 'message': 'success'})
        else:
            print(result)
            return JsonResponse({'code': '500', 'message': 'error'})
    

# Publications
class PublicationsView(ListView):
    model = Publication
    context_object_name = 'publications'
    template_name = 'publications.html'

def publicationView(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    return render(request, 'publication.html', {'publication': publication})

def editPublicationView(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    groups = TargetGroup.objects.all()
    data = {'name': publication.name, 'contactName': publication.contactName, 'email': publication.email}
    data['phone'] = publication.phone
    data['targetGroups'] = publication.targetGroups.all()
    data['recurrence'] = publication.recurrence
    data['rates'] = publication.rates.all()
    if request.method == 'POST':
        form = PublicationForm(instance=publication, data=request.POST)
        if form.is_valid():
            publication = form.save(commit=False)
            targets = request.POST.getlist('targetGroups')
            publication.targetGroups.set(targets)
            publication.save()
            rates = request.POST.getlist('rates')
            for rate in rates:
                parsedRate = json.loads(rate, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                if parsedRate.pk != '':
                    existingRate = publication.rates.get(pk = int(parsedRate.pk))
                    if len(parsedRate.name) < 1 and len(parsedRate.price) < 1:
                        existingRate.delete()
                    else:
                        existingRate.rateName = parsedRate.name
                        existingRate.dimensions = parsedRate.size
                        existingRate.bleed = parsedRate.bleed
                        existingRate.price = parsedRate.price
                        existingRate.save()
                else:
                    if len(parsedRate.name) > 0 and len(parsedRate.price) > 0:
                        newRate = Rate(publication=publication)
                        newRate.rateName = parsedRate.name
                        newRate.dimensions = parsedRate.size
                        newRate.bleed = parsedRate.bleed
                        newRate.price = parsedRate.price
                        newRate.save()
            deleteRates = request.POST.getlist('deleteRates')
            for rate in deleteRates:
                parsedDeleteRates = json.loads(rate)
                for parsedRate in parsedDeleteRates:
                    publication.rates.filter(pk = int(parsedRate)).delete()
            return JsonResponse({'code': '200', 'messag': 'Successfully submitted', 'publication': publication.pk})

        else:
            return JsonResponse({'code': '300', 'message': 'Validation errors', 'errors': form.errors})
    else:
        form = PublicationForm(instance=publication)
    return render(request, 'edit_publication.html', {'publication': publication, 'groups': groups, 'form': form})

def newPublicationView(request):
    groups = TargetGroup.objects.all()
    if request.method == 'POST':
        form = PublicationForm(request.POST)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.save()
            rates = request.POST.getlist('rates')
            for rate in rates:
                parsedRate = json.loads(rate, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                if len(parsedRate.name) > 0:
                    newRate = Rate(publication=publication)
                    newRate.rateName = parsedRate.name
                    newRate.dimensions = parsedRate.size
                    newRate.bleed = parsedRate.bleed
                    newRate.price = parsedRate.price
                    newRate.save()
            return JsonResponse({'code': '200', 'messag': 'Successfully submitted', 'publication': publication.pk})
        else:
            return JsonResponse({'code': '300', 'message': 'Validation errors', 'errors': form.errors})
    else: 
        form = PublicationForm()
    return render(request, 'new_publication.html', {'groups': groups, 'form': form})

def deletePublication(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    publication.delete()
    return redirect('publications')

def uploadPublication(request):
    if request.method == 'POST':
        pub_resource = PublicationResource()
        dataset = Dataset()
        new_pubs = request.FILES['myfile']

        imported_data = dataset.load(new_pubs.read().decode('utf-8'), format='csv')
        result = pub_resource.import_data(dataset, dry_run=True)

        if not result.has_errors():
            pub_resource.import_data(dataset, dry_run=False)
            return JsonResponse({'code': '200', 'message': 'success'})
        else:
            print(result)
            return JsonResponse({'code': '500', 'message': 'error'})

def uploadImage(request):
    if request.method == 'POST':
        image = Image(image = request.FILES['logo-file'])
        image.save()
        return JsonResponse({'code': '200', 'message': 'success', 'image': image.pk})
    return JsonResponse({'code': '500', 'message': 'error'})


# Clients
class ClientsView(ListView):
    model = Client
    context_object_name = 'clients'
    template_name = 'clients.html'

def clientView(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'client.html', {'client': client})

def newClientView(request):
    items = Client.objects.all()
    publications = Publication.objects.all()
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.save()
            rates = request.POST.getlist('rates')
            for pub in rates:
                pubJson = json.loads(pub, object_hook=lambda d:namedtuple('X', d.keys())(*d.values()))
                for rate in pubJson.rates:
                    newRate = Rate(publication = Publication.objects.get(name=pubJson.publication))
                    newRate.rateName = rate.name
                    newRate.dimensions = rate.size
                    newRate.bleed = rate.bleed
                    newRate.price = rate.price
                    newRate.client = client
                    newRate.save()
            return JsonResponse({'code': '200', 'messag': 'Successfully submitted', 'client': client.pk})

        else:
            return JsonResponse({'code': '300', 'message': 'Validation errors', 'errors': form.errors})
    else: 
        form = ClientForm()
    return render(request, 'new_client.html', {'form': form, 'clients': items, 'publications': publications})

def editClientView(request, pk):
    client = get_object_or_404(Client, pk=pk)
    items = Client.objects.all()
    publications = Publication.objects.all()
    if request.method == 'POST':
        form = ClientForm(instance=client, data=request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            rates = request.POST.getlist('rates')
            saveRates = []
            for pub in rates:
                pubJson = json.loads(pub, object_hook=lambda d:namedtuple('X', d.keys())(*d.values()))
                for rate in pubJson.rates:
                    print(rate)
                    if rate.pk != '':
                        existingRate = client.rates.get(pk=int(rate.pk))
                        if len(rate.name) < 1 and len(rate.price) < 1:
                            existingRate.delete()
                        else:
                            existingRate.rateName = rate.name
                            existingRate.dimensions = rate.size
                            existingRate.bleed = rate.bleed
                            existingRate.price = rate.price
                            existingRate.save()
                    else:
                        newRate = Rate(publication = Publication.objects.get(name=pubJson.publication))
                        newRate.rateName = rate.name
                        newRate.dimensions = rate.size
                        newRate.bleed = rate.bleed
                        newRate.price = rate.price
                        newRate.client = client
                        newRate.save()
            deleteRates = request.POST.getlist('deleteRates')
            for rate in deleteRates:
                parsedDeleteRates = json.loads(rate)
                for rate in parsedDeleteRates:
                    client.rates.filter(pk = int(rate)).delete()
            client.save()
            return JsonResponse({'code': '200', 'messag': 'Successfully submitted', 'client': client.pk})
        else:
            return JsonResponse({'code': '300', 'message': 'Validation errors', 'errors': form.errors})
    else: 
        form = ClientForm(instance=client)
    return render(request, 'edit_client.html', {'form': form, 'clients': items, 'publications': publications, 'client': client})

def deleteClient(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    return redirect('clients')

def uploadClient(request):
    if request.method == 'POST':
        client_resource = ClientResource()
        dataset = Dataset()
        new_cleints = request.FILES['myfile']

        imported_data = dataset.load(new_cleints.read().decode('utf-8'), format='csv')
        result = client_resource.import_data(dataset, dry_run=True)

        if not result.has_errors():
            client_resource.import_data(dataset, dry_run=False)
            return JsonResponse({'code': '200', 'message': 'success'})
        else:
            print(result)
            return JsonResponse({'code': '500', 'message': 'error'})