"""
Complex example for usage treversal logic.

URLs:

    * GET /orders -- list of orders
    * POST /orders -- creage an order
    * GET /orders/:id -- get an order
    * PATCH /orders/:id -- change order

Order object:

    * id -- int
    * value -- int, order's value
    * status -- str, one of {'executed', 'in_progress', 'done', 'canceled'}

Order lifecycle:

    executed --> in_progress --> done
       |                |
       |--> canceled <--|


I will use httpie (https://github.com/jkbrzt/httpie) for examples:

    # get orders
    $ http GET localhost:8080/orders --print=b
    [
        {
            "id": 1,
            "status": "executed",
            "value": 1000
        },
        {
            "id": 2,
            "status": "in_progress",
            "value": 1200
        },
        {
            "id": 3,
            "status": "done",
            "value": 900
        },
        {
            "id": 4,
            "status": "canceled",
            "value": 1500
        }
    ]

    # create an order
    $ http POST localhost:8080/orders value:=13000 --print=b
    {
        "id": 5,
        "status": "executed",
        "value": 13000
    }

    # try set status 'done'
    $ http PATCH localhost:8080/orders/1 status=done --print=b
    400: Bad Request

    # move order to 'in_progress'
    $ http PATCH localhost:8080/orders/1 status=in_progress --print=b
    {
        "id": 1,
        "status": "in_progress",
        "value": 1000
    }

Let's play with it!
"""
import asyncio

from aiohttp.web import HTTPBadRequest, HTTPNotFound

from aiohttp_traversal.ext.resources import Root, Resource
from aiohttp_traversal.ext.views import RESTView

from aiotraversal import Application
from aiotraversal.cmd import run


DATA = {
    'orders': [
        {'id': 1, 'status': 'executed', 'value': 1000},
        {'id': 2, 'status': 'in_progress', 'value': 1200},
        {'id': 3, 'status': 'done', 'value': 900},
        {'id': 4, 'status': 'canceled', 'value': 1500},
    ]
}


class NotExistValue(Exception):
    pass


class NotExistStatus(Exception):
    pass


class BadStatus(Exception):
    pass


class OrdersView(RESTView):
    methods = {'get', 'post'}

    @asyncio.coroutine
    def get(self):
        return (yield from self.resource.list())

    @asyncio.coroutine
    def post(self):
        data = yield from self.request.json()

        if 'value' not in data:
            raise NotExistValue()

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
        """ Return resource, who provide one order logic
        """
        if not name.isdigit():
            return None

        id = int(name)

        for order in (o for o in DATA['orders'] if id == o['id']):
            break
        else:
            return None

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
            raise NotExistStatus()

        status = data['status']

        to_status = getattr(self.resource, 'to_{}'.format(status), None)

        if not to_status:
            raise BadStatus()

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

    app = Application()

    with app.configure(loop=loop) as config:
        config.include('aiotraversal.cmd')
        config.include('aiotraversal.serve')

        config.add_child(Root, 'orders', OrdersResource)  # add child for root

        config.bind_view(OrdersResource, OrdersView)
        config.bind_view(BaseOrderResource, OrderView)  # add view for base class of resources

    run(app, loop)


if __name__ == '__main__':
    main()
