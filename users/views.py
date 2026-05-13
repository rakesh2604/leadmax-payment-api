from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User
from .serializers import UserSerializer


class UserListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'detail': 'No user matches the given id.'}, status=status.HTTP_404_NOT_FOUND)
        if user.pk != request.user.pk:
            return Response(
                {'detail': 'You can only view your own profile.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'detail': 'No user matches the given id.'}, status=status.HTTP_404_NOT_FOUND)

        if user != request.user:
            return Response(
                {'detail': 'You may only update your own profile.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'detail': 'No user matches the given id.'}, status=status.HTTP_404_NOT_FOUND)

        if user != request.user:
            return Response(
                {'detail': 'You may only delete your own account.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
