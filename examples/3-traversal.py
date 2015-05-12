import asyncio

from aiohttp.web import HTTPBadRequest, HTTPNotFound

from aiotraversal import Application
from aiotraversal.resources import Root, Resource
from aiotraversal.views import RESTView


DATA = {
    'orders': [
        {'id': 1, 'status': 'executed', 'value': 1000},
        {'id': 2, 'status': 'in_progress', 'value': 1200},
        {'id': 3, 'status': 'done', 'value': 900},
        {'id': 4, 'status': 'canceled', 'value': 1500},
    ]
}


class OrdersView(RESTView):
    methods = {'get', 'post'}

    @asyncio.coroutine
    def get(self):
        return (yield from self.resource.list())

    @asyncio.coroutine
    def post(self):
        data = yield from self.request.json()

        if 'value' not in data:
            raise HTTPBadRequest()

        return (yield from self.resource.create(value=data['value']))


class OrdersResource(Resource):
    @asyncio.coroutine
    def list(self):
        return DATA['orders']

    @asyncio.coroutine
    def create(self, value):
        order = {
            'id': max(o['id'] for o in DATA['orders']) + 1,
            'status': 'executed',
            'value': value,
        }

        DATA['orders'].append(order)
        return order

    @asyncio.coroutine
    def __getchild__(self, name):
        if not name.isdigit():
            raise HTTPNotFound()

        id = int(name)

        for order in (o for o in DATA['orders'] if id == o['id']):
            break
        else:
            raise HTTPNotFound()

        status = order['status']

        if status == 'executed':
            return ExecutedOrderResource(self, name, order)
        elif status == 'in_progress':
            return InProgressOrderResource(self, name, order)
        elif status == 'done':
            return DoneOrderResource(self, name, order)
        elif status == 'canceled':
            return CanceledOrderResource(self, name, order)


class OrderView(RESTView):
    methods = {'get', 'patch'}

    @asyncio.coroutine
    def get(self):
        return (yield from self.resource.get())

    @asyncio.coroutine
    def patch(self):
        data = yield from self.request.json()

        if 'status' not in data:
            raise HTTPBadRequest()

        status = data['status']

        to_status = getattr(self.resource, 'to_{}'.format(status), None)

        if not to_status:
            raise HTTPBadRequest()

        order = yield from to_status()

        return order


class BaseOrderResource(Resource):
    def __init__(self, parent, name, order):
        super().__init__(parent, name)
        self.order = order
        self.id = order['id']

    @asyncio.coroutine
    def get(self):
        return self.order

    @asyncio.coroutine
    def set_status(self, status):
        self.order['status'] = status
        return self.order


class CancelableOrder:
    @asyncio.coroutine
    def to_canceled(self):
        self.order['status'] = 'canceled'
        return self.order


class ExecutedOrderResource(CancelableOrder, BaseOrderResource):
    @asyncio.coroutine
    def to_in_progress(self):
        self.order['status'] = 'in_progress'
        return self.order


class InProgressOrderResource(CancelableOrder, BaseOrderResource):
    @asyncio.coroutine
    def to_done(self):
        self.order['status'] = 'done'
        return self.order


class DoneOrderResource(BaseOrderResource):
    pass


class CanceledOrderResource(BaseOrderResource):
    pass


def main():
    loop = asyncio.get_event_loop()

    app = Application()  # create main application instance
    app.include('aiotraversal.resources')
    app.add_child(Root, 'orders', OrdersResource)
    app.bind_view(OrdersResource, OrdersView)  # /orders
    app.bind_view(BaseOrderResource, OrderView)  # /orders/:id
    app.start(loop)  # start application

    try:
        loop.run_forever()  # run event loop
    finally:
        loop.close()


if __name__ == '__main__':
    main()
