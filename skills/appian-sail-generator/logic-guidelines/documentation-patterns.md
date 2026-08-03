# Requirement-Driven Documentation Pattern

> **Parent guide:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Referenced from:** `claude.md` → "CAPTURING USER REQUIREMENTS IN GENERATED CODE"

When generating SAIL interfaces from requirements, add structured comments that capture business logic, validation rules, and design decisions. This creates self-documenting code that helps developers understand the "why" behind implementation choices.

---

## Three-Tier Comment Structure

**1. Interface-level header** - Overall purpose and key requirements
**2. Section-level comments** - Business purpose + field requirements
**3. Inline comments** - Complex logic explanation (validations, calculations, conditionals)

---

## Interface-Level Header Format

```sail
/*
 * [INTERFACE NAME/PURPOSE]
 *
 * Purpose: [Brief description of business purpose]
 *
 * Key Requirements:
 * - [Requirement 1]
 * - [Requirement 2]
 * - [Requirement 3]
 */
```

---

## Section-Level Comment Format

```sail
/*
 * [SECTION NAME]
 * Requirement: [Business purpose of this section]
 * Fields:
 * - Field 1 (attributes): Description
 * - Field 2 (attributes): Description
 * [Optional] Validation: [Validation rule description]
 */
```

---

## Inline Comment Format

```sail
/* Requirement: [Specific requirement this line/block implements] */
value: someComplexLogic()
```

---

## Complete Form Example

```sail
a!localVariables(
  /*
   * BOARD/COMMITTEE SUBMISSION FORM
   *
   * Purpose: Capture partner memberships on external boards/committees
   *
   * Key Requirements:
   * - Auto-populate partner info from logged-in user (read-only)
   * - Validate end date > start date
   * - Support create/edit modes with same interface
   * - Position types sourced from reference data lookup
   */

  local!organizationName,
  local!organizationType,
  local!positionType,
  local!startDate,
  local!endDate,
  local!partnerName: user(loggedinuser(), "displayName"),

  a!formLayout(
    contents: {
      /*
       * ORGANIZATION INFORMATION
       * Requirement: Capture organization details where partner serves
       * Fields:
       * - Organization Name (required, manual entry)
       * - Organization Type (optional, manual entry, examples: Non-Profit, For-Profit, Government)
       * - Organization Description (optional, free text)
       */
      a!cardLayout(
        contents: {
          a!sectionLayout(
            label: "Organization Information",
            labelColor: "STANDARD",
            contents: {
              a!textField(
                label: "Organization Name",
                value: local!organizationName,
                saveInto: local!organizationName,
                required: true(),
                placeholder: "Enter the organization name"
              ),
              a!textField(
                label: "Organization Type",
                value: local!organizationType,
                saveInto: local!organizationType,
                placeholder: "e.g., Non-Profit, For-Profit, Government, etc."
              )
            }
          )
        },
        style: "#FFFFFF",
        shape: "ROUNDED",
        showBorder: true,
        showShadow: false,
        marginBelow: "STANDARD"
      ),

      /*
       * MEMBERSHIP DETAILS
       * Requirement: Track membership dates and validate date logic
       * Fields:
       * - Position/Role (required, dropdown from reference data)
       * - Start Date (required, manual entry)
       * - End Date (optional, must be after start date if provided)
       * Validation: End date > start date
       */
      a!cardLayout(
        contents: {
          a!sectionLayout(
            label: "Membership Details",
            labelColor: "STANDARD",
            contents: {
              a!dropdownField(
                label: "Position/Role on Board or Committee",
                choiceLabels: {"Board Member", "Committee Chair", "Advisor"},
                choiceValues: {"MEMBER", "CHAIR", "ADVISOR"},
                value: local!positionType,
                saveInto: local!positionType,
                required: true(),
                placeholder: "Select a position/role"
              ),
              a!dateField(
                label: "Membership Start Date",
                value: local!startDate,
                saveInto: local!startDate,
                required: true()
              ),
              a!dateField(
                label: "Membership End Date",
                value: local!endDate,
                saveInto: local!endDate,
                helpTooltip: "Leave blank if membership is still active",
                /* Requirement: Validate end date > start date when both are provided */
                validations: if(
                  and(
                    a!isNotNullOrEmpty(local!startDate),
                    a!isNotNullOrEmpty(local!endDate),
                    local!endDate <= local!startDate
                  ),
                  "Membership End Date must be after Membership Start Date",
                  {}
                )
              )
            }
          )
        },
        style: "#FFFFFF",
        shape: "ROUNDED",
        showBorder: true,
        showShadow: false,
        marginBelow: "STANDARD"
      ),

      /*
       * PARTNER INFORMATION
       * Requirement: Auto-populate from logged-in user profile (all read-only)
       * Fields:
       * - Partner Name (displayName from user profile)
       * - Partner ID (username from user profile)
       * - Business Unit (from HR/Workday integration - placeholder for now)
       */
      a!cardLayout(
        contents: {
          a!sectionLayout(
            label: "Partner Information",
            labelColor: "STANDARD",
            contents: {
              a!textField(
                label: "Partner Name",
                /* Requirement: Auto-populate displayName from logged-in user */
                value: user(loggedinuser(), "displayName"),
                saveInto: {},
                readOnly: true(),
                helpTooltip: "Auto-populated from user profile"
              ),
              a!textField(
                label: "Partner ID",
                /* Requirement: Auto-populate username from logged-in user */
                value: user(loggedinuser(), "username"),
                saveInto: {},
                readOnly: true(),
                helpTooltip: "Auto-populated from user profile"
              ),
              a!textField(
                label: "Group/Business Unit",
                /* Requirement: Would be auto-populated from HR feed/Workday integration */
                value: "Business Unit TBD",
                saveInto: {},
                readOnly: true(),
                helpTooltip: "Auto-populated from HR system integration"
              )
            }
          )
        },
        style: "#FFFFFF",
        shape: "ROUNDED",
        showBorder: true,
        showShadow: false
      )
    },
    buttons: a!buttonLayout(
      primaryButtons: {
        a!buttonWidget(
          label: "Submit",
          style: "SOLID",
          color: "ACCENT",
          submit: true()
        )
      },
      secondaryButtons: {
        a!buttonWidget(
          label: "Cancel",
          style: "LINK"
        )
      }
    )
  )
)
```

