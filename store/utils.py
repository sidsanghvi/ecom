import json
from .models import *


def cookieCart(request):
    # query cart cookie
    # convert cart cookie from string to dict.
    try:
        cart = json.loads(request.COOKIES['cart'])
    # if cart undefined, create cart.
    except:
        cart = {}

    # set empty variable for order
    items = []
    order = {'get_cart_total': 0, 'get_cart_quantity': 0, 'shipping': False}

    # add order values from cookie to above variable
    for key in cart:
        # try block just in case something breaks
        # eg: if a product in cart is deleted from db
        try:
            # update cart total items
            order['get_cart_quantity'] += cart[key]['quantity']
            # query relevant product
            product = Product.objects.get(id=key)
            # update cart total price
            order['get_cart_total'] += product.price * cart[key]['quantity']
            # update shipping needed or not
            if product.digital == False:
                order['shipping'] = True

            # create item object
            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL
                },
                'quantity': cart[key]['quantity'],
                'get_total': product.price * cart[key]['quantity'],
            }
            # add item object to items array, to query from cart.html
            items.append(item)
        except:
            pass
    return {'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        # query customer instance associated with user
        customer = request.user.customer
        # query/create+query an order for above customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        # query all order items in above order
        items = order.orderitem_set.all()
    else:
        cookie_data = cookieCart(request)
        order = cookie_data['order']
        items = cookie_data['items']
    return {'order': order, 'items': items}


def guestCheckout(request, data):
    # initialise name and email from data sent from js
    name = data['form']['name']
    email = data['form']['email']

    # initialse cart data from cookie
    cookieData = cookieCart(request)
    items = cookieData['items']
    order = cookieData['order']

    # query/create+query customer with associated email
    customer, created = Customer.objects.get_or_create(email=email)
    # add given name to associated customer object
    # we set name outside get_or_create to avoid duplicate data of customer with diff names but same email
    customer.name = name
    customer.save()

    # create order object with assoociated customer
    order = Order.objects.create(
        customer=customer,
        complete=False
    )

    # create order items for order
    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )

    return customer, order
