# CozyBerries Telegram Admin Bot

A powerful Telegram bot for managing CozyBerries e-commerce operations including products, orders, expenses, and inventory.

## Features

- **📦 Order Management**: View, track, and update order status
- **🛍️ Product Management**: CRUD operations for products with stock tracking
- **💰 Expense Management**: Track, approve, and manage business expenses
- **📊 Analytics**: Real-time business statistics and insights
- **📦 Stock Management**: Monitor inventory levels and low stock alerts
- **🔔 Notifications**: Real-time alerts for new orders
- **🔐 Admin Security**: Telegram user ID-based authentication

## Architecture

Built as a serverless application deployable on Vercel:
- **Python 3.13** with async/await support
- **python-telegram-bot** for Telegram integration
- **Supabase** for database operations
- **Vercel Serverless Functions** for webhook handling

## Project Structure

```
telegram-bot/
├── api/                    # Vercel serverless functions
│   ├── webhook.py         # Main Telegram webhook handler
│   ├── notify-order.py    # Order notification endpoint
│   └── health.py          # Health check endpoint
├── app/
│   ├── bot/               # Bot logic
│   │   ├── bot.py        # Bot initialization
│   │   ├── handlers/     # Command handlers
│   │   └── middleware/   # Authentication
│   ├── database/          # Database models & client
│   ├── services/          # Business logic layer
│   ├── utils/            # Utilities (formatting, validation)
│   └── config.py         # Configuration management
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
└── .env.example          # Environment variables template
```

## Setup Instructions

### Prerequisites

