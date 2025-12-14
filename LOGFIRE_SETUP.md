# 🔥 Logfire Setup Guide

## What is Logfire?

Logfire is Pydantic's observability platform that provides:
- 📊 Real-time logging and monitoring
- 🔍 Distributed tracing
- 📈 Performance metrics
- 🐛 Error tracking
- 🎯 Request/response inspection

## Setup Steps

### 1. Create Logfire Account

1. Go to: https://logfire.pydantic.dev/
2. Sign up with GitHub or email
3. Create a new project: `cozyberries-telegram-bot`
4. Get your API token from project settings

### 2. Add Environment Variables

#### Local Development

Add to `.env`:
```bash
LOGFIRE_TOKEN=your_token_here
LOGFIRE_PROJECT_NAME=cozyberries-telegram-bot
LOGFIRE_ENVIRONMENT=development
```

#### Production (Vercel)

1. Go to: https://vercel.com/cozyberries-projects/telegram-bot/settings/environment-variables

2. Add:
   ```
   LOGFIRE_TOKEN=your_token_here
   LOGFIRE_PROJECT_NAME=cozyberries-telegram-bot
   LOGFIRE_ENVIRONMENT=production
   ```

3. Redeploy:
   ```bash
   vercel --prod
   ```

### 3. Test Logfire Integration

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload

# Send test message to bot
# Check Logfire dashboard for logs
```

## Features Implemented

### 1. Automatic Instrumentation

```python
logfire.instrument_fastapi()   # FastAPI endpoints
logfire.instrument_httpx()     # HTTP requests
logfire.instrument_psycopg()   # Database queries
```

### 2. Bot Update Logging

Every Telegram update is logged with:
- Update ID
- User ID
- Command executed
- Processing time
- Success/failure status

```python
with log_bot_update(update_id, user_id, command):
    # Process update
    pass
```

### 3. Database Operation Tracking

All database operations are traced:
- Operation type (SELECT, INSERT, UPDATE, DELETE)
- Table name
- Record ID
- Query duration

```python
with log_database_operation("SELECT", "orders", order_id):
    # Query database
    pass
```

### 4. Error Tracking

Errors are automatically captured with context:
- Error type and message
- Stack trace
- Request context
- User information

```python
log_error(exception, {
    "endpoint": "webhook",
    "user_id": user_id
})
```

### 5. Metrics

Business metrics are tracked:
- Order count
- Revenue
- Average order value
- Response times

```python
log_metric("total_revenue", 1500.00, {
    "currency": "INR",
    "period": "daily"
})
```

## Viewing Logs

### Logfire Dashboard

1. Go to: https://logfire.pydantic.dev/
2. Select your project: `cozyberries-telegram-bot`
3. View:
   - **Traces**: Full request/response flow
   - **Logs**: Structured log messages
   - **Metrics**: Performance indicators
   - **Errors**: Exception tracking

### Filter by Context

```
# Filter by user
user_id:123456789

# Filter by command
command:/start

# Filter by error
error_type:ValueError

# Filter by environment
environment:production
```

## What Gets Logged

### Telegram Updates
```
[telegram_update]
├─ update_id: 123456789
├─ user_id: 123456789
├─ command: /start
├─ duration: 45ms
└─ status: success
```

### Database Operations
```
[database_operation]
├─ operation: SELECT
├─ table: orders
├─ record_id: order_123
├─ duration: 12ms
└─ rows: 1
```

### API Requests
```
[api_request]
├─ endpoint: /webhook
├─ method: POST
├─ status: 200
├─ duration: 234ms
└─ user_agent: TelegramBot
```

### Errors
```
[error_occurred]
├─ error: Database connection failed
├─ error_type: ConnectionError
├─ context: {"operation": "get_orders"}
├─ stack_trace: ...
└─ timestamp: 2024-12-14T03:30:00Z
```

## Benefits

### 1. Debugging
- See exactly what happened in each request
- Trace errors through the entire stack
- View request/response payloads

### 2. Performance Monitoring
- Identify slow operations
- Track response times
- Monitor resource usage

### 3. Business Insights
- Track command usage
- Monitor user engagement
- Measure conversion metrics

### 4. Alerting
- Get notified of errors
- Alert on performance issues
- Track SLA compliance

## Advanced Usage

### Custom Spans

```python
with logfire.span("custom_operation", param1="value"):
    # Your code
    pass
```

### Custom Metrics

```python
logfire.info(
    "order_created",
    order_id=order.id,
    amount=order.total_amount,
    customer_id=order.customer_id
)
```

### Contextual Logging

```python
logfire.debug("Processing started", user_id=123)
logfire.info("Processing completed", result="success")
logfire.error("Processing failed", error=str(e))
```

## Configuration Options

### In `app/logging_config.py`

```python
logfire.configure(
    token=logfire_token,
    service_name="cozyberries-telegram-bot",
    environment="production",
    send_to_logfire=True,        # Send to cloud
    console=False,               # Don't duplicate to console
    sampling_rate=1.0,           # Sample 100% of requests
)
```

### Environment-Specific Settings

**Development**:
- `LOGFIRE_ENVIRONMENT=development`
- More verbose logging
- All traces captured

**Production**:
- `LOGFIRE_ENVIRONMENT=production`
- Essential logging only
- Sampling for high traffic

## Troubleshooting

### Logfire Not Working

1. Check token is set:
   ```bash
   echo $LOGFIRE_TOKEN
   ```

2. Check logs for errors:
   ```bash
   vercel logs | grep -i logfire
   ```

3. Test locally:
   ```bash
   python -c "import logfire; logfire.configure(token='your_token'); print('OK')"
   ```

### No Logs Appearing

1. Verify environment variables are set in Vercel
2. Redeploy after setting variables
3. Check Logfire dashboard for correct project
4. Ensure `LOGFIRE_TOKEN` is valid

### High Volume Warnings

If you're seeing too many logs:

1. Adjust sampling rate:
   ```python
   logfire.configure(sampling_rate=0.1)  # Sample 10%
   ```

2. Filter by importance:
   ```python
   if important:
       logfire.info("Important event")
   ```

## Cost Considerations

Logfire pricing is based on:
- Number of spans
- Data retention period
- Features used

**Free Tier** includes:
- 1M spans/month
- 7 days retention
- Basic features

**For Production**:
- Consider sampling for high traffic
- Archive old logs
- Use appropriate log levels

## Best Practices

1. **Use Structured Logging**
   ```python
   # Good
   logfire.info("order_created", order_id=123, amount=100)
   
   # Bad
   logfire.info(f"Order {123} created with amount {100}")
   ```

2. **Add Context**
   ```python
   with logfire.span("process_order", order_id=order.id):
       # Processing...
   ```

3. **Track Important Metrics**
   ```python
   log_metric("revenue", total_amount)
   log_metric("orders_per_day", count)
   ```

4. **Log Errors with Context**
   ```python
   log_error(exception, {
       "user_id": user_id,
       "operation": "checkout"
   })
   ```

## Resources

- **Logfire Docs**: https://logfire.pydantic.dev/docs
- **Dashboard**: https://logfire.pydantic.dev/
- **Python SDK**: https://github.com/pydantic/logfire-python
- **Support**: https://github.com/pydantic/logfire/issues

---

**Status**: ✅ Logfire is configured and ready to use!

**Next Steps**:
1. Get your Logfire token
2. Add to environment variables
3. Redeploy
4. Check dashboard for logs
