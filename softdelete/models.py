from django.db import models, transaction
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


"""
references:

https://medium.com/@adriennedomingus/soft-deletion-in-django-e4882581c340
https://blog.usebutton.com/cascading-soft-deletion-in-django

When a model inherits from soft delete class the normal delete manage is overridden, therefore db actions such as
CASCADE, DO_NOTHING, etc are not propagated.
In that get_soft_delete_models() must be overridden in the inheriting models so that the CASCADE operation is performed.
"""


class SoftDeleteQuerySet(models.QuerySet):
    """ Perform soft deletes ONLY """
    def delete(self):
        return super(SoftDeleteQuerySet, self).update(deleted_at=timezone.now())


class SoftDeleteManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.with_deleted = kwargs.pop('deleted', False)
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def _base_queryset(self):
        return super().get_queryset().filter(deleted_at=None)

    def get_queryset(self):
        qs = SoftDeleteQuerySet(self.model)
        if self.with_deleted:
            return qs
        return qs.filter(deleted_at=None)


class SoftDeleteModel(BaseModel):
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    objects = SoftDeleteManager()
    objects_with_deleted = SoftDeleteManager(deleted=True)

    @transaction.atomic
    def delete(self):
        self.deleted_at = timezone.now()
        self.save()
        self._on_delete()

    def restore(self):
        self.deleted_at = None
        self.save()

    @staticmethod
    def get_soft_delete_models():
        """
        This method is necessary in order to let the soft delete operation which additional models to look for to delete
        """
        return []

    def _on_delete(self):
        """
        The '_on_delete' method is called when a soft delete is performed.
        The related models for soft delete are retrieved and compared with the relation tree of the object.
        While looping if the relation exists then the related object's 'delete' method is also called.
        """
        for relation in self._meta._relation_tree:
            related_models = self.get_soft_delete_models()
            if related_models and relation.model.__name__ in related_models:

                name_filter = {relation.name: self}

                """ this goes only delete one level down (calls queryset) """
                # relation.model.objects.filter(**name_filter).delete()
                """ 
                must iterate on the objects in order to reach all related models (e.g Device -> Evse -> Connector)
                since deletions are not such a frequent task it is ok to do it like that at the moment.
                TODO:re-evaluate 
                """
                for relation_obj in relation.model.objects.filter(**name_filter):
                    relation_obj.delete()