1. **Telegram Bot Token**: Get from [@BotFather](https://t.me/BotFather)
2. **Supabase Account**: For database access
3. **Vercel Account**: For deployment
4. **Admin Telegram User IDs**: Your Telegram user ID(s)

### Getting Your Telegram User ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your user ID
3. Save this ID for configuration

### Local Development Setup

1. **Clone and setup**:
   ```bash
   cd telegram-bot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Environment Variables**:
   ```env
   TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
   ADMIN_TELEGRAM_USER_IDS=123456789,987654321  # Comma-separated
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   LOG_LEVEL=INFO
   ```

### Vercel Deployment

#### 1. Install Vercel CLI

```bash
npm install -g vercel
```

#### 2. Login to Vercel

```bash
vercel login
```

#### 3. Configure Environment Variables

Set these in Vercel dashboard or via CLI:

```bash
vercel env add TELEGRAM_BOT_TOKEN
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add ADMIN_TELEGRAM_USER_IDS

# For production
vercel env add TELEGRAM_BOT_TOKEN production
vercel env add SUPABASE_URL production
vercel env add SUPABASE_SERVICE_ROLE_KEY production
vercel env add ADMIN_TELEGRAM_USER_IDS production
```

#### 4. Deploy

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

#### 5. Set Telegram Webhook

After deployment, get your Vercel URL and set the webhook:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-project.vercel.app/api/webhook"}'
```

Or use the provided script:

```bash
python scripts/setup_webhook.py
```

#### 6. Configure Supabase Webhook

For order notifications:

1. Go to Supabase Dashboard → Database → Webhooks
2. Create new webhook on `orders` table
3. Select INSERT events
4. Set URL to: `https://your-project.vercel.app/api/notify-order`
5. Save webhook

## Bot Commands

### General Commands

- `/start` - Welcome message and bot introduction
- `/help` - Show all available commands

### Product Management

- `/products` - List all products with pagination
- `/product <id>` - Get detailed product information
- `/add_product` - Interactive form to create new product
- `/update_product <id>` - Update product details
- `/delete_product <id>` - Delete a product (with confirmation)
- `/product_stock <id> <qty>` - Quick stock quantity update

### Order Management

- `/orders` - List recent orders with filters
- `/order <id>` - Get complete order details with items
- `/order_status <id> <status>` - Update order status
  - Status options: `payment_pending`, `payment_confirmed`, `processing`, `shipped`, `delivered`, `cancelled`

### Expense Management

- `/expenses` - List expenses with status filters
- `/expense <id>` - Get expense details
- `/add_expense` - Interactive form to create expense
- `/approve_expense <id>` - Approve a pending expense
- `/reject_expense <id> <reason>` - Reject an expense with reason
- `/update_expense <id>` - Update expense details

### Stock Management

- `/stock` - View all products with stock levels
- `/low_stock` - View products with low inventory (< 10 units)
- `/update_stock <id> <qty>` - Update product stock quantity

### Analytics

- `/stats` - Overall business statistics
- `/stats_orders` - Detailed order statistics by status
- `/stats_expenses` - Expense statistics and breakdown
- `/stats_products` - Product and inventory statistics

## Usage Examples

### Creating a Product

```
/add_product

Bot: Please enter the product name:
You: Premium Strawberry Jam

Bot: Now enter the product price (in ₹):
You: 299

Bot: Enter product description (or send /skip):
You: Handmade strawberry jam with organic ingredients

Bot: Enter initial stock quantity:
You: 50

Bot: ✅ Product created successfully!
```

### Updating Order Status

```
/order_status abc-123-def shipped

Bot: ✅ Order status updated!
     Order: #ORD-001
     New status: Shipped
```

### Approving Expense

```
/approve_expense expense-id-123

Bot: ✅ Expense approved!
     💳 Office Supplies Purchase
     Amount: ₹1,500
     Status: ✅ Approved
```

## Notifications

The bot automatically sends notifications for:

- **New Orders**: Instant alert when order is created
- Includes order summary and quick action buttons
- Sent to all configured admin users

## Security

- **Admin-Only Access**: All commands require admin authentication
- **Telegram User ID Verification**: Only pre-configured users can access
- **Supabase Service Key**: Never exposed to client
- **Webhook Validation**: Ensures requests come from Telegram

## Troubleshooting

### Bot Not Responding

1. Check webhook is set correctly:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
   ```

2. Check Vercel deployment logs:
   ```bash
   vercel logs
   ```

3. Test health endpoint:
   ```bash
   curl https://your-project.vercel.app/api/health
   ```

### Authentication Errors

- Verify your Telegram user ID is in `ADMIN_TELEGRAM_USER_IDS`
- Check environment variables are set in Vercel dashboard
- Ensure IDs are comma-separated without spaces

### Order Notifications Not Working

1. Verify Supabase webhook configuration
2. Check webhook URL is correct
3. Test notification endpoint:
   ```bash
   curl https://your-project.vercel.app/api/notify-order
   ```

### Common Issues

**"Configuration validation failed"**
- Check all required environment variables are set
- Verify Supabase credentials are correct

**"Access Denied"**
- Your Telegram user ID is not in admin list
- Check ADMIN_TELEGRAM_USER_IDS environment variable

**"Product/Order not found"**
- Verify the ID is correct (UUIDs are case-sensitive)
- Check database connection

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

- **Handlers**: Command processing logic
- **Services**: Database operations and business logic
- **Models**: Pydantic models matching database schema
- **Middleware**: Authentication and authorization
- **Utilities**: Formatting, validation, helpers

### Adding New Commands

1. Create handler in `app/bot/handlers/`
2. Add service method in `app/services/`
3. Register in `app/bot/bot.py`
4. Update documentation

## Tech Stack

- **Python 3.13** - Latest Python features
- **python-telegram-bot 21.0** - Telegram Bot API
- **Supabase 2.3.4** - Database client
- **Pydantic 2.9** - Data validation
- **Vercel** - Serverless deployment

## Support

For issues or questions:
1. Check troubleshooting section
2. Review Vercel logs
3. Check Telegram webhook info
4. Verify environment variables

## License

Proprietary - CozyBerries Internal Tool

## Changelog

### v1.0.0 (2024-12-14)
- Initial release
- Product CRUD operations
- Order management
- Expense tracking
- Stock management
- Analytics dashboard
- Order notifications
- Vercel deployment support
