<<<<<<< HEAD
import json
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.core.management import call_command
from .models import SleepRecord, WeatherRecord


def analytics(request):
    qs = SleepRecord.objects.values(
        'age', 'gender',
        'daily_screen_time_hours', 'sleep_duration_hours',
        'sleep_quality_score', 'stress_level',
    )
    df = pd.DataFrame(list(qs))

    if df.empty:
        return render(request, 'core/analytics.html', {'no_data': True})

    # Aggregation 1: Avg sleep quality by age group (answers Project 1 Q1)
    df['age_group'] = pd.cut(
        df['age'],
        bins=[0, 20, 30, 40, 50, 60, 100],
        labels=['<20', '20-29', '30-39', '40-49', '50-59', '60+'],
    )
    quality_by_age = (
        df.groupby('age_group', observed=True)['sleep_quality_score']
        .mean()
        .round(2)
    )
    quality_age_chart = {
        'labels': quality_by_age.index.astype(str).tolist(),
        'values': quality_by_age.fillna(0).tolist(),
    }

    # Aggregation 2: Avg stress level by daily screen time bucket (answers Project 1 Q2)
    df['screen_bucket'] = pd.cut(
        df['daily_screen_time_hours'],
        bins=[0, 2, 4, 6, 8, 24],
        labels=['0-2h', '2-4h', '4-6h', '6-8h', '8h+'],
    )
    stress_by_screen = (
        df.groupby('screen_bucket', observed=True)['stress_level']
        .mean()
        .round(2)
    )
    stress_screen_chart = {
        'labels': stress_by_screen.index.astype(str).tolist(),
        'values': stress_by_screen.fillna(0).tolist(),
    }

    # Aggregation 3: Record count by gender (doughnut chart)
    gender_counts = df['gender'].value_counts()
    gender_chart = {
        'labels': gender_counts.index.tolist(),
        'values': gender_counts.tolist(),
    }

    # Summary stats table: count, mean, min, max for 3 numeric fields
    stats_df = df[['sleep_duration_hours', 'stress_level', 'sleep_quality_score']].describe().round(2)
    summary = {
        col: {stat: float(stats_df.loc[stat, col]) for stat in ['count', 'mean', 'min', 'max']}
        for col in stats_df.columns
    }

    # Weather line chart — shown only when records exist
    weather_qs = WeatherRecord.objects.select_related('city').values(
        'city__name', 'date', 'temp_max',
    ).order_by('date')
    weather_df = pd.DataFrame(list(weather_qs))
    weather_chart_json = None
    if not weather_df.empty:
        weather_df['date'] = weather_df['date'].astype(str)
        pivot = weather_df.pivot_table(
            index='date', columns='city__name', values='temp_max', aggfunc='mean'
        )
        weather_chart_json = json.dumps({
            'labels': pivot.index.tolist(),
            'datasets': [
                {
                    'label': col,
                    'data': [round(float(v), 1) if pd.notna(v) else None for v in pivot[col]],
                }
                for col in pivot.columns
            ],
        })

    return render(request, 'core/analytics.html', {
        'no_data': False,
        'total_records': len(df),
        'quality_age_chart': json.dumps(quality_age_chart),
        'stress_screen_chart': json.dumps(stress_screen_chart),
        'gender_chart': json.dumps(gender_chart),
        'weather_chart': weather_chart_json,
        'summary': summary,
    })


@require_POST
@staff_member_required
def fetch_weather(request):
    try:
        call_command('fetch_data')
        messages.success(request, 'Weather data fetched successfully.')
    except Exception as e:
        messages.error(request, f'Fetch failed: {e}')
    return redirect('analytics')
=======
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from .forms import RecordForm
from django.contrib import messages

# Create your views here.
def home(request):
    context = {"message": "The real world context behind the dataset is that it explores the relationship between phone usage, sleep patterns, and stress levels. With there being a drastic increase in use of smartphones and usage of them, it is important to determine the affects they have on health."}
    return render(request, "core/home.html", context=context)

def create_record(request):
    if request.method == "POST":
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, "Record created successfully")
            return redirect("record_detail", pk = record.pk)

    else:
        form = RecordForm() #show empty form

    return render(request, "core/create_record.html", {"form": form})   #render form with errors if form is invalid

