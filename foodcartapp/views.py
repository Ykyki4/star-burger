import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderProduct


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_request = request.data

    try:
        order_products = order_request['products']
    except KeyError:
        return Response(
            {"message": "No product list in the order"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not isinstance(order_products, list):
        return Response(
            {"message": "Products must be a list"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not order_request['products']:
        return Response({"message": "Products can`t be empty"}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        first_name=order_request['firstname'],
        last_name=order_request['lastname'],
        phone=order_request['phonenumber'],
        address=order_request['address'],
    )

    for order_request_product in order_products:
        product = Product.objects.get(pk=order_request_product['product'])
        OrderProduct.objects.create(
            order=order,
            product=product,
            quantity=order_request_product['quantity'],
            price=product.price
        )

    return JsonResponse({})
