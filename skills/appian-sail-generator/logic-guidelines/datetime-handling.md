# Date/Time Handling Rules {#datetime-critical-rules}

> **Related documentation:**
> - `logic-guidelines/LOGIC-PRIMARY-REFERENCE.md` (mock data interfaces)
> - `conversion-guidelines/validation-enforcement-module.md` (type matching enforcement)
>
> **Quick Reference:** `logic-guidelines/null-safety-quick-ref.md` (Date/Time section)

---

## Correct Date/Time Functions

🚨 **CRITICAL**: Use the correct function for date/time creation

```sail
/* ✅ CORRECT - Use dateTime() for specific date/time creation */
dateTime(year(today()), month(today()), 1, 0, 0, 0)  /* Month to Date */

/* ❌ WRONG - a!dateTimeValue() does NOT exist in Appian */
a!dateTimeValue(year: year(today()), month: month(today()), day: 1)
```

---

## Type Casting with todate() in Sample Data

**When creating sample data with dates, use todate() for consistency:**

```sail
/* ❌ WRONG - mixing date literals with date arithmetic can cause inconsistencies */
local!data: {
  a!map(dueDate: today()),              /* Type: Date */
  a!map(dueDate: now() + 1)             /* Type: DateTime - causes grid sort errors! */
}

/* ✅ RIGHT - consistent Date types */
local!data: {
  a!map(dueDate: today()),              /* Type: Date */
  a!map(dueDate: today() + 1),          /* Type: Date */
  a!map(dueDate: today() + 7)           /* Type: Date */
}

/* ✅ ALSO RIGHT - explicit todate() for clarity */
local!data: {
  a!map(dueDate: todate(today())),      /* Type: Date */
  a!map(dueDate: todate(today() + 1)),  /* Type: Date */
  a!map(dueDate: todate(today() + 7))   /* Type: Date */
}
```

---

## Date/DateTime Arithmetic Returns Intervals

Subtracting dates or datetimes returns an **Interval** type, not a Number:
- `now() - timestamp` → Interval (Day to Second)
- `today() - dateValue` → Interval (Day to Day)

**Cannot compare Intervals directly to Numbers:**

```sail
/* ❌ WRONG */
if(now() - fv!row.timestamp < 1, ...)  /* Error: Cannot compare Interval to Number */

/* ✅ RIGHT */
if(tointeger(now() - fv!row.timestamp) < 1, ...)  /* Convert Interval to Integer first */
```

---

## Query Filter Data Type Matching

**The a!queryFilter function requires exact data type matching between field and value:**

```sail
/* ❌ WRONG - Date arithmetic with DateTime field */
a!queryFilter(
  field: recordType!Case.fields.createdOn,  /* DateTime field */
  value: today() - 30  /* Date value - TYPE MISMATCH */
)

/* ✅ CORRECT - Use DateTime functions for DateTime fields */
a!queryFilter(
  field: recordType!Case.fields.createdOn,  /* DateTime field */
  value: a!subtractDateTime(startDateTime: now(), days: 30)  /* DateTime value */
)

/* ✅ CORRECT - Date field with Date value */
a!queryFilter(
  field: recordType!Case.fields.dueDate,  /* Date field */
  value: today() - 30  /* Date value */
)
```

### Most Common Mismatches:
- **DateTime fields**: Use `now()`, `todatetime()`, `dateTime()`, `a!subtractDateTime()`, `a!addDateTime()`, `userdatetime()`
- **Date fields**: Use `today()`, `todate()`, `date()`, `datevalue()`, `eomonth()`, `edate()`, date arithmetic
- **User fields**: Use `loggedInUser()`, `touser()`, or User variables from `a!pickerFieldUsers` — NOT plain text usernames
- **Group fields**: Use `togroup()` or Group variables from `a!pickerFieldGroups` — NOT plain group IDs

**For all other types, see the Type Compatibility Matrix below.**

### Workflow Before Writing Date/DateTime Filters:
1. **Check data-model-context.md** for the actual field type
2. **Date field** → Use `today()`, `todate()`, `date()`, `datevalue()`, `eomonth()`, `edate()`, date arithmetic
3. **DateTime field** → Use `now()`, `todatetime()`, `dateTime()`, `a!subtractDateTime()`, `a!addDateTime()`, `userdatetime()`

---

## Complete Type Matching Reference for a!queryFilter()

**a!queryFilter() requires exact type matching between `field` and `value` parameters. Mismatched types cause runtime failures.**

