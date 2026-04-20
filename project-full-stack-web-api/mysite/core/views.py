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