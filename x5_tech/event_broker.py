

class CanceledOrderEvent:

    def __call__(self):
        print("CanceledOrderEvent")


class CancelPaymentEvent:

    def __call__(self):
        print("CancelPaymentEvent")


class EventBroker:

    def __init__(self):
        self._event_handlers = {}

    def __call__(self, event):
        """Публикация события"""
        self.publish(event)

    def subscribe(self, event_predicate, subsciber):
        """
        Предикат — это функция, которая возвращает true или false в зависимости от переданного значения.

        """
        print('subscribe', id(self), event_predicate, subsciber)

        subscribers = self._event_handlers.setdefault(event_predicate, set())
        subscribers.add(subsciber)

    def register(self, event_predicate):
        def decorator(func):
            self.subscribe(event_predicate, func)
            return func
        return decorator

    def unsubscribe(self, event_predicate, subsciber):
        if subscribers := self._event_handlers.get(event_predicate):
            subscribers.discard(subsciber)

    def publish(self, event):
        print('publish', id(self), event)

        matching_handlers = set()
        for event_predicate, handlers in self._event_handlers.items():
            if event_predicate(event):
                matching_handlers |= handlers
        if not matching_handlers:
            raise
        for handler in matching_handlers:
            handler(event)

    def instance(self, obj_type):
        """Подписка на какой-то тип событий"""
        print('instance', id(self), obj_type)
        _type = obj_type if obj_type is not None else type(None)

        def decorator(func):
            def __(e):
                return isinstance(e, _type)
            # self.subscribe(lambda e: isinstance(e, _type), func)
            self.subscribe(__, func)
            return func

        return decorator


# глобально
EVENT_BROKER = EventBroker()
# в ограниченнои контексте
handle_event = EventBroker()


# транслируем из контекста заказа глобально, кому надо
# Я: подписываем на событие CanceledOrderEvent из контекста заказа
# действие - публикация этого события глобально в EVENT_BROKER
handle_event.instance(CanceledOrderEvent)(EVENT_BROKER)


@EVENT_BROKER.instance(CanceledOrderEvent)
def handle_cancel_payment(event: CanceledOrderEvent):
    print('handle_cancel_payment')
    handle_event(CancelPaymentEvent())


@handle_event.instance(CancelPaymentEvent)
def _(event: CancelPaymentEvent):
    print('CancelPaymentEvent')
    # repo = PaymentRepo()
    # payment = repo.get_order_by_order_id(event.order_id)
    # payment.cancel()
    # repo.save(payment)


"""
как я понял логику:

"""

if __name__ == '__main__':
    print('EVENT_BROKER', id(EVENT_BROKER))
    print('handle_event', id(handle_event))

    # из ограниченного контекста
    handle_event(CanceledOrderEvent())
    print()