---

## Dashboard/Grid Example

```sail
a!localVariables(
  /*
   * SALES DASHBOARD - REGIONAL PERFORMANCE
   *
   * Purpose: Display real-time sales metrics by region with drill-down capability
   *
   * Key Requirements:
   * - Show top 5 regions by revenue (query sorted descending)
   * - Color-code performance: Green >$1M, Yellow $500K-$1M, Red <$500K
   * - Filter by date range (default: current quarter)
   * - Click region to drill into rep-level details
   */

  /* Requirement: Default to current quarter for date filter */
  local!startDate: eomonth(today(), -3),
  local!endDate: today(),

  a!headerContentLayout(
    header: {
      /* KPI CARDS - Top-level metrics */
      a!cardLayout(
        contents: {
          /* Requirement: Color-code based on performance thresholds */
          a!gaugeField(
            percentage: if(
              local!revenue > 1000000,
              /* Green: Above $1M */,
              if(
                local!revenue > 500000,
                /* Yellow: $500K-$1M */,
                /* Red: Below $500K */
              )
            )
          )
        }
      )
    }
  )
)
```

---

## Chart Example

```sail
/*
 * REVENUE TREND CHART
 * Requirement: Show monthly revenue trend for last 12 months
 * Data Source: Sales record type aggregation by month
 * Interaction: Clicking a month filters detail grid below
 */
a!columnChartField(
  categories: local!monthLabels,
  series: {
    a!chartSeries(
      label: "Revenue",
      data: local!monthlyRevenue,
      /* Requirement: Highlight months below target in red */
      color: a!forEach(
        items: local!monthlyRevenue,
        expression: if(fv!item < 100000, "NEGATIVE", "ACCENT")
      )
    )
  }
)
```

---

## Grid Column Comment Pattern

For calculated or conditional columns in grids, add inline comments explaining the business rule:

```sail
a!gridField(
  data: local!cases,
  columns: {
    a!gridColumn(
      label: "Case ID",
      value: fv!row.caseId
    ),
    a!gridColumn(
      label: "Priority",
      /* REQUIREMENT: High priority cases (priority = 1) show in red,
       * medium (priority = 2) in yellow, low (priority = 3) in gray */
      value: a!tagField(
        tags: a!tagItem(
          text: fv!row.priorityLabel,
          backgroundColor: a!match(
            value: fv!row.priority,
            equals: 1, "#EF4444",  /* Red for high */
            equals: 2, "#F59E0B",  /* Yellow for medium */
            equals: 3, "#6B7280",  /* Gray for low */
            "#9CA3AF"  /* Default gray */
          )
        )
      )
    ),
    a!gridColumn(
      label: "Days Open",
      /* REQUIREMENT: Highlight cases open > 30 days in red */
      value: a!richTextDisplayField(
        value: a!richTextItem(
          text: text(fv!row.daysOpen, "#,##0"),
          color: if(fv!row.daysOpen > 30, "NEGATIVE", "STANDARD")
        )
      )
    )
  }
)
```

---

## Benefits of Requirement Comments

### 1. Traceability
- Links implementation directly back to requirements
- Easy to verify code matches business intent
- Audit trail for compliance and review

### 2. Maintainability
- Future developers understand "why" decisions were made
- Read-only fields documented with business justification
- Validation logic tied to specific requirements

### 3. Onboarding
- New team members can understand interfaces quickly
- Self-documenting code reduces questions
- Clear examples of common patterns

### 4. Quality Assurance
- QA can verify implementation against documented requirements
- Easier to catch scope drift or missing features
- Validation rules documented inline for testing

---

## When to Add Requirement Comments

### Always add comments for:
- Read-only or disabled fields (explain why)
- Complex validation logic (reference requirement)
- Auto-populated fields (explain data source)
- Conditional visibility (explain business rule)
- Calculations and derived values (explain formula)
- Non-obvious placeholder values (explain future integration)

### Optional for:
- Simple, self-explanatory fields (name, email, etc.)
- Standard UI patterns with no special logic
- Obvious relationships (save button submits form)

---

## Anti-Pattern: Undocumented Code

```sail
a!localVariables(
  local!organizationName,
  local!startDate,
  local!endDate,

  a!formLayout(
    contents: {
      /* No context about why fields exist or their business purpose */
      a!cardLayout(
        contents: {
          a!sectionLayout(
            label: "Organization Information",
            contents: {
              a!textField(
                label: "Organization Name",
                value: local!organizationName,
                saveInto: local!organizationName,
                required: true()  /* Why required? No explanation */
              )
            }
          )
        }
      ),
      a!cardLayout(
        contents: {
          a!sectionLayout(
            label: "Partner Information",
            contents: {
              a!textField(
                label: "Partner Name",
                value: user(loggedinuser(), "displayName"),
                readOnly: true()  /* Why read-only? No explanation */
              )
            }
          )
        }
      )
    }
  )
)
```

**Problems with undocumented code:**
- No explanation for read-only fields
- Validation logic appears arbitrary
- Cannot verify implementation matches requirements
- Hard to onboard new developers
- Difficult to maintain over time
