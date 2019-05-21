from django_rq import job

from .services import ServiceAbstractClass


@job
def dispatch(message, trigger):
    """
    Receives a message and a trigger witch will be used to determine
    what to do with the message in witch queue.

    Parameters
    ----------
    message : dict
        The message containing data or a locator to get it.

    trigger : str
        A string containing a trigger to witch service to run
    """

    services = ServiceAbstractClass.__subclasses__()

    if not services:
        raise Exception('No ServiceAbstractClass subclass has been'
                        ' found. You need to create a new class '
                        'inherit it to make dispatch works.')

    triggers = {service.trigger: service for service in services}

    service = triggers.get(trigger)

    if not service:
        raise Exception('No trigger available to match your '
                        'request. Verify if there is any '
                        'ServiceAbstractClass subclass with '
                        'this trigger.')

    service(message)

    service.process()