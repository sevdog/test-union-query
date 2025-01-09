from django.db import models


class MainModel(models.Model):
    name = models.CharField(max_length=8)


class SecondaryModel(models.Model):
    main = models.ForeignKey(MainModel, on_delete=models.CASCADE)
    value = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('main', 'value'), name='secondary_uniq'),
        )