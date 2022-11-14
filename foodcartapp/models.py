from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import ExpressionWrapper, F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def get_price(self):
        return self.annotate(
            price=Sum(
                ExpressionWrapper(
                    F('products__price') * F('products__quantity'),
                    output_field=models.PositiveIntegerField()
                )
            )
        )

    def get_available_restaurants(self):
        restaurant_menu_items = RestaurantMenuItem.objects.select_related(
            'restaurant', 'product'
        )
        for order in self:
            for order_product in order.products.all():
                product_restaurants = set(
                    menu_item.restaurant for menu_item in restaurant_menu_items
                    if order_product.product == menu_item.product
                    and menu_item.availability
                )
            order.available_restaurants = product_restaurants
        return self


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('New', 'Новый'),
        ('Clarified', 'Уточнён'),
        ('Packed', 'Собран'),
        ('Delivered', 'Доставлен'),
    )

    PAYMENT_TYPE_CHOICES = (
        ('Cash', 'Наличными'),
        ('Electronically', 'Электронно')
    )

    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    phonenumber = PhoneNumberField('Номер телефона', db_index=True)
    address = models.CharField('Адрес', max_length=100)
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=ORDER_STATUS_CHOICES,
        default='New',
        db_index=True,
    )
    comment = models.TextField('Комментарий', blank=True)

    registrated_at = models.DateTimeField('Зарегестрирован в', default=timezone.now, db_index=True)
    called_at = models.DateTimeField('Утверждём в', null=True, blank=True, db_index=True)
    delivered_at = models.DateTimeField('Доставлен в', null=True, blank=True, db_index=True)

    payment_type = models.CharField(
        'Способ оплаты',
        max_length=15,
        choices=PAYMENT_TYPE_CHOICES,
        default='Cash',
        db_index=True,
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='Ресторан',
        help_text='Ресторан выполнения заказа',
        blank=True,
        null=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname}, {self.address}'


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Продукт',
    )
    quantity = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        'Цена',
        validators=[MinValueValidator(0)],
        max_digits=8,
        decimal_places=2,
    )

    class Meta:
        verbose_name = 'Продукт заказа'
        verbose_name_plural = 'Продукты заказа'

    def __str__(self):
        return f'{self.product} для {self.order}'
