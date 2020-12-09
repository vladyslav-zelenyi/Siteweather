import logging

from django.shortcuts import redirect
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import status, permissions
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from siteweather.models import CustomUser
from siteweather.serializers import CustomUserSerializer, UpdateProfileSerializer, \
    UpdatePasswordSerializer

logger = logging.getLogger('django')


class UserProfile(RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    parser_classes = (MultiPartParser, FormParser)
    template_name = 'profile/profile.html'

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serialized = self.get_serializer(profile).data
        return Response({'profile': serialized}, template_name='profile/profile.html')


class UserProfileUpdate(UpdateAPIView):
    serializer_class = UpdateProfileSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'profile/profile_update.html'
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(pk=self.request.user.pk)
        serializer = UpdateProfileSerializer(user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = UpdateProfileSerializer(self.request.user, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(data=serializer.data, template_name=self.template_name, status=status.HTTP_200_OK)
        else:
            return Response({'errors': serializer.errors}, template_name=self.template_name,
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    def perform_update(self, serializer):
        serializer.save(self.request)


class UserPasswordUpdate(UpdateAPIView):
    serializer_class = UpdatePasswordSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    parser_classes = (MultiPartParser, FormParser)
    template_name = 'profile/password_update.html'

    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(pk=self.request.user.pk)
        serializer = UpdatePasswordSerializer(user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = UpdatePasswordSerializer(self.request.user, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            logger.warning(f'{self.request.user} updated his password')
            return redirect('siteweather:home')
        else:
            return Response({'errors': serializer.errors}, template_name=self.template_name,
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        # todo: Correct response, remove "PATCH" (how?)

    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.pk)

    def perform_update(self, serializer):
        serializer.save(self.request)


schema_view = get_schema_view(
   openapi.Info(
      title="SWAGGER",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
