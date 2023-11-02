weather = ['current', 'forecast']
metrics = [
    'temperature',
    'wind',
    'other',
    'pollution',
]
cities = [
    'valencia',
    'barcelona',
    'madrid',
]


def return_topics():
    topics = {
        f'current/city/{index + 1}/metric/{metric_index + 1}': f'current/city/{city}/metric/{metric}'
        for index, city in enumerate(cities)
        for metric_index, metric in enumerate(metrics)
    }
    return topics


topics_pub = [
    'current/city/valencia/metric/temperature',
    'current/city/valencia/metric/wind',
    'current/city/valencia/metric/other',
    'current/city/valencia/metric/pollution',

    'current/city/barcelona/metric/temperature',
    'current/city/barcelona/metric/wind',
    'current/city/barcelona/metric/other',
    'current/city/barcelona/metric/pollution',

    'current/city/madrid/metric/temperature',
    'current/city/madrid/metric/wind',
    'current/city/madrid/metric/other',
    'current/city/madrid/metric/pollution',

    'forecast/city/valencia',
    'forecast/city/barcelona',
    'forecast/city/madrid',

    'current/city/valencia/metric/#',
    'current/city/barcelona/metric/#',
    'current/city/madrid/metric/#',

    'current/city/#',
    'forecast/city/#',

]
