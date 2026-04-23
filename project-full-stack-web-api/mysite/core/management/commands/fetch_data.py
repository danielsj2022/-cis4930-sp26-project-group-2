from django.core.management.base import BaseCommand
from django.db import transaction
import requests
from core.models import City, Record, DataRun


CITIES = [
    {'name': 'Tallahassee', 'lat': 30.4383, 'lon': -84.2807},
    {'name': 'Dallas', 'lat': 32.7831, 'lon': -96.8067},
    {'name': 'New York', 'lat': 40.7143, 'lon': -74.006},
]

API_URL = 'https://api.open-meteo.com/v1/forecast'


class Command(BaseCommand):
    help = 'Fetch 7-day weather forecast from Open-Meteo and save to database'

    def handle(self, *args, **options):
        run = DataRun.objects.create(source='api')

        for city_info in CITIES:
            try:
                resp = requests.get(
                    API_URL,
                    params={
                        'latitude': city_info['lat'],
                        'longitude': city_info['lon'],
                        'daily': [
                            'temperature_2m_max',
                            'temperature_2m_min',
                            'precipitation_probability_max',
                        ],
                        'timezone': 'America/New_York',
                        'temperature_unit': 'fahrenheit',
                    },
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()

                daily = data.get('daily', {})
                dates = daily.get('time', [])
                temp_max_list = daily.get('temperature_2m_max', [])
                temp_min_list = daily.get('temperature_2m_min', [])
                precip_list = daily.get('precipitation_probability_max', [])

                city, _ = City.objects.get_or_create(name=city_info['name'])

                saved = 0
                with transaction.atomic():
                    for i, date_str in enumerate(dates):
                        _, created = Record.objects.update_or_create(
                            city=city,
                            date=date_str,
                            defaults={
                                'temp_max': temp_max_list[i] if i < len(temp_max_list) else 0,
                                'temp_min': temp_min_list[i] if i < len(temp_min_list) else 0,
                                'precipitation': precip_list[i] if i < len(precip_list) else 0,
                                'source': 'api',
                                'run': run,
                            },
                        )
                        if created:
                            saved += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fetched {city_info["name"]}: {saved} new records saved'
                    )
                )

            except requests.exceptions.Timeout:
                self.stderr.write(
                    self.style.ERROR(f'Timeout fetching {city_info["name"]} — skipping')
                )
            except requests.exceptions.RequestException as e:
                self.stderr.write(
                    self.style.ERROR(f'Error fetching {city_info["name"]}: {e}')
                )
