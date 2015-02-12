from __future__ import unicode_literals

from collections import OrderedDict

from django.db import models

from .exceptions import ProcessorAlreadyExists, ProcessorDoesNotExists
from ..settings import IMPORT_FROM


class Manager(object):
    """Manager for data processors"""

    def __init__(self):
        self.processors = OrderedDict()

    def models_list(self):
        mlist = filter(
            lambda m: getattr(m, 'ignore_sync', True), models.get_models())
        mlist = filter(
            lambda m: str(m.__module__).startswith('mtr.sync'), mlist)
        return mlist

    def model_choices(self):
        """Return all registered django models as choices"""

        for model in self.models_list():
            yield (
                '{}.{}'.format(model.__module__, model.__name__),
                '{} | {}'.format(
                    model._meta.app_label.title(),
                    model._meta.verbose_name.title()))

    def processor_choices(self):
        """Return all registered processors"""

        for processor in self.processors.values():
            yield (processor.__name__,
                '{} | {}'.format(processor.file_format,
                    processor.file_description))

    def register(self, cls):
        """Decorator to append new processor"""

        if self.has_processor(cls):
            raise ProcessorAlreadyExists(
                'Processor {} already exists'.format(cls.__name__))
        self.processors[cls.__name__] = cls

        if cls.position:
            self.processors = OrderedDict(
                sorted(self.processors.items(), key=lambda p: p.position))

        return cls

    def unregister(self, cls):
        """Decorator to pop processor"""

        self.processors.pop(cls.__name__, None)

        return cls

    def has_processor(self, cls):
        """Check if processor already exists"""

        return True if self.processors.get(cls.__name__, False) else False

    def make_processor(self, settings):
        """Create new processor instance if exists"""

        processor = self.processors.get(settings.processor, None)

        if processor is None:
            raise ProcessorDoesNotExists(
                'Processor {} does not exists'.format(settings.processor))

        return processor(settings)

    def export_data(self, settings, data=None):
        """Export data to file if no data passed,
        create queryset it from settings"""

        processor = self.make_processor(settings)

        if data is None:
            queryset = self.prepare_queryset(settings)
            data = self.filtered_data(settings, queryset)

        return processor.export_data(data)

    def prepare_queryset(self, settings):
        current_model = settings.model_class()

        # TODO: filter data to export

        return current_model.objects.all()

    def filtered_data(self, settings, queryset):
        """Prepare data using filters from settings and return iterator"""

        fields = list(settings.fields_with_filters())

        data = {
            'rows': len(queryset),
            'cols': len(fields),
            'items': (
                field.process(item) for item in queryset for field in fields)
        }

        return data

    def import_processors(self):
        """Import modules within IMPORT_FROM paths"""

        for module in IMPORT_FROM():
            try:
                __import__(module)
            except ImportError:
                raise ImportError(
                    'Invalid module {}, unable to import'.format(module))

manager = Manager()
manager.import_processors()