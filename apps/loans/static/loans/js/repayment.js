// Repayment form handling
class RepaymentForm {
    constructor(formId) {
        this.form = document.getElementById(formId);
        if (!this.form) return;

        this.amountInput = this.form.querySelector('input[name="amount"]');
        this.maxAmount = parseFloat(this.amountInput?.getAttribute('data-balance') || 0);
        this.penaltyAmount = parseFloat(this.amountInput?.getAttribute('data-penalties') || 0);

        this.initialize();
    }

    initialize() {
        // Format amount on blur
        this.amountInput?.addEventListener('blur', () => this.formatAmount());

        // Validate form on submit
        this.form.addEventListener('submit', (e) => this.validateForm(e));

        // Real-time balance update
        this.amountInput?.addEventListener('input', () => this.updateRemainingBalance());
    }

    formatAmount() {
        if (this.amountInput.value) {
            this.amountInput.value = parseFloat(this.amountInput.value).toFixed(2);
        }
    }

    validateForm(e) {
        const amount = parseFloat(this.amountInput.value);
        if (amount > this.maxAmount) {
            e.preventDefault();
            alert('Payment amount cannot exceed the total balance.');
            return false;
        }
        return true;
    }

    updateRemainingBalance() {
        const amount = parseFloat(this.amountInput.value) || 0;
        const remaining = Math.max(0, this.maxAmount - amount).toFixed(2);
        
        // Update remaining balance display if it exists
        const remainingDisplay = document.getElementById('remainingBalance');
        if (remainingDisplay) {
            remainingDisplay.textContent = remaining;
        }
    }
}

// Penalty waiver form handling
class PenaltyWaiverForm {
    constructor(formId) {
        this.form = document.getElementById(formId);
        if (!this.form) return;

        this.amountInput = this.form.querySelector('input[name="amount"]');
        this.maxAmount = parseFloat(this.amountInput?.getAttribute('data-current-penalty') || 0);

        this.initialize();
    }

    initialize() {
        // Format amount on blur
        this.amountInput?.addEventListener('blur', () => this.formatAmount());

        // Validate form on submit
        this.form.addEventListener('submit', (e) => this.validateForm(e));
    }

    formatAmount() {
        if (this.amountInput.value) {
            this.amountInput.value = parseFloat(this.amountInput.value).toFixed(2);
        }
    }

    validateForm(e) {
        const amount = parseFloat(this.amountInput.value);
        if (amount > this.maxAmount) {
            e.preventDefault();
            alert('Waiver amount cannot exceed the current penalty.');
            return false;
        }
        return true;
    }
}

// Transaction list handling
class TransactionList {
    constructor() {
        this.initialize();
    }

    initialize() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Loan balance updater
class LoanBalanceUpdater {
    constructor(loanId) {
        this.loanId = loanId;
        if (!this.loanId) return;

        this.initialize();
    }

    initialize() {
        // Update balance every minute
        this.updateBalance();
        setInterval(() => this.updateBalance(), 60000);
    }

    async updateBalance() {
        try {
            const response = await fetch(`/loans/${this.loanId}/balance/`);
            if (!response.ok) throw new Error('Failed to fetch balance');

            const data = await response.json();
            if (!data.success) throw new Error(data.error || 'Unknown error');

            this.updateBalanceDisplay(data.balance);
        } catch (error) {
            console.error('Error updating balance:', error);
        }
    }

    updateBalanceDisplay(balance) {
        // Update principal remaining
        const principalElement = document.getElementById('principalRemaining');
        if (principalElement) {
            principalElement.textContent = balance.principal_remaining.toFixed(2);
        }

        // Update penalties
        const penaltiesElement = document.getElementById('currentPenalties');
        if (penaltiesElement) {
            penaltiesElement.textContent = balance.penalties.toFixed(2);
        }

        // Update total balance
        const totalElement = document.getElementById('totalBalance');
        if (totalElement) {
            totalElement.textContent = balance.total_balance.toFixed(2);
        }

        // Update progress bar if exists
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${balance.payment_progress}%`;
            progressBar.setAttribute('aria-valuenow', balance.payment_progress);
        }
    }
}

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize repayment form if present
    new RepaymentForm('repaymentForm');

    // Initialize penalty waiver form if present
    new PenaltyWaiverForm('waivePenaltyForm');

    // Initialize transaction list
    new TransactionList();

    // Initialize balance updater if loan ID is present
    const loanId = document.body.getAttribute('data-loan-id');
    if (loanId) {
        new LoanBalanceUpdater(loanId);
    }
});
