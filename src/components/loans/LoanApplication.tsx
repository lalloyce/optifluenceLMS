import React, { useState } from 'react';
import { Calculator } from 'lucide-react';

export function LoanApplication() {
  const [loanAmount, setLoanAmount] = useState('');
  const [term, setTerm] = useState('12');
  const interestRate = 0.15; // 15% annual interest rate

  const calculateMonthlyPayment = () => {
    const principal = parseFloat(loanAmount);
    const numberOfPayments = parseInt(term);
    const monthlyRate = interestRate / 12;

    if (!principal || !numberOfPayments) return 0;

    const payment = (principal * monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) /
      (Math.pow(1 + monthlyRate, numberOfPayments) - 1);

    return payment.toFixed(2);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle loan application submission
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 max-w-2xl mx-auto">
      <div className="flex items-center mb-6">
        <Calculator className="h-6 w-6 text-blue-600 mr-2" />
        <h2 className="text-2xl font-bold text-gray-900">Loan Application</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Loan Amount
          </label>
          <div className="mt-1 relative rounded-md shadow-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-500 sm:text-sm">$</span>
            </div>
            <input
              type="number"
              value={loanAmount}
              onChange={(e) => setLoanAmount(e.target.value)}
              className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 rounded-md"
              placeholder="0.00"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Loan Term (months)
          </label>
          <select
            value={term}
            onChange={(e) => setTerm(e.target.value)}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          >
            <option value="12">12 months</option>
            <option value="24">24 months</option>
            <option value="36">36 months</option>
            <option value="48">48 months</option>
          </select>
        </div>

        {loanAmount && (
          <div className="bg-gray-50 p-4 rounded-md">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Loan Summary</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Monthly Payment</p>
                <p className="text-lg font-bold text-gray-900">
                  ${calculateMonthlyPayment()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Annual Interest Rate</p>
                <p className="text-lg font-bold text-gray-900">{interestRate * 100}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Interest</p>
                <p className="text-lg font-bold text-gray-900">
                  ${((calculateMonthlyPayment() * parseInt(term)) - parseFloat(loanAmount)).toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Payment</p>
                <p className="text-lg font-bold text-gray-900">
                  ${(calculateMonthlyPayment() * parseInt(term)).toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Submit Application
          </button>
        </div>
      </form>
    </div>
  );
}