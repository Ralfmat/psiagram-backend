from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class testView(APIView):
    def get(self, request):
        return Response({"message": "This is a test view accessible only to authenticated users."})