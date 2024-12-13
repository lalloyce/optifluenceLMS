import React from 'react';
import { Payment } from '../../types';
import { Check, X, Clock } from 'lucide-react';

interface PaymentHistoryProps {
  payments: Payment[];
}

export function PaymentHistory({ payments }: PaymentHistoryProps) {
  const getStatusIcon = (status: Payment['status']) => {
    switch (status) {
      case 'completed':
        return <Check className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <X className="h-5 w-5 text-red-500" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
    }
  };

  return (
    <div className="bg-white shadow-sm rounded-lg">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg font-medium leading-6 text-gray-900">Payment History</h3>
      </div>
      <div className="border-t border-gray-200">
        <ul role="list" className="divide-y divide-gray-200">
          {payments.map((payment) => (
            <li key={payment.id} className="px-4 py-4 sm:px-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  {getStatusIcon(payment.status)}
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">
                      ${payment.amount.toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(payment.date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize"
                    style={{
                      backgroundColor: payment.status === 'completed' ? 'rgb(220 252 231)' :
                        payment.status === 'failed' ? 'rgb(254 226 226)' : 'rgb(254 249 195)',
                      color: payment.status === 'completed' ? 'rgb(22 101 52)' :
                        payment.status === 'failed' ? 'rgb(153 27 27)' : 'rgb(161 98 7)'
                    }}>
                    {payment.status}
                  </span>
                  <span className="ml-4 text-sm text-gray-500">
                    {payment.type === 'scheduled' ? 'Scheduled Payment' : 'Extra Payment'}
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}