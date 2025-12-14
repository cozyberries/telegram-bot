"""Analytics command handlers"""

from telegram import Update
from telegram.ext import ContextTypes
from app.bot.middleware.auth import admin_required
from app.services import order_service, expense_service, product_service
from app.utils.formatters import format_currency, format_stats_summary


@admin_required
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - overall statistics"""
    try:
        # Gather statistics
        total_orders = await order_service.get_order_count()
        pending_orders = await order_service.get_order_count("payment_pending")
        delivered_orders = await order_service.get_order_count("delivered")
        total_revenue = await order_service.get_total_revenue()
        
        total_expenses = await expense_service.get_expense_count()
        pending_expenses = await expense_service.get_expense_count("pending")
        total_expense_amount = await expense_service.get_total_expense_amount()
        
        total_products = await product_service.get_product_count()
        low_stock_products = len(await product_service.get_low_stock_products())
        
        stats = {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "pending_expenses": pending_expenses,
            "total_expense_amount": total_expense_amount,
            "total_products": total_products,
            "low_stock_products": low_stock_products,
            "net_profit": total_revenue - total_expense_amount,
        }
        
        message = format_stats_summary(stats)
        
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error fetching statistics: {str(e)}")


@admin_required
async def stats_orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats_orders command - order statistics"""
    try:
        total = await order_service.get_order_count()
        pending = await order_service.get_order_count("payment_pending")
        confirmed = await order_service.get_order_count("payment_confirmed")
        processing = await order_service.get_order_count("processing")
        shipped = await order_service.get_order_count("shipped")
        delivered = await order_service.get_order_count("delivered")
        cancelled = await order_service.get_order_count("cancelled")
        revenue = await order_service.get_total_revenue()
        
        avg_order_value = revenue / total if total > 0 else 0
        
        message = (
            "📊 *Order Statistics*\n\n"
            f"*Total Orders:* {total}\n"
            f"*Revenue:* {format_currency(revenue)}\n"
            f"*Avg Order Value:* {format_currency(avg_order_value)}\n\n"
            "*By Status:*\n"
            f"⏳ Pending Payment: {pending}\n"
            f"✅ Payment Confirmed: {confirmed}\n"
            f"🔄 Processing: {processing}\n"
            f"📦 Shipped: {shipped}\n"
            f"✅ Delivered: {delivered}\n"
            f"❌ Cancelled: {cancelled}\n"
        )
        
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error fetching order statistics: {str(e)}")


@admin_required
async def stats_expenses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats_expenses command - expense statistics"""
    try:
        total = await expense_service.get_expense_count()
        pending = await expense_service.get_expense_count("pending")
        approved = await expense_service.get_expense_count("approved")
        rejected = await expense_service.get_expense_count("rejected")
        paid = await expense_service.get_expense_count("paid")
        
        total_amount = await expense_service.get_total_expense_amount()
        pending_amount = await expense_service.get_total_expense_amount("pending")
        approved_amount = await expense_service.get_total_expense_amount("approved")
        
        avg_expense = total_amount / total if total > 0 else 0
        
        message = (
            "📊 *Expense Statistics*\n\n"
            f"*Total Expenses:* {total}\n"
            f"*Total Amount:* {format_currency(total_amount)}\n"
            f"*Avg Expense:* {format_currency(avg_expense)}\n\n"
            "*By Status:*\n"
            f"⏳ Pending: {pending} ({format_currency(pending_amount)})\n"
            f"✅ Approved: {approved} ({format_currency(approved_amount)})\n"
            f"❌ Rejected: {rejected}\n"
            f"💰 Paid: {paid}\n"
        )
        
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error fetching expense statistics: {str(e)}")


@admin_required
async def stats_products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats_products command - product statistics"""
    try:
        total_products = await product_service.get_product_count()
        low_stock = await product_service.get_low_stock_products(threshold=10)
        out_of_stock = [p for p in low_stock if (p.stock_quantity or 0) == 0]
        
        # Get all products to calculate total stock value
        all_products = await product_service.get_products(limit=1000)
        total_stock_value = sum(p.price * (p.stock_quantity or 0) for p in all_products)
        total_items_in_stock = sum(p.stock_quantity or 0 for p in all_products)
        
        message = (
            "📊 *Product Statistics*\n\n"
            f"*Total Products:* {total_products}\n"
            f"*Total Stock Value:* {format_currency(total_stock_value)}\n"
            f"*Total Items in Stock:* {total_items_in_stock}\n\n"
            "*Stock Status:*\n"
            f"⚠️ Low Stock: {len(low_stock)} products\n"
            f"❌ Out of Stock: {len(out_of_stock)} products\n"
        )
        
        if out_of_stock:
            message += "\n*Out of Stock Products:*\n"
            for product in out_of_stock[:5]:  # Show first 5
                message += f"• {product.name}\n"
        
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error fetching product statistics: {str(e)}")
