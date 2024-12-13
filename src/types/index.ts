// Common Types
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'customer' | 'admin';
  phoneNumber: string;
}

export interface Loan {
  id: string;
  userId: string;
  amount: number;
  term: number;
  status: 'pending' | 'approved' | 'active' | 'completed' | 'rejected';
  interestRate: number;
  startDate?: Date;
  endDate?: Date;
  nextPaymentDate?: Date;
  totalPayable: number;
  remainingAmount: number;
}

export interface Payment {
  id: string;
  loanId: string;
  amount: number;
  date: Date;
  status: 'pending' | 'completed' | 'failed';
  type: 'scheduled' | 'extra';
}