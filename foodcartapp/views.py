import json

from django.http import JsonResponse
from django.templatetags.static import static
import phonenumbers
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

    required_fields = {
        'products': list,
        'firstname': str,
        'lastname': str,
        'phonenumber': str,
        'address': str,
    }

    missing_fields = [
        field for field in required_fields
        if field not in order_request.keys()
    ]

    if missing_fields:
        return Response({'message': f"{', '.join(missing_fields)} field missing"},
                        status=status.HTTP_400_BAD_REQUEST)

    empty_fields = [
        field for field in required_fields
        if not order_request[field]
    ]

    if empty_fields:
        return Response({'message': f"{', '.join(empty_fields)} field can`t be empty or None"},
                        status=status.HTTP_400_BAD_REQUEST)

    wrong_type_fields = [
        (field_name, field_type) for field_name, field_type in required_fields.items()
        if not isinstance(order_request[field_name], field_type)
    ]
    if wrong_type_fields:
        messages = [
            f'{field_name}: Это поле должно быть типа {field_type}'
            for field_name, field_type in wrong_type_fields
        ]
        return Response(
            {'message': ', '.join(messages)},
            status=status.HTTP_400_BAD_REQUEST
        )
    phonenumber = phonenumbers.parse(order_request['phonenumber'])
    if not phonenumbers.is_valid_number(phonenumber):
        return Response(
            {'message': 'phonenumber is wrong'},
            status=status.HTTP_400_BAD_REQUEST
        )

    order = Order.objects.create(
        first_name=order_request['firstname'],
        last_name=order_request['lastname'],
        phone=order_request['phonenumber'],
        address=order_request['address'],
    )

    for order_request_product in order_request['products']:
        try:
            product = Product.objects.get(pk=order_request_product['product'])
        except Product.DoesNotExist:
            return Response(
                {'message': 'Product not exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        OrderProduct.objects.create(
            order=order,
            product=product,
            quantity=order_request_product['quantity'],
            price=product.price
        )

    return JsonResponse({})
