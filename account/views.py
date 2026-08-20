from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from account.serializers import UserSerializer
from rest_framework.generics import CreateAPIView
from account.serializers import RegisterSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser



User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)




class RegisterView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer