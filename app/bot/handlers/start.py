"""Start command handler with interactive menu"""

from telegram import Update
from telegram.ext import ContextTypes
from app.bot.middleware.auth import admin_required
from app.bot.handlers.menu import show_main_menu


@admin_required
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - shows interactive main menu"""
    await show_main_menu(update, context)


@admin_required
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command - shows interactive main menu"""
    await show_main_menu(update, context)
