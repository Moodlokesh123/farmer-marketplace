import pandas as pd

from sklearn.linear_model import LinearRegression

from market.models import MarketPrice


def predict_price(crop_name, market_name=None):

    records = MarketPrice.objects.filter(
        crop_name__icontains=crop_name
    )

    if market_name:
        records = records.filter(
            market_name__icontains=market_name
        )

    records = records.order_by('date')

    if records.count() < 3:
        return None

    data = []

    for record in records:

        data.append({
            'date': record.date,
            'modal_price': float(
                record.modal_price
            )
        })

    df = pd.DataFrame(data)

    df['date'] = pd.to_datetime(
        df['date']
    )

    df['days'] = (
        df['date'] - df['date'].min()
    ).dt.days

    X = df[['days']]

    y = df['modal_price']

    model = LinearRegression()

    model.fit(X, y)

    next_day = df['days'].max() + 1

    prediction = model.predict(
        [[next_day]]
    )

    return round(
        float(prediction[0]),
        2
    )