### Type Compatibility Matrix

| Field Type | Compatible Value Types | Incompatible (Will Fail) |
|------------|----------------------|--------------------------|
| **Text** | Text literals, text variables, `tostring()`, `concat()` | Integer, Boolean, Date, DateTime, User |
| **Number (Integer)** | Integer literals, integer variables, `tointeger()`, Decimal | Text, Boolean, Date, DateTime |
| **Number (Decimal)** | Decimal literals, decimal variables, `todecimal()`, Integer | Text, Boolean, Date, DateTime |
| **Date** | `today()`, `todate()`, `date()`, `datevalue()`, `eomonth()`, `edate()`, date arithmetic, Date variables | DateTime, `now()`, `a!subtractDateTime()`, `a!addDateTime()`, `userdatetime()`, Text, Integer |
| **DateTime** | `now()`, `todatetime()`, `dateTime()`, `a!subtractDateTime()`, `a!addDateTime()`, `userdatetime()`, DateTime variables | Date, `today()`, `todate()`, `datevalue()`, `eomonth()`, `edate()`, Text, Integer |
| **Boolean** | `true()`, `false()`, Boolean variables | Text (`"true"`), Integer (`1`, `0`) |
| **User** | `loggedInUser()`, `touser()`, User variables, `a!pickerFieldUsers` result | Text (username string without `touser()`) |
| **Group** | `togroup()`, Group variables, `a!pickerFieldGroups` result | Integer (group ID without `togroup()`), Text |

**Note:** Integer and Decimal are the ONLY interchangeable types. All other combinations require exact match.

### Function Return Types Quick Reference

**Date Functions:**

| Function | Returns | Use For |
|----------|---------|---------|
| `today()` | Date | Current date only |
| `todate(...)` | Date | Convert value to Date |
| `date(y, m, d)` | Date | Create specific Date |
| `datevalue(text)` | Date | Parse text string to Date |
| `eomonth(startDate, months)` | Date | Last day of month N months from startDate |
| `edate(startDate, months)` | Date | Same day N months from startDate |
| `today() + N` / `today() - N` | Date | Date arithmetic |

**DateTime Functions:**

| Function | Returns | Use For |
|----------|---------|---------|
| `now()` | DateTime | Current date and time |
| `todatetime(...)` | DateTime | Convert value to DateTime |
| `dateTime(y, m, d, h, m, s)` | DateTime | Create specific DateTime |
| `a!subtractDateTime(...)` | DateTime | Past DateTime calculation |
| `a!addDateTime(...)` | DateTime | Future DateTime calculation |
| `userdatetime(y, m, d, h, m, s)` | DateTime | Create DateTime in user's preferred calendar |

**Other Type Functions:**

| Function | Returns | Use For |
|----------|---------|---------|
| `tointeger(...)` | Integer | Convert to whole number |
| `todecimal(...)` | Decimal | Convert to decimal number |
| `tostring(...)` | Text | Convert to text |
| `true()` / `false()` | Boolean | Boolean literals |
| `loggedInUser()` | User | Current user |
| `touser(...)` | User | Convert username/value to User |
| `togroup(...)` | Group | Convert group ID/value to Group |

**Formatting (Returns Text, not Date/DateTime):**

| Function | Returns | Use For |
|----------|---------|---------|
| `datetext(value, format)` | Text | Format Date or DateTime as text string |

### Local Variable Type Inheritance

A local variable's type is determined by its initialization expression:

```sail
local!filterDate: today(),           /* Type: Date */
local!filterTimestamp: now(),        /* Type: DateTime */
local!filterStatus: "Active",        /* Type: Text */
local!filterStatusId: 1,             /* Type: Integer */
local!filterActive: true(),          /* Type: Boolean */
local!filterUser: loggedInUser(),    /* Type: User */
```

**When using a local variable in a!queryFilter(), trace back to its declaration to verify type compatibility with the field.**

---

## Function Return Type Detection for Type Validation {#datetime.type-detection}

### Date-Returning Functions (Incompatible with DateTime fields)

When these functions appear in `a!queryFilter()` value parameter with a **DateTime field**, wrap the entire expression in `todatetime()`:

