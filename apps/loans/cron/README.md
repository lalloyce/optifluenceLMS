# Risk Management Cron Jobs

This document outlines the cron jobs required for the risk management system.

## Daily Risk Summary

Add the following to your crontab to send daily risk summaries:

```bash
# Send risk summary at 7:00 AM every day
0 7 * * * cd /Applications/XAMPP/xamppfiles/htdocs/optifluenceLMS && python manage.py send_risk_summary
```

To add this to your crontab:

1. Open your crontab:
```bash
crontab -e
```

2. Add the above line, adjusting the path to match your installation

3. Save and exit

## Verifying Cron Setup

To verify the cron job:

1. Check cron logs:
```bash
grep CRON /var/log/syslog
```

2. Test the command manually:
```bash
cd /Applications/XAMPP/xamppfiles/htdocs/optifluenceLMS
python manage.py send_risk_summary
```

## Additional Notes

- Ensure the user running the cron job has proper permissions
- Set up proper logging in Django settings
- Configure email settings in Django settings
- Monitor the cron job execution through logs
