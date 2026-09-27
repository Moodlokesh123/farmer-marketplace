from django.shortcuts import render, redirect, get_object_or_404
from .models import Farmer, Buyer, Crop, Order, MarketPrice, PriceAlert
from .forms import CropForm, FarmerForm, BuyerForm
from ml.price_prediction import predict_price

# -----------------------------
# Home Page
# -----------------------------
def home(request):
    return render(request, 'home.html')


# -----------------------------
# Farmer Section
# -----------------------------
def register_farmer(request):
    if request.method == 'POST':
        form = FarmerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = FarmerForm()
    return render(request, 'register_farmer.html', {'form': form})


def farmer_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            farmer = Farmer.objects.get(email=email, password=password)
            request.session['farmer_id'] = farmer.id
            return redirect('farmer_dashboard')
        except Farmer.DoesNotExist:
            return render(request, 'farmer_login.html',
                          {'error': 'Invalid email or password'})
    return render(request, 'farmer_login.html')


def farmer_dashboard(request):
    if 'farmer_id' not in request.session:
        return redirect('farmer_login')

    farmer = Farmer.objects.get(id=request.session['farmer_id'])
    crops = Crop.objects.filter(farmer=farmer)
    orders = Order.objects.filter(crop__farmer=farmer)

    return render(request, 'farmer_dashboard.html', {
        'crops': crops,
        'orders': orders
    })


def add_crop(request):
    if 'farmer_id' not in request.session:
        return redirect('farmer_login')

    form = CropForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        crop = form.save(commit=False)
        crop.farmer_id = request.session['farmer_id']
        crop.save()
        return redirect('farmer_dashboard')

    return render(request, 'add_crop.html', {'form': form})


def edit_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id)

    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES, instance=crop)
        if form.is_valid():
            form.save()
            return redirect('farmer_dashboard')
    else:
        form = CropForm(instance=crop)

    return render(request, 'edit_crop.html', {'form': form})


def delete_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id)
    crop.delete()
    return redirect('farmer_dashboard')


def farmer_orders(request):
    if 'farmer_id' not in request.session:
        return redirect('farmer_login')

    orders = Order.objects.filter(crop__farmer_id=request.session['farmer_id'])
    return render(request, 'farmer_orders.html', {'orders': orders})


# -----------------------------
# Marketplace
# -----------------------------
def marketplace(request):
    crops = Crop.objects.all()

    # Search
    query = request.GET.get('q')
    if query:
        crops = crops.filter(crop_name__icontains=query)

    # Price filter
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    if min_price and max_price:
        crops = crops.filter(price__range=(min_price, max_price))

    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        crops = crops.filter(category_id=category_id)

    return render(request, 'marketplace.html', {'crops': crops})


# -----------------------------
# Cart System
# -----------------------------
def add_to_cart(request, crop_id):
    cart = request.session.get('cart', {})

    if str(crop_id) in cart:
        cart[str(crop_id)] += 1
    else:
        cart[str(crop_id)] = 1

    request.session['cart'] = cart
    return redirect('view_cart')


