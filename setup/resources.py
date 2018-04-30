from import_export import widgets, fields, resources
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from .models import TargetGroup, Publication, Client

class TargetGroupResource(resources.ModelResource):
    class Meta:
        model = TargetGroup


class PublicationResource(resources.ModelResource):
    logo = publication__logo='uploads/2018/04/placeholder.png'
    targetGroups = fields.Field(
        column_name='targetGroups',
        attribute='targetGroups',
        widget=ManyToManyWidget(TargetGroup, ',', 'name'))
    class Meta:
        model = Publication
        import_id_fields = ('name',)

class ClientResource(resources.ModelResource):
    logo = publication__logo='uploads/2018/04/placeholder.png'
    parent = fields.Field(
        column_name='parent',
        attribute='parent',
        widget=ForeignKeyWidget(Client, 'name'))
    class Meta:
        model = Client
        import_id_fields = ('name',)
