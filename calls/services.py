import json

from django.urls import reverse_lazy

from core.services import ServiceAbstractClass

from .serializers import CallSerializer
from .serializers import RegistrySerializer

from .models import Call


class RegistryService(ServiceAbstractClass):
    """
    RegistryService is a service responsible for new registries processing.
    """

    trigger = 'registry-service'
    queue = 'registry-service-done'
    validation_class = RegistrySerializer

    def startTask(self):
        super().startTask()

    def obtainMessage(self):
        pass

    def validateMessage(self):
        """
        Uses RegistrySerializer to validate information obtained at
        self.message or on other variable.

        :returns: bool
            Returns True if message is valid and populates self.result

        self.registry: RegistrySerializer
            Is an instance of RegistrySerializer with the data if the message
            is valid.

        self.result: dict
            Contains the result of validation if the message is invalid.
        """
        assert self.validation_class is not None, (f'{self.__class__.__name__}'
                                                   ' must include a validation'
                                                   '_attribute or override '
                                                   'validateMessage method.')

        validation_class = self.validation_class
        registry = validation_class(data=self.message, context={'request': None})

        if registry.is_valid():
            self.is_valid = True
            self.registry = registry
        else:
            self.result = registry.errors
            super().finishTask(failed=True)

        return self.is_valid

    def transformMessage(self):
        pass

    def persistData(self):
        """
        Persist the data into a storage.

        Persist the data into Registry model instance.

        :returns: Registry
            Returns a Registry instance
        """

        assert self.is_valid is not None, ('You must override the '
                                           'persistData method if you want '
                                           'to persist the data without '
                                           'validating it first.')

        registry = self.registry
        registry.save()

        self.result = json.dumps(registry.data)
        return registry.instance

    def propagateResult(self):
        super().propagateResult()

    def finishTask(self):
        super().finishTask()


class CallService(ServiceAbstractClass):
    """
    CallService is responsible for getting a pair of registries and
    consolidate into a complete call.
    """

    trigger = 'registry-service-done'
    queue = 'call-service-done'

    def startTask(self):
        super().startTask()

    def obtainMessage(self):
        pass

    def validateMessage(self):
        pass

    def transformMessage(self):
        """
        Transform the registry message into a dict to be used to create or
        update a Call instance.
        """

        message = json.loads(self.message)

        call_data = {
            'call_id': message.get('call_id')
        }

        if message.get('type') == 'start':
            call_data['start_timestamp'] = message.get('timestamp')
            call_data['source'] = message.get('source')
            call_data['destination'] = message.get('destination')
        else:
            call_data['stop_timestamp'] = message.get('timestamp')

        self.data = call_data
        return self.data

    def persistData(self):
        """
        Create or update a Call model instance.

        :returns: Call
            Returns a Call instance.
        """

        call_data = self.data

        call, created = Call.objects.update_or_create(
            call_id=call_data.get('call_id'),
            defaults=call_data
        )

        if not created:
            call.refresh_from_db()
        self.persisted_data = call
        return self.persisted_data

    def propagateResult(self):
        """
        Propagate a serialized message of consolidated Call instance.
        """

        call = self.persisted_data
        self.result = json.dumps(CallSerializer(call, context={'request': None}).data)

        if call.start_timestamp and call.stop_timestamp:
            super().propagateResult()
            return True

        return False

    def finishTask(self):
        super().finishTask()
