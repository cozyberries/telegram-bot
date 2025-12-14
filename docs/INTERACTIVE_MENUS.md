# Interactive Menu System Documentation

## Overview

The CozyBerries Telegram Bot now features a comprehensive interactive menu system with nested inline keyboards for all commands. Users can navigate through the entire bot functionality using intuitive button-based menus instead of typing commands.

## Key Features

### 1. **Main Menu Hub**
- Central navigation point accessed via `/start` or `/menu`
- Visual categorization with emojis
- Quick access to all major functions

### 2. **Nested Submenus**
Each category has its own submenu with relevant actions:
- 📦 **Orders Management**
- 🛍️ **Products Management**
- 💰 **Expenses Management**
- 📊 **Stock Management**
- 📈 **Analytics Dashboard**

### 3. **Interactive Features**

#### **Pagination**
- Browse large lists with Previous/Next buttons
- Page indicators showing current position
- Configurable items per page

#### **Item Actions**
- View details inline
- Edit, delete, or update items
- Contextual action buttons for each item type

#### **Confirmation Dialogs**
- Safety prompts for destructive actions
- Clear Yes/No options
- Easy cancellation

#### **Back Navigation**
- Every submenu has back buttons
- Return to previous menu or main menu
- Breadcrumb-style navigation

## Menu Structure

```
Main Menu
├── 📦 Orders
│   ├── View All Orders (paginated)
│   ├── Filter by Status (Pending/Confirmed/Shipped/Delivered)
│   ├── Create New Order
│   └── Back to Main Menu
│
├── 🛍️ Products
│   ├── View All Products (paginated)
│   │   └── Product Details → Edit/Delete/Update Stock
│   ├── Search Products
│   ├── Browse by Category
│   ├── Add New Product
│   ├── Update Product
│   ├── Delete Product
│   └── Back to Main Menu
│
├── 💰 Expenses
│   ├── View All Expenses (paginated)
│   │   └── Expense Details → Approve/Reject/Delete
│   ├── Filter (Pending/Approved)
│   ├── Add New Expense
│   ├── Approve Expense
│   ├── Reject Expense
│   └── Back to Main Menu
│
├── 📊 Stock
│   ├── View All Stock
│   ├── Low Stock Alert
│   ├── Out of Stock
│   ├── Update Stock
│   ├── Stock Report
│   └── Back to Main Menu
│
└── 📈 Analytics
    ├── Overall Statistics
    ├── Order Statistics
    ├── Expense Statistics
    ├── Product Statistics
    ├── Revenue Statistics
    ├── Date Range Reports
    └── Back to Main Menu
```

## Usage Guide

### Getting Started

1. **Open the bot** in Telegram
2. Type `/start` or `/menu`
3. **Tap any category button** to enter that section
4. **Navigate using inline buttons** - no need to type commands!

### Example Workflows

#### Managing Products

```
/start
→ Tap "🛍️ Products"
→ Tap "📋 View All Products"
→ Tap on a product name
→ Tap "✏️ Edit" or "📦 Update Stock"
→ Follow the prompts
```

#### Checking Orders

```
/start
→ Tap "📦 Orders"
→ Tap "⏳ Pending" to filter
→ Browse with Next/Prev buttons
→ Tap an order to see details
→ Tap "✏️ Update Status"
```

#### Viewing Analytics

```
/start
→ Tap "📈 Analytics"
→ Tap "📊 Overall Stats"
→ View comprehensive dashboard
→ Use "« Back" to return
```

## Command Reference

### Primary Commands

| Command | Description |
|---------|-------------|
| `/start` | Show main interactive menu |
| `/menu` | Show main interactive menu |
| `/orders` | Quick access to orders menu |
| `/products` | Quick access to products menu |
| `/expenses` | Quick access to expenses menu |
| `/stock` | Quick access to stock menu |
| `/stats` | Quick access to analytics |

### Legacy Commands (Still Supported)

All text-based commands continue to work for advanced users:
- `/product <id>` - View product details
- `/order <id>` - View order details
- `/expense <id>` - View expense details
- etc.

## Technical Implementation

### Core Components

#### 1. Menu Handler (`menu.py`)
- **Main menu generation**: `get_main_menu_keyboard()`
- **Submenu keyboards**: Individual functions for each category
- **Callback routing**: Central `handle_menu_callback()` function
- **Pagination support**: `get_pagination_keyboard()`

