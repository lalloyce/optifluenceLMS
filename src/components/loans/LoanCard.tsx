import React from 'react';
import { Calendar, DollarSign } from 'lucide-react';
import { Loan } from '../../types';

interface LoanCardProps {
  loan: Loan;
}

export function LoanCard({ loan }: LoanCardProps) {
  const getStatusColor = (status: Loan['status']) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'active': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Loan #{loan.id.slice(0, 8)}
          </h3>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(loan.status)}`}>
            {loan.status.charAt(0).toUpperCase() + loan.status.slice(1)}
          </span>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Total Amount</p>
          <p className="text-xl font-bold text-gray-900">${loan.amount.toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center">
          <DollarSign className="h-5 w-5 text-gray-400 mr-2" />
          <div>
            <p className="text-sm text-gray-500">Remaining</p>
            <p className="font-medium">${loan.remainingAmount.toLocaleString()}</p>
          </div>
        </div>
        <div className="flex items-center">
          <Calendar className="h-5 w-5 text-gray-400 mr-2" />
          <div>
            <p className="text-sm text-gray-500">Next Payment</p>
            <p className="font-medium">
              {loan.nextPaymentDate ? new Date(loan.nextPaymentDate).toLocaleDateString() : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500">Progress</span>
          <span className="text-sm font-medium text-gray-900">
            {Math.round(((loan.totalPayable - loan.remainingAmount) / loan.totalPayable) * 100)}%
          </span>
        </div>
        <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full"
            style={{
              width: `${((loan.totalPayable - loan.remainingAmount) / loan.totalPayable) * 100}%`
            }}
          />
        </div>
      </div>
    </div>
  );
}