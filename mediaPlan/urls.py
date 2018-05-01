"""mediaPlan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from setup import views as setup_views
from plans import views as plans_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', setup_views.homeView, name='home'),

    #setup
    path('setup/target-groups', setup_views.TargetGroupsView.as_view(), name='target_groups'),
    path('setup/target-groups/<int:pk>', setup_views.targetGroupView, name='target_group'),
    path('setup/target-groups/<int:pk>/edit', setup_views.editTargetGroupView, name='edit_target_group'),
    path('setup/target-groups/new', setup_views.newTargetGroupView, name='new_target_group'),
    path('setup/target-groups/<int:pk>/delete', setup_views.deleteGroup, name='delete_group'),
    path('setup/target-groups/upload', setup_views.uploadGroup, name='upload_groups'),

    path('setup/publications', setup_views.PublicationsView.as_view(), name='publications'),
    path('setup/publications/<int:pk>', setup_views.publicationView, name='publication'),
    path('setup/publications/<int:pk>/edit', setup_views.editPublicationView, name='edit_publication'),
    path('setup/publications/new', setup_views.newPublicationView, name='new_publication'),
    path('setup/publications/<int:pk>/delete', setup_views.deletePublication, name='delete_publication'),
    path('setup/publications/upload', setup_views.uploadPublication, name='upload_publications'),
    path('setup/publications/upload-image', setup_views.uploadImage, name='upload_image'),

    path('setup/clients', setup_views.ClientsView.as_view(), name='clients'),
    path('setup/clients/<int:pk>', setup_views.clientView, name='client'),
    path('setup/clients/<int:pk>/edit', setup_views.editClientView, name='edit_client'),
    path('setup/clients/new', setup_views.newClientView, name='new_client'),
    path('setup/clients/<int:pk>/delete', setup_views.deleteClient, name='delete_client'),
    path('setup/clients/upload', setup_views.uploadClient, name='upload_clients'),

    #media plans
    path('plans/media-plans', plans_views.MediaPlansView.as_view(), name='media_plans'),
    path('plans/media-plans/new', plans_views.newPlanView, name='new_plan'),
    path('plans/media-plans/<int:pk>/edit', plans_views.editPlanView, name='edit_plan'),
    path('plans/media-plans/<int:pk>/designs', plans_views.designsPlanView, name='designs_plan'),
    path('plans/media-plans/<int:pk>/plan', plans_views.planView, name='plan'),
    path('plans/media-plans/upload-thumbnails', plans_views.uploadThumbnail, name='upload_thumbnail'),
    path('plans/media-plans/<int:pk>/delete', plans_views.deletePlan, name='delete_plan'),
    path('plans/media-plans/<int:pk>/save', plans_views.createPdf, name='save_pdf'),
    path('plans/media-plans/<int:pk>/design-pdf', plans_views.designPdf, name='design_pdf'),
    path('plans/media-plans/<int:pk>/continue', plans_views.continuePlan, name='continue_plan'),
    path('plans/media-plans/<int:pk>/update-status', plans_views.updateStatus, name='update_status'),
    path('plans/media-plans/<int:pk>/pdf/<int:pub>', plans_views.publicationPdf, name='pub_pdf'),
    path('plans/media-plans/<int:pk>/update-pub-status', plans_views.updatePubStatus, name='update_pub_status'),

    path('plans/designs', plans_views.DesignsView.as_view(), name='designs'),
    path('plans/designs/<int:pk>', plans_views.designsCampaign, name='designs_campaign'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
