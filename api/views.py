import datetime
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
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
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


def add_page_visit(request):
    try:
        fulldate = datetime.datetime.now()
        year = fulldate.year
        month = fulldate.month
        day = fulldate.day
        domain = request.data.get('domain')
        page = request.data.get('page')
        try:
            v = Visit.objects.get(
                domain=domain, year=year, month=month, day=day)
            details = json.loads(v.details)
            detailsUpdated = False
            for item in details:
                if item['page'] == page:
                    item['count'] += 1
                    detailsUpdated = True
            if not detailsUpdated:
                details.append({'page': page, 'count': 1})
            v.details = json.dumps(
                details, default=lambda o: o.__dict__)
            v.save()
        except ObjectDoesNotExist:
            visitObject = Visit()
            visitObject.domain = domain
            visitObject.year = year
            visitObject.month = month
            visitObject.day = day
            detail = [Details(page, 1)]
            visitObject.details = json.dumps(
                detail, default=lambda o: o.__dict__)
            visitObject.save()

        return Response(None, status.HTTP_201_CREATED)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


def get_page_visit(request):
    try:
        visits = Visit.objects.all()
        serializer = VisitSerializer(visits, many=True)
        data = serializer.data
        for item in data:
            item['details'] = json.loads(item['details'])
        return Response(serializer.data, status.HTTP_200_OK)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)
