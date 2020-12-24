from PIL import Image
from django.db import models
 
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

User = get_user_model()


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class MinResalutionErrorException(Exception):
    pass


class MaxResalutionErrorException(Exception):
    pass


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(self, *args, **kwargs):

        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class().base_manager.all().order_by('id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(models=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )
        return products


class LatestProducts:
    object = LatestProductsManager()


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Meta:
        abstract = True

    MIN_RESOLUTION = (200, 200)
    MAX_RESOLUTION = (800, 800)
    MAX_IMAGE_SIZE = 31457

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    discription = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        imgage = self.image
        img = Image.open(imgage)
        min_width, min_height = self.MIN_RESOLUTION
        max_width, max_height = self.MAX_RESOLUTION
        if img.height < min_height or img.width < min_width:
            raise MinResalutionErrorException('Разрешения изображения меньше минимального!')
        if img.height > max_height or img.width > max_width:
            raise MaxResalutionErrorException('Разрешения изображения больше максимального!')

        # Обрезование изображение

        # image = self.image
        # img = Image.open(image)
        # new_image = img.convert('RGB')
        # resized_new_image = new_image.resize((500,500), Image.ANTIALIAS)
        # filestrieam = BytesIO()
        # resized_new_image.save(filestrieam, 'JPEG', quality=90)
        # filestrieam.seek(0)
        # name = '{}.{}'.format(*self.image.name.split('.'))
        # self.image = InMemoryUploadedFile(
        #    filestrieam, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestrieam), None
        # )
        super().save(*args, **kwargs)


class NoteBook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    image = models.ImageField(verbose_name='Изображения')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    processor_freq = models.CharField(max_length=255, verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Видеокарта')
    time_without_charge = models.CharField(max_length=255, verbose_name='Время работы аккумулятора')

    def __str__(self):
        return "{} : {} ".format(self.category.name, self.title)

    def get_absolute_url(self):
        return (self.id)


class Smartphone(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ')
    image = models.ImageField(verbose_name='Изображения')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    resolution = models.CharField(max_length=255, verbose_name='Разрешение экрана')
    accum_volume = models.CharField(max_length=255, verbose_name='Оперативная память')
    sd = models.BooleanField(default=True)
    sd_volume_max = models.CharField(max_length=255, verbose_name='Максимальный обьем встраивамой памяти')
    main_cam_mp = models.CharField(max_length=255, verbose_name='Главная камера')
    frontal_cam_mp = models.CharField(max_length=255, verbose_name='Фронтальная камера')

    def __str__(self):
        return " {} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Пакупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Обшая цена')

    def __str__(self):
        return "Продукт: {} (для корзины)".format(self.product.title)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)
    product = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.SlugField(unique=True)

    def __str__(self):
        return "Покупатель: {} {} ".format(self.user, self.phone)

    """
def getInfoById(self, category, newSlug):
    if self.category=='smartphones':
        for i in Smartphone.slug:
            if newSlug == i:


"""
