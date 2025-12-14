# Add Expense - Single Message Format

## ✅ New Feature

The `/add_expense` command now uses a **single-message format** instead of the old multi-step conversation!

## 📝 How to Use

### 1. Start the Command

Send `/add_expense` to the bot.

### 2. Receive the Format Guide

The bot will respond with:

```
💰 Add New Expense

Please send all details in one message using this format:

Amount: 1500
Detail: Office supplies purchase
Date: 2025-12-14
Notes: Pens, paper, and notebooks

📋 Format Guide:
• Amount: Required - expense amount (₹)
• Detail: Required - what was purchased
• Date: Optional - transaction date (YYYY-MM-DD)
• Notes: Optional - additional information

💡 Example:
Amount: 2500
Detail: Client lunch meeting
Date: 2025-12-14
Notes: 3 people at Taj restaurant

Send your expense details now, or /cancel to stop.
```

### 3. Send Your Expense Details

Reply with all details in one message:

```
Amount: 3500
Detail: New laptop for development
Date: 2025-12-14
Notes: MacBook Air M2
```

### 4. Get Confirmation

The bot will respond with:

```
✅ Expense Created Successfully!

💰 Amount: ₹3,500.00
📝 Detail: New laptop for development
📅 Date: 2025-12-14
📌 Notes: MacBook Air M2

🆔 ID: 123e4567-e89b-12d3-a456-426614174000
⏳ Status: PENDING
```

## 🎯 Features

### Required Fields
- **Amount:** The expense amount in ₹ (e.g., `1500`, `2500.50`)
- **Detail:** Description of what was purchased

### Optional Fields
- **Date:** Transaction date in YYYY-MM-DD format (defaults to today)
- **Notes:** Additional information or comments

### Flexible Field Names

You can use different names for the same field:

**Amount:**
- `Amount: 1500`
- `Amt: 1500`
- `Price: 1500`
- `Cost: 1500`

**Detail:**
- `Detail: Office supplies`
- `Details: Office supplies`
- `Description: Office supplies`
- `Desc: Office supplies`
- `Title: Office supplies`

**Date:**
- `Date: 2025-12-14`
- `Transaction Date: 2025-12-14`
- `Expense Date: 2025-12-14`

**Notes:**
- `Notes: Additional info`
- `Note: Additional info`
- `Additional Notes: Additional info`
- `Comments: Additional info`

## ✨ Examples

### Example 1: Minimal (Amount + Detail)

```
Amount: 500
Detail: Coffee meeting
```

Result: Creates expense with today's date

### Example 2: With Date

```
Amount: 2000
Detail: Client dinner
Date: 2025-12-13
```

### Example 3: Full Details

```
Amount: 5000
Detail: Software subscription
Date: 2025-12-14
Notes: Annual renewal - Adobe Creative Cloud
```

### Example 4: Using Alternative Field Names

```
Cost: 1200
Desc: Office snacks
Transaction Date: 2025-12-14
Comments: For team meeting
```

## ❌ Error Handling

If you miss required fields or format incorrectly, the bot will help:

**Missing Amount:**
```
❌ Amount is required

Please try again with the correct format:

Amount: 1500
Detail: Office supplies
Date: 2025-12-14
Notes: Optional notes
```

**Invalid Amount:**
```
❌ Invalid amount: Amount must be a positive number

Please try again...
```

**Invalid Date:**
```
❌ Invalid date: Date must be in YYYY-MM-DD format

Please try again...
```

## 🔄 Cancelling

Send `/cancel` at any time to stop the expense creation process.

## 📊 What Happens After Creation

Once created, the expense:
- ✅ Is saved to the database
- ⏳ Has status `PENDING` (awaiting approval)
- 🆔 Gets a unique ID
- 📅 Uses today's date if none provided
- 🏷️ Gets default category `other`
- 💳 Has default payment method `cash`

## 🎨 Benefits of Single Message Format

### Old Way (Multi-Step):
```
Bot: Enter title
You: Office supplies
Bot: Enter amount
You: 1500
Bot: Select category
You: 1
Bot: Enter date
You: 2025-12-14
Bot: Enter vendor
You: /skip
```
**5 back-and-forth messages** ❌

### New Way (Single Message):
```
Bot: Send all details in one message
You: Amount: 1500
     Detail: Office supplies
     Date: 2025-12-14
Bot: ✅ Created!
```
**1 message** ✅

## 🚀 Tips

1. **Copy the format** from the bot's message for easy editing
2. **No need for vendor** - it's handled automatically
3. **Date is optional** - defaults to today
4. **Notes are optional** - add them only if needed
5. **Use simple numbers** for amounts (e.g., `1500` not `₹1,500.00`)

---

**Status:** ✅ Live and Ready
**Version:** 2.0
**Last Updated:** December 14, 2025