def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for crop_id, quantity in cart.items():
        crop = Crop.objects.get(id=crop_id)
        subtotal = crop.price * quantity
        total += subtotal

        cart_items.append({
            'crop': crop,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def increase_quantity(request, crop_id):
    cart = request.session.get('cart', {})
    if str(crop_id) in cart:
        cart[str(crop_id)] += 1
    request.session['cart'] = cart
    return redirect('view_cart')


def decrease_quantity(request, crop_id):
    cart = request.session.get('cart', {})
    if str(crop_id) in cart:
        cart[str(crop_id)] -= 1
        if cart[str(crop_id)] <= 0:
            del cart[str(crop_id)]
    request.session['cart'] = cart
    return redirect('view_cart')


def remove_from_cart(request, crop_id):
    cart = request.session.get('cart', {})
    if str(crop_id) in cart:
        del cart[str(crop_id)]
    request.session['cart'] = cart
    return redirect('view_cart')


# -----------------------------
# Buy Now
# -----------------------------
def buy_now(request, crop_id):
    request.session['buy_now_crop'] = crop_id
    return redirect('payment')


# -----------------------------
# Place Order From Cart
# -----------------------------
def place_order(request):
    request.session['cart_order'] = True
    return redirect('payment')


# -----------------------------
# Payment Page
# -----------------------------
def payment(request):

    if 'buyer_id' not in request.session:
        return redirect('buyer_login')

    total = 0
    crop = None
    quantity = 1
    cart_items = []

    # BUY NOW
    if 'buy_now_crop' in request.session:

        crop = get_object_or_404(
            Crop,
            id=request.session['buy_now_crop']
        )

        total = crop.price * quantity

    # CART ORDER
    elif 'cart_order' in request.session:

        cart = request.session.get('cart', {})

        for crop_id, quantity in cart.items():

            crop_obj = get_object_or_404(
                Crop,
                id=crop_id
            )

            subtotal = crop_obj.price * quantity
            total += subtotal

            cart_items.append({
                'crop': crop_obj,
                'quantity': quantity,
                'subtotal': subtotal
            })

    if request.method == 'POST':

        buyer = get_object_or_404(
            Buyer,
            id=request.session['buyer_id']
        )

        # Buy Now
        if 'buy_now_crop' in request.session:

            crop = get_object_or_404(
                Crop,
                id=request.session['buy_now_crop']
            )

            Order.objects.create(
                buyer=buyer,
                crop=crop,
                quantity=1,
                status='Pending'
            )

            del request.session['buy_now_crop']

        # Cart
        elif 'cart_order' in request.session:

            cart = request.session.get('cart', {})

            for crop_id, quantity in cart.items():

                crop = get_object_or_404(
                    Crop,
                    id=crop_id
                )

                Order.objects.create(
                    buyer=buyer,
                    crop=crop,
                    quantity=quantity,
                    status='Pending'
                )

            request.session['cart'] = {}
            del request.session['cart_order']

        return redirect('payment_success')

    return render(request, 'payment.html', {
        'crop': crop,
        'quantity': quantity,
        'cart_items': cart_items,
        'total': total
    })

# -----------------------------
# Buyer Section
# -----------------------------
def register_buyer(request):
    if request.method == "POST":
        form = BuyerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('buyer_login')
    else:
        form = BuyerForm()

    return render(request, 'register_buyer.html', {'form': form})


def buyer_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        buyer = Buyer.objects.filter(email=email, password=password).first()

        if buyer:
            request.session['buyer_id'] = buyer.id
            return redirect('buyer_dashboard')
        else:
            return render(request, 'buyer_login.html',
                          {'error': 'Invalid credentials'})

    return render(request, 'buyer_login.html')


def buyer_dashboard(request):
    if 'buyer_id' not in request.session:
        return redirect('buyer_login')

    crops = Crop.objects.all()
    orders = Order.objects.filter(buyer_id=request.session['buyer_id'])

    return render(request, 'buyer_dashboard.html', {
        'crops': crops,
        'orders': orders
    })


def buyer_orders(request):
    if 'buyer_id' not in request.session:
        return redirect('buyer_login')

    buyer = Buyer.objects.get(id=request.session['buyer_id'])
    orders = Order.objects.filter(buyer=buyer)

    return render(request, 'buyer_orders.html', {'orders': orders})


# -----------------------------
# Order Status Update (Farmer)
# -----------------------------
def approve_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Approved"
    order.save()
    return redirect('farmer_orders')


def reject_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Rejected"
    order.save()
    return redirect('farmer_orders')


def deliver_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Delivered"
    order.save()
    return redirect('farmer_orders')
def payment_success(request):
    return render(request, 'payment_success.html')
def price_discovery(request):

    # --------------------------------
    # GET ALL MARKET PRICES
    # --------------------------------

    prices = MarketPrice.objects.all().order_by('-date')


    # --------------------------------
    # GET FILTER VALUES
    # --------------------------------

    crop = request.GET.get('crop', '').strip()

    state = request.GET.get('state', '').strip()

    district = request.GET.get('district', '').strip()

    market = request.GET.get('market', '').strip()


    # --------------------------------
    # APPLY FILTERS
    # --------------------------------

    if crop:

        prices = prices.filter(
            crop_name__icontains=crop
        )


    if state:

        prices = prices.filter(
            state__icontains=state
        )


    if district:

        prices = prices.filter(
            district__icontains=district
        )


    if market:

        prices = prices.filter(
            market_name__icontains=market
        )


    # --------------------------------
    # MARKET COMPARISON
    # --------------------------------

    comparison = []

    max_modal = 0


    # Find highest modal price

    for price in prices:

        modal_price = float(
            price.modal_price
        )

        if modal_price > max_modal:

            max_modal = modal_price


    # Calculate bar width

    for price in prices:

        modal_price = float(
            price.modal_price
        )


        if max_modal > 0:

            bar_width = (
                modal_price / max_modal
            ) * 100

        else:

            bar_width = 0


        comparison.append({

            'market':
                price.market_name,

            'min_price':
                price.min_price,

            'max_price':
                price.max_price,

            'modal_price':
                price.modal_price,

            'bar_width':
                round(
                    bar_width,
                    2
                ),

        })


    # --------------------------------
    # LOCATION OPTIONS
    # --------------------------------

    states = (
        MarketPrice.objects
        .values_list(
            'state',
            flat=True
        )
        .distinct()
        .order_by('state')
    )


    districts = (
        MarketPrice.objects
        .values_list(
            'district',
            flat=True
        )
        .distinct()
        .order_by('district')
    )


    markets = (
        MarketPrice.objects
        .values_list(
            'market_name',
            flat=True
        )
        .distinct()
        .order_by('market_name')
    )


    crops = (
        MarketPrice.objects
        .values_list(
            'crop_name',
            flat=True
        )
        .distinct()
        .order_by('crop_name')
    )


    # --------------------------------
    # CONTEXT
    # --------------------------------

    context = {

        'prices':
            prices,

        'comparison':
            comparison,

        'crop':
            crop,

        'state':
            state,

        'district':
            district,

        'market':
            market,

        'states':
            states,

        'districts':
            districts,

        'markets':
            markets,

        'crops':
            crops,

    }


    return render(
        request,
        'price_discovery.html',
        context
    )
def price_trends(request):

    crop = request.GET.get('crop', '').strip()

    prices = MarketPrice.objects.all().order_by('date')

    if crop:
        prices = prices.filter(
            crop_name__icontains=crop
        )

    trend_data = []

    for price in prices:

        trend_data.append({
            'date': price.date.strftime('%Y-%m-%d'),
            'min_price': float(price.min_price),
            'max_price': float(price.max_price),
            'modal_price': float(price.modal_price),
        })

    context = {
        'prices': prices,
        'trend_data': trend_data,
        'crop': crop,
    }

    return render(
        request,
        'price_trends.html',
        context
    )
def demand_supply(request):

    prices = MarketPrice.objects.all().order_by('-date')

    crop = request.GET.get('crop', '').strip()
    state = request.GET.get('state', '').strip()
    district = request.GET.get('district', '').strip()
    market = request.GET.get('market', '').strip()

    # -----------------------------
    # FILTERS
    # -----------------------------

    if crop:
        prices = prices.filter(
            crop_name__icontains=crop
        )

    if state:
        prices = prices.filter(
            state__icontains=state
        )

    if district:
        prices = prices.filter(
            district__icontains=district
        )

    if market:
        prices = prices.filter(
            market_name__icontains=market
        )


    # -----------------------------
    # DEMAND COUNTS
    # -----------------------------

    high_demand = prices.filter(
        demand='High'
    ).count()

    medium_demand = prices.filter(
        demand='Medium'
    ).count()

    low_demand = prices.filter(
        demand='Low'
    ).count()


    # -----------------------------
    # SUPPLY COUNTS
    # -----------------------------

    high_supply = prices.filter(
        supply='High'
    ).count()

    medium_supply = prices.filter(
        supply='Medium'
    ).count()

    low_supply = prices.filter(
        supply='Low'
    ).count()


    # -----------------------------
    # CONTEXT
    # -----------------------------

    context = {

        'prices': prices,

        'crop': crop,

        'state': state,

        'district': district,

        'market': market,

        'high_demand': high_demand,

        'medium_demand': medium_demand,

        'low_demand': low_demand,

        'high_supply': high_supply,

        'medium_supply': medium_supply,

        'low_supply': low_supply,

    }


    return render(
        request,
        'demand_supply.html',
        context
    )
def price_alerts(request):

    if 'farmer_id' not in request.session:
        return redirect('farmer_login')

    farmer = Farmer.objects.get(
        id=request.session['farmer_id']
    )

    alerts = PriceAlert.objects.filter(
        farmer=farmer
    ).order_by('-created_at')

    triggered_alerts = []

    for alert in alerts:

        prices = MarketPrice.objects.filter(
            crop_name__icontains=alert.crop_name
        )

        if alert.market_name:

            prices = prices.filter(
                market_name__icontains=alert.market_name
            )

        for price in prices:

            if price.modal_price >= alert.target_price:

                triggered_alerts.append({
                    'alert': alert,
                    'price': price,
                })

    context = {
        'alerts': alerts,
        'triggered_alerts': triggered_alerts,
    }

    return render(
        request,
        'price_alerts.html',
        context
    )
def create_price_alert(request):

    if 'farmer_id' not in request.session:
        return redirect('farmer_login')

    farmer = Farmer.objects.get(
        id=request.session['farmer_id']
    )

    if request.method == 'POST':

        crop_name = request.POST.get('crop_name', '').strip()
        target_price = request.POST.get('target_price', '').strip()
        market_name = request.POST.get('market_name', '').strip()

        if crop_name and target_price:

            try:
                target_price = float(target_price)

                if target_price > 0:

                    PriceAlert.objects.create(
                        farmer=farmer,
                        crop_name=crop_name,
                        target_price=target_price,
                        market_name=market_name
                    )

                    return redirect('price_alerts')

            except ValueError:
                pass

    return redirect('price_alerts')
def price_prediction(request):

    crop = request.GET.get('crop', '').strip()
    market = request.GET.get('market', '').strip()

    prediction = None

    prices = MarketPrice.objects.all().order_by('-date')

    if crop:
        prices = prices.filter(
            crop_name__icontains=crop
        )

    if market:
        prices = prices.filter(
            market_name__icontains=market
        )

    if crop:
        prediction = predict_price(crop)

    crops = (
        MarketPrice.objects
        .values_list(
            'crop_name',
            flat=True
        )
        .distinct()
        .order_by('crop_name')
    )

    markets = (
        MarketPrice.objects
        .values_list(
            'market_name',
            flat=True
        )
        .distinct()
        .order_by('market_name')
    )

    recent_prices = prices[:10]

    context = {
        'crop': crop,
        'market': market,
        'prediction': prediction,
        'prices': prices,
        'recent_prices': recent_prices,
        'crops': crops,
        'markets': markets,
    }

    return render(
        request,
        'price_prediction.html',
        context
    )
from django.http import JsonResponse
from .models import MarketPrice


def voice_assistant(request):
    return render(request, 'voice_assistant.html')


def voice_price_query(request):
    crop = request.GET.get('crop', '').strip()

    if not crop:
        return JsonResponse({
            'success': False,
            'message': 'Please provide a crop name.'
        })

    prices = MarketPrice.objects.filter(
        crop_name__icontains=crop
    ).order_by('-date')

    if not prices.exists():
        return JsonResponse({
            'success': False,
            'message': 'No price information found for this crop.'
        })

    latest_date = prices.first().date

    latest_prices = prices.filter(date=latest_date)

    highest = max(latest_prices, key=lambda x: float(x.modal_price))

    message = (
        "{} market price is available from {} to {} per quintal. "
        "Highest modal price found at {} market is {} per quintal."
    ).format(
        crop,
        min(float(p.modal_price) for p in latest_prices),
        max(float(p.modal_price) for p in latest_prices),
        highest.market_name,
        highest.modal_price
    )

    return JsonResponse({
        'success': True,
        'message': message
    })
# =========================================================
# VOICE-BASED CROP SELLING
# =========================================================

def voice_sell(request):
    if 'farmer_id' not in request.session:
        return redirect('farmer_login')

    return render(request, 'voice_sell_crop.html')


def voice_sell_crop(request):

    # Farmer must be logged in
    if 'farmer_id' not in request.session:
        return JsonResponse({
            'success': False,
            'message': 'Farmer login required.'
        }, status=401)

    # Only POST is allowed
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request.'
        }, status=405)

    # Get data from voice-selling page
    crop_name = request.POST.get('crop_name', '').strip()
    quantity = request.POST.get('quantity', '').strip()
    price = request.POST.get('price', '').strip()

    # Validate required fields
    if not crop_name or not quantity or not price:
        return JsonResponse({
            'success': False,
            'message': 'Crop, quantity and price are required.'
        })

    # Convert numbers
    try:
        quantity_value = float(quantity)
        price_value = float(price)

        if quantity_value <= 0 or price_value <= 0:
            raise ValueError

    except (ValueError, TypeError):

        return JsonResponse({
            'success': False,
            'message': 'Please provide valid quantity and price.'
        })

    # Create crop listing
    Crop.objects.create(
        farmer_id=request.session['farmer_id'],
        crop_name=crop_name,
        quantity=quantity_value,
        price=price_value
    )

    return JsonResponse({
        'success': True,
        'message': 'Crop listed successfully.'
    })    