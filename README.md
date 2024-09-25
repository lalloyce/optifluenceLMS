# optifluenceLoanSystem

# Lending Business Database

## Overview

This project implements a comprehensive database system for a lending business. It manages customer information, loan issuance, repayments, penalties, and provides various reports and analytics features.

## Features

- Customer management (individuals and businesses)
- Loan management (personal and business loans)
- Automated interest calculation
- Penalty application for overdue loans
- Overpayment handling
- Comprehensive transaction tracking
- Customizable loan types
- Detailed reporting and analytics

## Database Schema

The database consists of the following main tables:

1. `Customers`: Stores customer information
2. `LoanTypes`: Defines different types of loans
3. `Loans`: Records individual loans
4. `Transactions`: Tracks all financial transactions
5. `CustomerAccounts`: Maintains running balances for customers
6. `Overpayments`: Records customer overpayments

## Setup Instructions

1. Ensure you have MySQL (version 5.7 or higher) installed on your system.
2. Clone this repository to your local machine.
3. Connect to your MySQL server using a client of your choice.
4. Run the SQL scripts in the following order:
   - `schema.sql`: Creates the database structure
   - `procedures.sql`: Adds stored procedures and functions
   - `triggers.sql`: Sets up necessary triggers
   - `events.sql`: Creates scheduled events

## Usage

### Issuing a Loan

To issue a new loan, use the `IssueLoan` stored procedure:

```sql
CALL IssueLoan(CustomerID, LoanTypeID, Amount);
```

### Processing a Repayment

To process a loan repayment, use the `ProcessRepayment` stored procedure:

```sql
CALL ProcessRepayment(LoanID, Amount, PaymentMethod);
```

### Generating Reports

1. Outstanding Loans Report:
   ```sql
   CALL GetOutstandingLoansReport();
   ```

2. Customer Statement:
   ```sql
   CALL GenerateCustomerStatement(CustomerID, StartDate, EndDate);
   ```

## Automated Processes

- Daily penalty application is handled by the `apply_penalties` event, which runs automatically every day.
- Overpayments are automatically applied to outstanding loans when processing repayments or issuing new loans.

## Customization

To add new loan types, insert records into the `LoanTypes` table:

```sql
INSERT INTO LoanTypes (Name, InterestRate, RepaymentPeriod, GracePeriod, PenaltyRate)
VALUES ('New Loan Type', 12.00, 90, 0, 15.00);
```

## Best Practices

1. Regularly backup your database.
2. Monitor database performance and optimize queries as needed.
3. Implement proper security measures, including user authentication and authorization.
4. Regularly review and update interest rates and penalty calculations as per business requirements.

## Contributing

Contributions to improve the database schema, add new features, or optimize existing processes are welcome. Please submit a pull request with your proposed changes.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Support

For any questions or support, please open an issue in the GitHub repository or contact the database administrator.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/optifluence/optifluenceLMS.git
   ```
2. Navigate to the project directory:
   ```bash
   cd optifluenceLMS
   ```
3. Install the dependencies:
   ```bash
   npm install
   ```

## Usage
1. Create a `.env` file in the root directory with the required environment variables.
2. Start the server:
   ```bash
   npm start
   ```
3. Access the application at `http://localhost:3000`.

## API Endpoints
- **POST** `/api/register`: Register a new user.
- **POST** `/api/login`: Log in an existing user.
- **POST** `/api/reset-password`: Request a password reset.
- **GET** `/verify/:token`: Verify user account.

## Contributing
Feel free to submit issues or pull requests for any improvements or bug fixes.

## License
This project is licensed under the MIT License.