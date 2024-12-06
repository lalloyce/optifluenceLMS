from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Loan
from .serializers import LoanSerializer

class LoanListAPIView(generics.ListAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

class LoanCreateAPIView(generics.CreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

class LoanDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

class LoanApproveAPIView(generics.UpdateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        loan = self.get_object()
        loan.status = 'approved'
        loan.save()
        return Response({'status': 'loan approved'})

class LoanRejectAPIView(generics.UpdateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        loan = self.get_object()
        loan.status = 'rejected'
        loan.save()
        return Response({'status': 'loan rejected'})

class LoanDisburseAPIView(generics.UpdateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        loan = self.get_object()
        loan.status = 'disbursed'
        loan.save()
        return Response({'status': 'loan disbursed'})

class LoanScheduleAPIView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        loan = self.get_object()
        schedule = loan.get_repayment_schedule()
        return Response(schedule)
