import pytest

from abc import ABC
from uuid import uuid4

from django.urls import resolve, reverse

from rest_framework import status

from .services import ServiceAbstractClass


pytestmark = pytest.mark.django_db


@pytest.fixture(scope='function')
def sac_abstract_methods_mocker(mocker):
    """
    Fixture to mock the abstract methods of ServiceAbstractClass making
    it testable without asking for implementing all abstract methods on
    an instance.
    """

    mocker.patch.multiple(ServiceAbstractClass, __abstractmethods__=set())

    yield

    mocker.resetall()


def test_if_theres_a_schema_url_for_metadata_and_documentation(client):
    """
    Test if there is a schema URL for metadata and documentation.
    """

    url = reverse('docs')

    response = client.get(url)

    assert url
    assert response.status_code == status.HTTP_200_OK


def test_task_API_endpoint_and_namespace_definition(client):
    """
    Test if there is a Task API endpoint and if is defined as "core"
    namespace and "task-list" as his name
    """

    url = '/api/v1/task/'
    resolved = resolve(url)

    assert resolved.namespace == 'core'\
        and resolved.url_name == 'task-list'


def test_documentation_for_task_view():
    """
    Test if there is documentation for the Task API Endpoint
    """

    url = reverse('core:task-list')
    view = resolve(url).func

    assert view.__doc__


def test_return_404_when_a_Task_is_not_found(client):
    """
    Test if a 404 Http status is returned when a Task is not found.
    """

    url = reverse('core:task-detail', kwargs={'job_id': uuid4()})

    request = client.get(url)

    assert request.status_code == status.HTTP_404_NOT_FOUND


def test_for_a_task_abstract_class():
    """
    Test for the existence of a ServiceAbstractClass to import.
    """

    assert ServiceAbstractClass


def test_for_serviceabstractclass_as_abstract_class_instance():
    """
    Test for ServiceAbstractClass is a abstract base class(ABC) instance
    """

    assert issubclass(ServiceAbstractClass, ABC)


def test_for_some_serviceabstractclass_attributes():
    """
    Test for a list of attributes that ServiceAbstractClass must implement.
    """

    attributes = {'trigger', 'queue', 'message'}

    for attribute in attributes:
        assert hasattr(ServiceAbstractClass, attribute)


def test_for_initial_validation_when_instantiate_serviceabstractclass(sac_abstract_methods_mocker):
    """
    Test if a instance of ServiceAbstractClass raises an exception when
    instantiated without value for 'trigger' attribute.

    Test use sac_abstract_methods_mocker fixture.
    """

    class TestService(ServiceAbstractClass):
        pass

    with pytest.raises(Exception) as exception:
        TestService()

    assert str(exception.value) == 'A trigger must be a string and it is needed to accept any task.'


def test_for_queue_parameter_initial_validation_when_instantiate_serviceabstractclass(sac_abstract_methods_mocker):
    """
    Test if a instance of ServiceAbstractClass raises an exception when
    instantiated without value for 'queue' attribute.

    Test use sac_abstract_methods_mocker fixture.
    """

    class TestService(ServiceAbstractClass):
        trigger = 'test'
        pass

    with pytest.raises(Exception) as exception:
        TestService()

    assert str(exception.value) == 'A queue must be a string and it is needed to propagate the results.'


def test_for_serviceabstractclass_abstract_methods():
    """
    Test for abstract methods of ServiceAbstractClass. Expect to find the
    following list 'obtainMessage', 'validateMessage', 'transformMessage',
    'persistData', 'propagateResult'.
    """

    methods = {'obtainMessage', 'validateMessage', 'transformMessage',
               'persistData', 'propagateResult'}

    assert ServiceAbstractClass.__abstractmethods__ == methods


def test_for_process_method_on_serviceabstractclass():
    """
    Test for the process method used to run all methods at once.
    """

    assert ServiceAbstractClass.process


def test_for_existence_of_a_dispatch_method():
    """
    Test for the existence of a dispatch method witch will be used
    """

    from core.tasks import dispatch

    assert callable(dispatch)


def test_extract_subsclass_information_from_ServiceAbstractClass(sac_abstract_methods_mocker):
    """
    Test for extract the subclasses from ServiceAbstractClass.

    Test use sac_abstract_methods_mocker fixture.
    """

    class RegistryValidationService(ServiceAbstractClass):
        trigger = 'registry-validation'
        queue = 'registry-q'

    class RegistryPersistenceService(ServiceAbstractClass):
        trigger = 'registry-persistence'
        queue = 'registry-q'

    services = ServiceAbstractClass.__subclasses__()

    assert len(services) == 2

def test_build_a_dict_using_trigger_attribute_from_all_ServiceAbstractClass_subclasses(sac_abstract_methods_mocker):
    """
    Test for build a dict with the trigger attribute from all
    ServiceAbstractClass subclasses.

    Test use sac_abstract_methods_mocker fixture.
    """

    class RegistryValidationService(ServiceAbstractClass):
        trigger = 'registry-validation'
        queue = 'registry-q'

    class RegistryPersistenceService(ServiceAbstractClass):
        trigger = 'registry-persistence'
        queue = 'registry-q'

    services = ServiceAbstractClass.__subclasses__()

    triggers = {service.trigger: service for service in services}

    assert len(triggers) == 2
    assert 'registry-validation' in triggers.keys()
    assert 'registry-persistence' in triggers.keys()
    assert 'RegistryValidationService' in str(triggers.values())
    assert 'RegistryPersistenceService' in str(triggers.values())
