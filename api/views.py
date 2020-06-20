"""
API Views
"""
import datetime
import json
from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Visit
from .serializers import VisitSerializer
from .visitdetails import Details


@api_view(['GET', 'POST'])
def greeter(request):
    try:
        if request.method == 'POST':
            return add_page_visit(request)
        elif request.method == 'GET':
            return get_page_visit(request)
        else:
            return Response(None, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    except ValueError as ex:
        return Response(ex.args[0], status.HTTP_400_BAD_REQUEST)


def add_page_visit(request):
    try:
        fulldate = datetime.datetime.now()
        year = fulldate.year
        month = fulldate.month
        day = fulldate.day
        domain = request.data.get('domain')
        page = request.data.get('page')
        try:
            visit_object = Visit.objects.get(
                domain=domain, year=year, month=month, day=day)
            details = json.loads(visit_object.details)
            details_updated = False
            for item in details:
                if item['page'] == page:
                    item['count'] += 1
                    details_updated = True
            if not details_updated:
                details.append({'page': page, 'count': 1})
            visit_object.details = json.dumps(
                details, default=lambda o: o.__dict__)
            visit_object.save()
        except ObjectDoesNotExist:
            visit_object = Visit()
            visit_object.domain = domain
            visit_object.year = year
            visit_object.month = month
            visit_object.day = day
            detail = [Details(page, 1)]
            visit_object.details = json.dumps(
                detail, default=lambda o: o.__dict__)
            visit_object.save()

        return Response(None, status.HTTP_201_CREATED)
    except ValueError as ex:
        return Response(ex.args[0], status.HTTP_400_BAD_REQUEST)


def get_page_visit(request):
    try:
        domain = request.data.get('domain')
        start_date = date.fromisoformat(request.data.get('startDate'))
        end_date = date.fromisoformat(request.data.get('endDate'))
        visits = Visit.objects.filter(
            year__range=(start_date.year, end_date.year),
            month__range=(start_date.month, end_date.month),
            day__range=(start_date.day, end_date.day),
            domain=domain)
        serializer = VisitSerializer(visits, many=True)
        data = serializer.data
        for item in data:
            item['details'] = json.loads(item['details'])
        return Response(serializer.data, status.HTTP_200_OK)
    except ValueError as ex:
        return Response(ex.args[0], status.HTTP_400_BAD_REQUEST)
