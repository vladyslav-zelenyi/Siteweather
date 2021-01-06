import logging

from rest_framework import status
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from siteweather.models import CustomUser
from siteweather.profile.serializers import SuperUserCustomUserSerializer, UpdateProfileSerializer, \
    UpdatePasswordSerializer
from siteweather.serializers import CustomUserSerializer

logger = logging.getLogger('django')


class UserProfile(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    parser_classes = (MultiPartParser, FormParser)
    template_name = 'profile/profile.html'

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serialized = self.get_serializer(profile).data
        return Response({'profile': serialized}, template_name='profile/profile.html')

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return SuperUserCustomUserSerializer
        else:
            return CustomUserSerializer


class UserProfileUpdate(GenericAPIView):
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

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = self.serializer_class(self.request.user, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'message': 'You have successfully updated your profile', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'errors': serializer.errors}, template_name=self.template_name,
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    def perform_update(self, serializer):
        serializer.save(self.request)


class UserPasswordUpdate(GenericAPIView):
    serializer_class = UpdatePasswordSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    parser_classes = [MultiPartParser, FormParser]
    template_name = 'profile/password_update.html'

    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(pk=self.request.user.pk)
        serializer = UpdatePasswordSerializer(user)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = UpdatePasswordSerializer(self.request.user, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            logger.warning(f'{self.request.user} updated his password')
            return Response({'message': 'Your password has been successfully updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': serializer.errors}, template_name=self.template_name,
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.pk)

    def perform_update(self, serializer):
        serializer.save(self.request)
