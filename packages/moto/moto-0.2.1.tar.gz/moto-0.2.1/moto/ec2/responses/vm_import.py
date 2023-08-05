from jinja2 import Template

from moto.ec2.models import ec2_backend
from moto.ec2.utils import resource_ids_from_querystring


class VMImport(object):
    def cancel_conversion_task(self):
        raise NotImplementedError('VMImport.cancel_conversion_task is not yet implemented')

    def describe_conversion_tasks(self):
        raise NotImplementedError('VMImport.describe_conversion_tasks is not yet implemented')

    def import_instance(self):
        raise NotImplementedError('VMImport.import_instance is not yet implemented')

    def import_volume(self):
        raise NotImplementedError('VMImport.import_volume is not yet implemented')