def update_record(request, pk):
    record = get_object_or_404(Record, pk=pk)    #model needed
    if request.method == "POST":
        form = RecordForm(request.POST, instance = record)
        if form.is_valid():
            form.save()
            messages.success(request, "Record updated successfully")
            return redirect("record_detail", pk = record.pk)
    else:
        form = RecordForm(instance=record) #show form with existing data
        return render(request, "core/create_record.html", {"form": form})   #render form with errors if form is invalid

def delete_record(request, pk):
    record = get_object_or_404(Record, pk = pk)  #model needed  
    if request.method == "POST":
        record.delete()
        messages.success(request, "Record deleted successfully")
        return redirect("records")
    else:
        return render(request, "core/record_confirm_delete.html", {"record": record})
# def records(request):
#     temp_data = [
#         {"city": "tallahassee", "date": "2026-04-19", "temp_max": 75.7, "temp_min": 57.9, "precipitation": 9},
#         {"city": "tallahassee", "date": "2026-04-20", "temp_max": 79.9, "temp_min": 50.9, "precipitation": 0},
#         {"city": "tallahassee", "date": "2026-04-21", "temp_max": 83.7, "temp_min": 52.5, "precipitation": 0},
#         {"city": "tallahassee", "date": "2026-04-22", "temp_max": 83.9, "temp_min": 57.2, "precipitation": 0},
#         {"city": "tallahassee", "date": "2026-04-23", "temp_max": 86.4, "temp_min": 56.0, "precipitation": 1},
#         {"city": "tallahassee", "date": "2026-04-24", "temp_max": 84.8, "temp_min": 58.7, "precipitation": 5},
#         {"city": "tallahassee", "date": "2026-04-25", "temp_max": 88.4, "temp_min": 60.1, "precipitation": 26},
#     ]
#     paginator = Paginator(temp_data, 20)
#     return render(request, "core/records.html", context= {"records": temp_data})

class RecordListView(ListView):
    paginate_by = 20
    # model = Record  # Assuming you have a Record model defined in your models.py
    template_name = "core/records.html"

    def get_queryset(self):
        return [
            {"id": 1, "city": "tallahassee", "date": "2026-04-19", "temp_max": 75.7, "temp_min": 57.9, "precipitation": 9},
            {"id": 2, "city": "tallahassee", "date": "2026-04-20", "temp_max": 79.9, "temp_min": 50.9, "precipitation": 0},
            {"id": 3, "city": "tallahassee", "date": "2026-04-21", "temp_max": 83.7, "temp_min": 52.5, "precipitation": 0},
            {"id": 4, "city": "tallahassee", "date": "2026-04-22", "temp_max": 83.9, "temp_min": 57.2, "precipitation": 0},
            {"id": 5, "city": "tallahassee", "date": "2026-04-23", "temp_max": 86.4, "temp_min": 56.0, "precipitation": 1},
            {"id": 6, "city": "tallahassee", "date": "2026-04-24", "temp_max": 84.8, "temp_min": 58.7, "precipitation": 5},
            {"id": 7, "city": "tallahassee", "date": "2026-04-25", "temp_max": 88.4, "temp_min": 60.1, "precipitation": 26},
            {"id": 8, "city": "tallahassee", "date": "2026-04-19", "temp_max": 75.7, "temp_min": 57.9, "precipitation": 9},
            {"id": 9, "city": "tallahassee", "date": "2026-04-20", "temp_max": 79.9, "temp_min": 50.9, "precipitation": 0},
            {"id": 10, "city": "tallahassee", "date": "2026-04-21", "temp_max": 83.7, "temp_min": 52.5, "precipitation": 0},
            {"id": 11, "city": "tallahassee", "date": "2026-04-22", "temp_max": 83.9, "temp_min": 57.2, "precipitation": 0},
            {"id": 12, "city": "tallahassee", "date": "2026-04-23", "temp_max": 86.4, "temp_min": 56.0, "precipitation": 1},
            {"id": 13, "city": "tallahassee", "date": "2026-04-24", "temp_max": 84.8, "temp_min": 58.7, "precipitation": 5},
            {"id": 14, "city": "tallahassee", "date": "2026-04-25", "temp_max": 88.4, "temp_min": 60.1, "precipitation": 26},
        ]

class RecordDetailView(DetailView):
    # model = Record  # Assuming you have a Record model defined in your models.py
    template_name = "core/record_detail.html"
    context_object_name = "record"