#### 2. Interactive Handlers
Each module has enhanced interactive handlers:
- `products_interactive.py` - Product management
- `orders_interactive.py` - Order management (to be completed)
- `expenses_interactive.py` - Expense management (to be completed)
- `stock_interactive.py` - Stock management (to be completed)

#### 3. Callback Query Router
Central routing in `bot.py`:
```python
async def _handle_callback_query(update, context):
    # Routes based on callback data prefix
    if data.startswith("menu_"):
        # Menu navigation
    elif data.startswith("products_"):
        # Product actions
    elif data.startswith("order"):
        # Order actions
    # ... etc
```

### Callback Data Convention

Callbacks follow a hierarchical naming pattern:

```
{category}_{action}_{id}

Examples:
- menu_products          # Navigate to products menu
- products_list_all      # Show all products
- products_page_2        # Go to page 2
- product_details_abc123 # Show product details
- product_edit_abc123    # Edit specific product
- confirm_delete_product_abc123 # Confirm deletion
```

## Benefits

### For Users
- ✅ **No commands to remember**
- ✅ **Visual, intuitive navigation**
- ✅ **Faster operations**
- ✅ **Reduced errors** (no typos in commands)
- ✅ **Mobile-friendly** design

### For Admins
- ✅ **Easier onboarding** for new users
- ✅ **Consistent UX** across all features
- ✅ **Better engagement** with bot features
- ✅ **Professional appearance**

## Customization

### Adding New Menus

1. **Define keyboard function** in `menu.py`:
```python
def get_custom_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Action 1", callback_data="custom_action1")],
        [InlineKeyboardButton("« Back", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)
```

2. **Add handler** in menu or dedicated file:
```python
async def handle_custom_menu(update, context):
    query = update.callback_query
    # Process custom actions
```

3. **Register callback** in `bot.py`:
```python
elif data.startswith("custom_"):
    await handle_custom_menu(update, context)
```

### Styling Guidelines

- **Emojis**: Use consistently for visual identification
- **Text**: Clear, concise button labels
- **Layout**: 1-2 buttons per row for mobile
- **Navigation**: Always provide back/cancel options
- **Confirmations**: Use for destructive actions

## Migration Notes

### Backward Compatibility

- All original text commands still work
- Existing workflows are preserved
- Users can choose their preferred interaction method

### Gradual Rollout

1. ✅ **Phase 1**: Core menu system (Completed)
2. ✅ **Phase 2**: Products interactive menus (Completed)
3. 🚧 **Phase 3**: Orders interactive menus (In Progress)
4. 📋 **Phase 4**: Expenses enhancement (Planned)
5. 📋 **Phase 5**: Stock interactive menus (Planned)
6. 📋 **Phase 6**: Advanced analytics (Planned)

## Testing

### Manual Testing Checklist

- [ ] Main menu displays correctly
- [ ] All category buttons work
- [ ] Submenu navigation functions
- [ ] Back buttons return to correct menu
- [ ] Pagination works (Prev/Next)
- [ ] Item selection shows details
- [ ] Action buttons perform correctly
- [ ] Confirmation dialogs appear
- [ ] Error messages display properly
- [ ] Mobile layout looks good

### Integration Tests

Located in `tests/test_interactive_menus.py` (to be created):
- Menu navigation flows
- Callback routing
- Button state management
- User context preservation

## Troubleshooting

### Common Issues

**Menu not appearing**
- Check bot initialization
- Verify handler registration
- Review callback query routing

**Buttons not responding**
- Check callback data format
- Verify handler exists
- Review error logs

**Wrong menu displayed**
- Check callback routing logic
- Verify data prefixes
- Review menu state management

## Future Enhancements

### Planned Features

1. **Search Integration**
   - Inline search within menus
   - Auto-complete suggestions
   - Recent searches

2. **Bulk Operations**
   - Multi-select checkboxes
   - Batch actions
   - Select all/none

3. **Favorites/Quick Actions**
   - Customizable shortcuts
   - Recent items
   - Frequent actions

4. **Advanced Filters**
   - Date range pickers
   - Multi-criteria filters
   - Saved filter presets

5. **Notifications**
   - In-menu alerts
   - Badge indicators
   - Action confirmations

## Support

For issues or questions:
- Check logs in `/var/log/telegram-bot/`
- Review error messages in bot responses
- Contact development team

---

**Last Updated**: December 14, 2025  
**Version**: 2.0  
**Status**: ✅ Production Ready (Core Features)
