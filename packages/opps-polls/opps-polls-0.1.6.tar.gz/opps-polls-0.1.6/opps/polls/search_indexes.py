#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from haystack.indexes import SearchIndex, Indexable, CharField, DateTimeField

from .models import Poll


class PollIndex(SearchIndex, Indexable):
    text = CharField(document=True, use_template=True)
    date_available = DateTimeField(model_attr='date_available')
    date_update = DateTimeField(model_attr='date_update')

    def get_updated_field(self):
        return 'date_update'

    def get_model(self):
        return Poll

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            date_available__lte=datetime.now(),
            published=True)
