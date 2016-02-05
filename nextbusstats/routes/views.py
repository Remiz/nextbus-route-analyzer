from django.shortcuts import render, get_object_or_404
from django_ajax.decorators import ajax
from django.db.models import Avg
from django.http import Http404
from .models import Route, Direction, Stop, Prediction


def routes_list(request):
    return render(request, 'routes/routes_list.html', {
        'routes': Route.objects.filter(monitored=True),
    })


def route(request, route_id):
    route = get_object_or_404(Route, pk=route_id)
    return render(request, 'routes/route.html', {
        'route': route,
    })


@ajax
def get_chart(request):
    if request.method != 'POST':
        raise Http404
    stop_id = request.POST.get('stop_selected', None)
    if stop_id in [None, '']:
        raise ValueError("stop_id can't be None or empty")
    stop = get_object_or_404(Stop, pk=stop_id)
    datetime_from = request.POST.get('datetime_from')
    datetime_to = request.POST.get('datetime_to')
    predictions = Prediction.objects.filter(
        stop=stop,
        posted_at__gt=datetime_from,
        posted_at__lte=datetime_to,
    )
    formated_predictions = []
    for prediction in predictions:
        formated_predictions.append({
            'posted_at': prediction.posted_at.isoformat(),
            'prediction': prediction.seconds,
        })
    return {'predictions': formated_predictions}


@ajax
def get_daily_average_chart(request):
    if request.method != 'POST':
        raise Http404
    stop_id = request.POST.get('stop_selected', None)
    if stop_id in [None, '']:
        raise ValueError("stop_id can't be None or empty")
    stop = get_object_or_404(Stop, pk=stop_id)
    avg_weekday = {}
    for weekday in range(1, 8):
        prediction_avg = Prediction.objects.filter(
            stop=stop,
            posted_at__week_day=weekday
        ).aggregate(Avg('seconds'))
        avg_weekday[weekday] = prediction_avg['seconds__avg']
    return {'avg_weekday': avg_weekday}


@ajax
def get_hourly_average_chart(request):
    if request.method != 'POST':
        raise Http404
    stop_id = request.POST.get('stop_selected', None)
    if stop_id in [None, '']:
        raise ValueError("stop_id can't be None or empty")
    stop = get_object_or_404(Stop, pk=stop_id)
    avg_hourly = {}
    for hour in range(0, 24):
        prediction_avg = Prediction.objects.filter(
            stop=stop,
            posted_at__hour=hour
        ).aggregate(Avg('seconds'))
        avg_hourly[hour] = prediction_avg['seconds__avg']
    print avg_hourly
    return {'avg_hourly': avg_hourly}


@ajax
def get_stops_from_direction(request):
    if request.method != 'POST':
        raise Http404
    direction_id = request.POST.get('direction', None)
    if direction_id in [None, '']:
        raise ValueError("direction_id can't be None or empty")
    direction = get_object_or_404(Direction, pk=direction_id)
    stops = []
    for stop in direction.stops.all().order_by('directionstop__position'):
        stops.append({
            'id': stop.id,
            'title': stop.title,
        })
    return {'stops': stops}
