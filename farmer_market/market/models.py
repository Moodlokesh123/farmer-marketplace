from django.db import models


class Farmer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Buyer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


CATEGORY_CHOICES = [
    ('Grains', 'Grains'),
    ('Fruits', 'Fruits'),
    ('Vegetables', 'Vegetables'),
    ('Organic', 'Organic'),
]

class Crop(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    crop_name = models.CharField(max_length=100)
    price = models.FloatField()
    quantity = models.IntegerField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='crops/', null=True, blank=True)


class Order(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, default="Pending")
    payment_status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return self.crop.crop_name

class Cart(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.crop.crop_name
class MarketPrice(models.Model):

    crop_name = models.CharField(max_length=100)

    market_name = models.CharField(max_length=150)

    district = models.CharField(max_length=100)

    state = models.CharField(max_length=100, default="Telangana")

    date = models.DateField()

    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    modal_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    demand = models.CharField(
        max_length=20,
        choices=[
            ("Low", "Low"),
            ("Medium", "Medium"),
            ("High", "High"),
        ],
        default="Medium"
    )

    supply = models.CharField(
        max_length=20,
        choices=[
            ("Low", "Low"),
            ("Medium", "Medium"),
            ("High", "High"),
        ],
        default="Medium"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {} - {}".format(
            self.crop_name,
            self.market_name,
            self.date
        )  
class PriceAlert(models.Model):

    farmer = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE
    )

    crop_name = models.CharField(
        max_length=100
    )

    target_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    market_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):

        return "{} - ₹{}".format(
            self.crop_name,
            self.target_price
        )      
    