from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Null&Black fields temporarily set as Null to avoid db errors. Change in future as needed.


class Customer(models.Model):
    # create rlationship b/w inbuilt User model
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=240, blank=True)
    email = models.CharField(max_length=240, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=240, blank=True)
    price = models.DecimalField(
        decimal_places=2, max_digits=12, null=True, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    # to ensure app no crash if no image for product
    @property  # this is a property decorator. It allows func's to be called as attribs
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    # 1 order can be placed by 1 customer, 1 customer can have many orders
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=True)
    transaction_id = models.CharField(max_length=240, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_quantity(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    # check if item is digital or not. Accordingly will ask for shipping details.
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for orderitem in orderitems:
            if not orderitem.product.digital:
                shipping = True
            pass
        return shipping


class OrderItem(models.Model):
    # 1 order item is only 1 product, 1 product can be many order items
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True)
    # 1 order item can only be in 1 order, 1 order can have many order items
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    # 1 address belongs to 1 customer, 1 customer can have many address'
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    # relationship unclear - 1 address has 1 order, 1 order has many address'?
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=240, blank=True)
    city = models.CharField(max_length=240, blank=True)
    state = models.CharField(max_length=240, blank=True)
    zipcode = models.CharField(max_length=240, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
