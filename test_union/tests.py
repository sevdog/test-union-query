from django.db import models
from django.test import TestCase
from .models import MainModel, SecondaryModel


DATA = [
    {'value': 1, 'timestamp': '2025-01-01T00:30:00Z'},
    {'value': 2, 'timestamp': '2025-01-01T00:30:00Z'},
]


def query_with_union(data):
    secondary_qs = SecondaryModel.objects.none()
    for elem in data:
        secondary_qs = secondary_qs.union(
            SecondaryModel.objects.filter(
                value=elem['value'],
                timestamp__gte=elem['timestamp'],
            )
            .order_by('-timestamp')
            .values('main', 'timestamp')[:1]
        )

    if len(data) > 1:
        secondary_qs = secondary_qs.order_by('-timestamp')

    return MainModel.objects.get(pk=secondary_qs.values('main')[:1])

def query_with_subquery(data):
    secondary_qs = SecondaryModel.objects.none()
    for elem in data:
        secondary_qs |= (
            SecondaryModel.objects.filter(
                value=elem['value'],
                timestamp__gte=elem['timestamp']
            ).filter(
                timestamp__gte=SecondaryModel.objects.filter(
                    value=elem['value'],
                ).values('timestamp').order_by('-timestamp')[:1]
            )
        )


    secondary_qs = secondary_qs.order_by('-timestamp')
    return MainModel.objects.get(pk=secondary_qs.values('main')[:1])


class ModelTestCase(TestCase):

    fixtures = ['test']

    def test_union_single(self):
        main = query_with_union(DATA[:1])
        self.assertEqual(main.pk, 1)

    def test_union_multiple(self):
        main = query_with_union(DATA)
        self.assertEqual(main.pk, 1)

    def test_suqquery_single(self):
        main= query_with_subquery(DATA[:1])
        self.assertEqual(main.pk, 1)

    def test_suqquery_multiple(self):
        main = query_with_subquery(DATA)
        self.assertEqual(main.pk, 1)
