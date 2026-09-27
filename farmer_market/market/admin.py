from django.contrib import admin

from .models import (
    Farmer,
    Buyer,
    Crop,
    Order,
    MarketPrice,
    PriceAlert
)


admin.site.register(Farmer)
admin.site.register(Buyer)
admin.site.register(Crop)
admin.site.register(Order)
admin.site.register(MarketPrice)
admin.site.register(PriceAlert)