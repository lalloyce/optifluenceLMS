from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionListAPIView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

class TransactionCreateAPIView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

class TransactionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

class TransactionReverseAPIView(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        transaction = self.get_object()
        if transaction.can_be_reversed():
            transaction.reverse_transaction()
            return Response({'status': 'transaction reversed'})
        return Response(
            {'error': 'Transaction cannot be reversed'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
