import React from 'react';
import { LoanCard } from '../components/loans/LoanCard';
import { PaymentHistory } from '../components/payments/PaymentHistory';
import { Loan, Payment } from '../types';

// Mock data - replace with actual API calls
const mockLoans: Loan[] = [
  {
    id: '1234567890',
    userId: 'user123',
    amount: 10000,
    term: 12,
    status: 'active',
    interestRate: 0.15,
    startDate: new Date('2024-01-01'),
    endDate: new Date('2024-12-31'),
    nextPaymentDate: new Date('2024-03-01'),
    totalPayable: 11500,
    remainingAmount: 8625
  }
];

const mockPayments: Payment[] = [
  {
    id: 'pay123',
    loanId: '1234567890',
    amount: 958.33,
    date: new Date('2024-02-01'),
    status: 'completed',
    type: 'scheduled'
  },
  {
    id: 'pay124',
    loanId: '1234567890',
    amount: 958.33,
    date: new Date('2024-01-01'),
    status: 'completed',
    type: 'scheduled'
  }
];

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back! Here's an overview of your loans and recent activities.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {mockLoans.map(loan => (
          <LoanCard key={loan.id} loan={loan} />
        ))}
      </div>

      <div className="mt-8">
        <PaymentHistory payments={mockPayments} />
      </div>
    </div>
  );
}