| Function Pattern | Returns | Wrap Pattern |
|------------------|---------|--------------|
| `today()` | Date | `todatetime(today())` |
| `today() + N` | Date | `todatetime(today() + N)` |
| `today() - N` | Date | `todatetime(today() - N)` |
| `todate(...)` | Date | `todatetime(todate(...))` |
| `date(y, m, d)` | Date | `todatetime(date(y, m, d))` |
| `datevalue(...)` | Date | `todatetime(datevalue(...))` |
| `eomonth(...)` | Date | `todatetime(eomonth(...))` |
| `eomonth(...) + N` | Date | `todatetime(eomonth(...) + N)` |
| `edate(...)` | Date | `todatetime(edate(...))` |
| `edate(...) + N` | Date | `todatetime(edate(...) + N)` |

### DateTime-Returning Functions (Incompatible with Date fields)

When these functions appear in `a!queryFilter()` value parameter with a **Date field**, wrap the entire expression in `todate()`:

| Function Pattern | Returns | Wrap Pattern |
|------------------|---------|--------------|
| `now()` | DateTime | `todate(now())` |
| `todatetime(...)` | DateTime | `todate(todatetime(...))` |
| `datetime(...)` | DateTime | `todate(datetime(...))` |
| `a!subtractDateTime(...)` | DateTime | `todate(a!subtractDateTime(...))` |
| `a!addDateTime(...)` | DateTime | `todate(a!addDateTime(...))` |
| `userdatetime(...)` | DateTime | `todate(userdatetime(...))` |

### Detection Regex Patterns {#datetime.type-detection.regex}

**For automated detection during validation:**

```bash
# Pattern 1: Date functions (return Date type)
DATE_FUNCTIONS="(today|todate|date\(|datevalue|eomonth|edate)"

# Pattern 2: DateTime functions (return DateTime type)
DATETIME_FUNCTIONS="(now|todatetime|datetime\(|a!subtractDateTime|a!addDateTime|userdatetime)"
```

**Reference:** See `/conversion-guidelines/validation-enforcement-module.md#validation.type-matching` for complete automated detection workflow.

---

## Date Function Corrections

```sail
/* ❌ WRONG - addDateTime rejects negative values */
value: a!addDateTime(startDateTime: today(), days: -30)

/* ✅ CORRECT - Use subtractDateTime for past dates */
value: a!subtractDateTime(startDateTime: now(), days: 30)
```

---

## min()/max() Return Type Casting

**The min() and max() functions return variant types that may need explicit casting for comparisons:**

```sail
/* ❌ WRONG - min() result used directly without type casting */
local!startDates: a!forEach(
  items: local!courses,
  expression: fv!item.startDate  /* Array of Date values */
),
local!earliestStart: min(local!startDates),  /* Returns variant */
local!isUrgent: local!earliestStart < today() + 30  /* May cause type error */

/* ✅ CORRECT - Cast min() result to proper type */
local!startDates: a!forEach(
  items: local!courses,
  expression: fv!item.startDate  /* Array of Date values */
),
local!earliestStart: todate(min(local!startDates)),  /* Explicit Date type */
local!isUrgent: local!earliestStart < today() + 30  /* Date comparison works */
```

### Rules:
- **Date arrays**: Wrap with `todate(min(...))` or `todate(max(...))`
- **DateTime arrays**: Wrap with `todatetime(min(...))` or `todatetime(max(...))`
- **Number arrays**: Wrap with `tointeger(...)` or `todecimal(...)` if specific type needed
- **Always cast** when using the result in comparisons or calculations

---

## text() Function with Date/DateTime Values

**The text() function CANNOT accept null values. Always check for null before calling text():**

```sail
/* ❌ WRONG - Passing null to text() causes errors */
text(a!defaultValue(fv!row['recordType!Case.fields.createdOn'], null), "MMM d, yyyy")

/* ✅ CORRECT - Check for null BEFORE calling text() */
if(
  a!isNullOrEmpty(a!defaultValue(fv!row['recordType!Case.fields.createdOn'], null)),
  "–",
  text(fv!row['recordType!Case.fields.createdOn'], "MMM d, yyyy")
)

/* ✅ CORRECT - Alternative pattern with defaultValue as fallback string */
if(
  a!isNullOrEmpty(a!defaultValue(fv!row['recordType!Case.fields.dueDate'], null)),
  "No due date",
  text(fv!row['recordType!Case.fields.dueDate'], "MM/DD/YYYY")
)
```

**Rule**: When formatting dates with text(), ALWAYS wrap in a null check that returns a fallback string (like "–" or "N/A"), NOT null.

---

## Valid Operators by Data Type

See `/conversion-guidelines/common-conversion-patterns.md#common.query-parameters` for the complete operator reference table and examples.
