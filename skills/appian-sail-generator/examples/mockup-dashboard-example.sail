/* ==========================================================================
 * REFERENCE MOCKUP — Case Management Dashboard
 * ==========================================================================
 * Purpose: Static SAIL mockup of a list page with KPI strip, custom filters,
 * and a grid.
 *
 * Follows patterns from:
 *   - ui-guidelines/layouts/header-content-layout-instructions.md
 *   - ui-guidelines/patterns/kpis.md (a!cardGroupLayout + a!stampField +
 *     compound a!richTextDisplayField with label + value)
 *   - ui-guidelines/components/grid-field-instructions.md (sortField discipline)
 *   - logic-guidelines/pattern-matching.md (a!match for tag colours)
 *   - logic-guidelines/array-type-initialization-guidelines.md (touniformstring,
 *     tointeger for empty arrays)
 *
 * Phase 2 conversion of this mockup:
 *   - local!cases (array of maps)          ->  a!queryRecordType(...).data
 *   - fv!row.status                         ->  fv!row['recordType!...status']
 *   - Custom search/filter UX with TODO-CONVERTER -> showSearchBox / userFilters
 * ==========================================================================
 */
a!localVariables(
  /* UI state — not entity data */
  local!searchText: "",
  local!statusFilter: null,
  local!selectedCases: tointeger({}),

  /* Sample data — hard-coded, no rand()/now()/today() per Rule 9 */
  local!cases: {
    a!map(id: 1001, caseNumber: "CASE-5847", title: "Account access issue", customer: "Acme Corp", status: "Open", priority: "High", dueDate: date(2025, 6, 12), assignedTo: "Maria Lopez"),
    a!map(id: 1002, caseNumber: "CASE-5848", title: "Billing discrepancy", customer: "Globex Inc", status: "In Progress", priority: "Medium", dueDate: date(2025, 6, 14), assignedTo: "James Chen"),
    a!map(id: 1003, caseNumber: "CASE-5849", title: "Feature request: dark mode", customer: "Initech", status: "Open", priority: "Low", dueDate: date(2025, 7, 1), assignedTo: "Maria Lopez"),
    a!map(id: 1004, caseNumber: "CASE-5850", title: "Login timeout on mobile", customer: "Acme Corp", status: "Closed", priority: "High", dueDate: date(2025, 5, 30), assignedTo: "David Kim"),
    a!map(id: 1005, caseNumber: "CASE-5851", title: "Export to PDF broken", customer: "Hooli", status: "In Progress", priority: "High", dueDate: date(2025, 6, 8), assignedTo: "James Chen"),
    a!map(id: 1006, caseNumber: "CASE-5852", title: "Account merge request", customer: "Pied Piper", status: "Open", priority: "Medium", dueDate: date(2025, 6, 20), assignedTo: "David Kim"),
    a!map(id: 1007, caseNumber: "CASE-5853", title: "Password reset loop", customer: "Globex Inc", status: "Closed", priority: "Medium", dueDate: date(2025, 5, 28), assignedTo: "Maria Lopez"),
    a!map(id: 1008, caseNumber: "CASE-5854", title: "API rate limit confusion", customer: "Initech", status: "Open", priority: "Low", dueDate: date(2025, 7, 5), assignedTo: "James Chen")
  },

  /* Derived KPI counts via wherecontains() — touniformstring per array-type-initialization-guidelines.md */
  local!openCount: count(wherecontains("Open", touniformstring(local!cases.status))),
  local!inProgressCount: count(wherecontains("In Progress", touniformstring(local!cases.status))),
  local!closedCount: count(wherecontains("Closed", touniformstring(local!cases.status))),
  local!highPriorityCount: count(wherecontains("High", touniformstring(local!cases.priority))),

  a!headerContentLayout(
    header: {
      a!sideBySideLayout(
        alignVertical: "MIDDLE",
        items: {
          a!sideBySideItem(
            item: a!richTextDisplayField(
              labelPosition: "COLLAPSED",
              value: a!richTextItem(text: "Case Management", size: "MEDIUM_PLUS", style: "STRONG")
            )
          ),
          a!sideBySideItem(
            width: "MINIMIZE",
            item: a!buttonArrayLayout(
              buttons: {
                a!buttonWidget(
                  label: "New case",
                  icon: "plus",
                  style: "SOLID",
                  color: "ACCENT"
                )
              }
            )
          )
        }
      )
    },
    contents: {
      /* Width-constrained content: gutter + WIDE_PLUS + gutter per claude.md guidance */
      a!columnsLayout(
        columns: {
          a!columnLayout(width: "AUTO"),
          a!columnLayout(
            width: "WIDE_PLUS",
            contents: {

              /* ===== KPI strip — pattern from ui-guidelines/patterns/kpis.md ===== */
              a!cardGroupLayout(
                cards: {
                  a!cardLayout(
                    contents: {
                      a!sideBySideLayout(
                        items: {
                          a!sideBySideItem(
                            width: "MINIMIZE",
                            item: a!stampField(
                              icon: "folder-open",
                              backgroundColor: "#3B82F6",
                              contentColor: "#FFFFFF",
                              size: "TINY",
                              shape: "ROUNDED",
                              labelPosition: "COLLAPSED"
                            )
                          ),
                          a!sideBySideItem(
                            width: "AUTO",
                            item: a!richTextDisplayField(
                              labelPosition: "COLLAPSED",
                              value: {
                                a!richTextItem(text: "Open Cases", color: "#6B7280", size: "STANDARD"),
                                char(10),
                                a!richTextItem(text: local!openCount, style: "STRONG", size: "LARGE", color: "#262626")
                              }
                            )
                          )
                        },
                        alignVertical: "MIDDLE",
                        spacing: "STANDARD"
                      )
                    },
                    style: "#FFFFFF",
                    showBorder: true,
                    padding: "MORE",
                    shape: "ROUNDED"
                  ),
                  a!cardLayout(
                    contents: {
                      a!sideBySideLayout(
                        items: {
                          a!sideBySideItem(
                            width: "MINIMIZE",
                            item: a!stampField(
                              icon: "clock-o",
                              backgroundColor: "#F59E0B",
                              contentColor: "#FFFFFF",
                              size: "TINY",
                              shape: "ROUNDED",
                              labelPosition: "COLLAPSED"
                            )
                          ),
                          a!sideBySideItem(
                            width: "AUTO",
                            item: a!richTextDisplayField(
                              labelPosition: "COLLAPSED",
                              value: {
                                a!richTextItem(text: "In Progress", color: "#6B7280", size: "STANDARD"),
                                char(10),
                                a!richTextItem(text: local!inProgressCount, style: "STRONG", size: "LARGE", color: "#262626")
                              }
                            )
                          )
                        },
                        alignVertical: "MIDDLE",
                        spacing: "STANDARD"
                      )
                    },
                    style: "#FFFFFF",
                    showBorder: true,
                    padding: "MORE",
                    shape: "ROUNDED"
                  ),
                  a!cardLayout(
                    contents: {
                      a!sideBySideLayout(
                        items: {
                          a!sideBySideItem(
                            width: "MINIMIZE",
                            item: a!stampField(
                              icon: "check-circle",
                              backgroundColor: "#059669",
                              contentColor: "#FFFFFF",
                              size: "TINY",
                              shape: "ROUNDED",
                              labelPosition: "COLLAPSED"
                            )
                          ),
                          a!sideBySideItem(
                            width: "AUTO",
                            item: a!richTextDisplayField(
                              labelPosition: "COLLAPSED",
                              value: {
                                a!richTextItem(text: "Closed", color: "#6B7280", size: "STANDARD"),
                                char(10),
                                a!richTextItem(text: local!closedCount, style: "STRONG", size: "LARGE", color: "#262626")
                              }
                            )
                          )
                        },
                        alignVertical: "MIDDLE",
                        spacing: "STANDARD"
                      )
                    },
                    style: "#FFFFFF",
                    showBorder: true,
                    padding: "MORE",
                    shape: "ROUNDED"
                  ),
                  a!cardLayout(
                    contents: {
                      a!sideBySideLayout(
                        items: {
                          a!sideBySideItem(
                            width: "MINIMIZE",
                            item: a!stampField(
                              icon: "exclamation-triangle",
                              backgroundColor: "#DC2626",
                              contentColor: "#FFFFFF",
                              size: "TINY",
                              shape: "ROUNDED",
                              labelPosition: "COLLAPSED"
                            )
                          ),
                          a!sideBySideItem(
                            width: "AUTO",
                            item: a!richTextDisplayField(
                              labelPosition: "COLLAPSED",
                              value: {
                                a!richTextItem(text: "High Priority", color: "#6B7280", size: "STANDARD"),
                                char(10),
                                a!richTextItem(text: local!highPriorityCount, style: "STRONG", size: "LARGE", color: "#262626")
                              }
                            )
                          )
                        },
                        alignVertical: "MIDDLE",
                        spacing: "STANDARD"
                      )
                    },
                    style: "#FFFFFF",
                    showBorder: true,
                    padding: "MORE",
                    shape: "ROUNDED"
                  )
                }
              ),

              /* ===== Filter strip — custom UX with TODO-CONVERTER per claude.md "Grid Search and Filters" ===== */
              a!columnsLayout(
                columns: {
                  a!columnLayout(
                    width: "WIDE",
                    contents: {
                      /* TODO-CONVERTER: Convert to grid showSearchBox: true */
                      a!textField(
                        label: "Search",
                        labelPosition: "COLLAPSED",
                        placeholder: "Search cases...",
                        value: local!searchText,
                        saveInto: local!searchText
                      )
                    }
                  ),
                  a!columnLayout(
                    width: "NARROW_PLUS",
                    contents: {
                      /* TODO-CONVERTER: Convert to userFilter on Case.status if available */
                      a!dropdownField(
                        label: "Status",
                        labelPosition: "COLLAPSED",
                        placeholder: "All statuses",
                        choiceLabels: {"Open", "In Progress", "Closed"},
                        choiceValues: {"Open", "In Progress", "Closed"},
                        value: local!statusFilter,
                        saveInto: local!statusFilter
                      )
                    }
                  )
                }
              ),

              /* ===== Grid — sortField discipline per grid-field-instructions.md ===== */
              a!gridField(
                labelPosition: "COLLAPSED",
                data: local!cases,
                columns: {
                  a!gridColumn(label: "Case #", sortField: "caseNumber", value: fv!row.caseNumber, width: "NARROW"),
                  a!gridColumn(label: "Title", sortField: "title", value: fv!row.title),
                  a!gridColumn(label: "Customer", sortField: "customer", value: fv!row.customer, width: "NARROW"),
                  a!gridColumn(
                    label: "Status",
                    sortField: "status",
                    /* Tag colour via a!match() — exact-value pattern matching per logic-guidelines/pattern-matching.md */
                    value: a!tagField(
                      labelPosition: "COLLAPSED",
                      tags: a!tagItem(
                        text: fv!row.status,
                        backgroundColor: a!match(
                          value: fv!row.status,
                          equals: "Open", then: "ACCENT",
                          equals: "In Progress", then: "WARN",
                          equals: "Closed", then: "POSITIVE",
                          default: "SECONDARY"
                        )
                      )
                    ),
                    width: "NARROW"
                  ),
                  a!gridColumn(label: "Priority", sortField: "priority", value: fv!row.priority, width: "NARROW"),
                  a!gridColumn(label: "Due", sortField: "dueDate", value: text(fv!row.dueDate, "MMM d, yyyy"), width: "NARROW"),
                  /* Computed column — NO sortField per grid-field-instructions.md */
                  a!gridColumn(label: "Assigned to", value: fv!row.assignedTo)
                },
                selectionValue: local!selectedCases,
                selectionSaveInto: local!selectedCases,
                selectable: true,
                pageSize: 25
              )
            }
          ),
          a!columnLayout(width: "AUTO")
        }
      )
    },
    backgroundColor: "#F5F6F8"
  )
)
