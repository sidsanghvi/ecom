from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime

# Create your views here.

from .models import *


def store(request):
    # query all products
    products = Product.objects.all()

    # to dynaimcally render order info of logged in user
    if request.user.is_authenticated:
        # query customer instance associated with user
        customer = request.user.customer
        # query/create+query an order for above customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
    else:
        order = {'get_cart_total': 0,
                 'get_cart_quantity': 0, 'shipping': False}

    context = {'products': products, 'order': order}
    return render(request, 'store/store.html', context)


def cart(request):
    # to dynaimcally render order info of logged in user
    if request.user.is_authenticated:
        # query customer instance associated with user
        customer = request.user.customer
        # query/create+query an order for above customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        # query all order items in above order
        items = order.orderitem_set.all()
    else:
        # query cart cookie
        # convert cart cookie from string to dict.
        try:
            cart = json.loads(request.COOKIES['cart'])
        # if cart undefined, create cart.
        except:
            cart = {}
        # set empty variable for order
        items = []
        order = {'get_cart_total': 0,
                 'get_cart_quantity': 0, 'shipping': False}
        # add order values from cookie to above variable
        for key in cart:
            # update cart total items
            order['get_cart_quantity'] += cart[key]['quantity']
            # update cart total price
            product = Product.objects.get(id=key)
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

    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)


def checkout(request):
    # to dynaimcally render order info of logged in user
    if request.user.is_authenticated:
        # query customer instance associated with user
        customer = request.user.customer
        # query/create+query an order for above customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        # query all order items in above order
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0,
                 'get_cart_quantity': 0, 'shipping': False}

    context = {'items': items, 'order': order}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productID = data['productID']
    action = data['action']

    print(f'Action: {action}, Product ID: {productID}')

    # query relevant customer and product
    customer = request.user.customer
    product = Product.objects.get(id=productID)
    # query/create+query an incomplete order associated with above customer
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    # query/create+query an orderitem of above product associated with above order
    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    # based on above details, add or remove orderitem.
    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return redirect('')


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        # query relevant customer
        customer = request.user.customer
        # query/create+query an incomplete order associated with above customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        # query order total from data
        total = float(data['form']['total'])
        # set order transaction id
        order.transaction_id = transaction_id

        # security measure. Compare original total price with total sent to server from client

        if total == float(order.get_cart_total):
            order.complete = True

        order.save()
        # create shipping adress object for order
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode']
            )

    else:
        print('User not logged in')

    return JsonResponse('Payment complete', safe=False)
