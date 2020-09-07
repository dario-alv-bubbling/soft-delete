**how to:**

1. Add "softdelete" to your INSTALLED_APPS setting like this::
```djangotemplate
    INSTALLED_APPS = [
        ...
        'softdelete',
    ]
```

2. Import the app ::
```djangotemplate
    from softdelete.models import SoftDeleteModel
```

3. Create models inheriting the SoftDeleteModel :
```djangotemplate
    class MyModel(SoftDeleteModel):
        ...
```

4. In order to cascade delete related models on delete implement the following method:
```djangotemplate
    @staticmethod
    def get_soft_delete_models():
        return [ElectricCabinetEnvironmentalImpact.__name__, ElectricCabinetPhoto.__name__, ElectricCabinetEnergySources.__name__]

    
```
