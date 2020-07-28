from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime

# Create your views here.

from .models import *
from .utils import cartData, cookieCart


def store(request):
    # query all products
    products = Product.objects.all()

    # to dynaimcally render order info of logged in/guest user
    data = cartData(request)

    order = data['order']

    context = {'products': products, 'order': order}
    return render(request, 'store/store.html', context)


def cart(request):
    # to dynaimcally render order info of logged in/guest user
    data = cartData(request)

    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)


def checkout(request):
    # to dynaimcally render order info of logged in/guest user
    data = cartData(request)

    order = data['order']
    items = data['items']

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


# saving all order info to db
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        # query relevant customer
        customer = request.user.customer
        # query/create+query an incomplete order associated with above customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        print('User Anon')

        print('cookies: ', request.COOKIES)
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

    # query order total from data
    total = float(data['form']['total'])
    # set order transaction id
    order.transaction_id = transaction_id

    # security measure. Compare original total price with total sent to server from client
    if total == float(order.get_cart_total):
        order.complete = True

        order.save()

    return {}
