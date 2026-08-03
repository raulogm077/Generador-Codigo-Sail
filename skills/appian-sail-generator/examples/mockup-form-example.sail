/* ==========================================================================
 * REFERENCE MOCKUP — Employee Onboarding Form
 * ==========================================================================
 * Purpose: Static SAIL mockup of a single-step create form.
 *
 * Follows patterns from:
 *   - ui-guidelines/layouts/form-layout-instructions.md ("Basic Form Structure":
 *     a!cardLayout wraps a!sectionLayout sections inside contents)
 *   - logic-guidelines/null-safety-quick-ref.md (a!defaultValue for nullable
 *     booleans used in conditionals)
 *   - logic-guidelines/functions-reference.md#email-validation-pattern
 *   - logic-guidelines/choice-field-patterns.md (single checkbox uninitialised
 *     for unchecked, isNotNullOrEmpty for showWhen)
 *
 * Phase 2 conversion of this mockup:
 *   - local!isUpdate / local!cancel  ->  ri!isUpdate / ri!cancel
 *   - local!employee.*                ->  ri!employee['recordType!...fields.{uuid}*']
 *   - TODO-CONVERTER: Set X to Y      ->  resolved into a!save() in submit button
 * ==========================================================================
 */
a!localVariables(
  /* TODO-CONVERTER: Transform to ri!isUpdate */
  local!isUpdate: false(),
  /* TODO-CONVERTER: Transform to ri!cancel */
  local!cancel: false(),

  /* Form data — single map represents the employee entity */
  local!employee: a!map(
    firstName: "",
    lastName: "",
    email: "",
    hireDate: null,
    department: null,
    isContractor: null
  ),

  a!formLayout(
    titleBar: if(a!defaultValue(local!isUpdate, false()), "Update Employee", "Add Employee"),
    contentsWidth: "MEDIUM",
    contents: {
      /* a!cardLayout wraps sections per "Basic Form Structure" in form-layout-instructions.md */
      a!cardLayout(
        contents: {
          /* REQUIREMENT: Capture employee identity and onboarding details */
          a!sectionLayout(
            label: "Identity",
            labelColor: "STANDARD",
            contents: {
              a!columnsLayout(
                columns: {
                  a!columnLayout(
                    contents: {
                      a!textField(
                        label: "First name",
                        value: local!employee.firstName,
                        saveInto: local!employee.firstName,
                        required: true,
                        characterLimit: 50
                      )
                    }
                  ),
                  a!columnLayout(
                    contents: {
                      a!textField(
                        label: "Last name",
                        value: local!employee.lastName,
                        saveInto: local!employee.lastName,
                        required: true,
                        characterLimit: 50
                      )
                    }
                  )
                }
              ),
              /* REQUIREMENT: Validate email format (SAIL has no regex — pattern
                 from logic-guidelines/functions-reference.md#email-validation-pattern) */
              a!textField(
                label: "Work email",
                value: local!employee.email,
                saveInto: local!employee.email,
                required: true,
                validations: {
                  if(
                    and(
                      a!isNotNullOrEmpty(local!employee.email),
                      or(
                        not(contains(local!employee.email, "@")),
                        not(contains(local!employee.email, "."))
                      )
                    ),
                    "Enter a valid email address",
                    ""
                  )
                }
              )
            }
          ),
          a!sectionLayout(
            label: "Onboarding",
            labelColor: "STANDARD",
            contents: {
              a!columnsLayout(
                columns: {
                  a!columnLayout(
                    contents: {
                      a!dateField(
                        label: "Hire date",
                        value: local!employee.hireDate,
                        saveInto: local!employee.hireDate,
                        required: true,
                        validations: {
                          /* REQUIREMENT: Hire date cannot be in the past. The if()
                             short-circuit pattern protects against null comparison
                             (per logic-guidelines/null-safety-quick-ref.md). */
                          if(
                            a!isNotNullOrEmpty(local!employee.hireDate),
                            if(local!employee.hireDate < today(), "Hire date cannot be in the past", ""),
                            ""
                          )
                        }
                      )
                    }
                  ),
                  a!columnLayout(
                    contents: {
                      a!dropdownField(
                        label: "Department",
                        placeholder: "Select a department",
                        choiceLabels: {"Engineering", "Sales", "Marketing", "Operations", "Finance"},
                        choiceValues: {"Engineering", "Sales", "Marketing", "Operations", "Finance"},
                        value: local!employee.department,
                        saveInto: local!employee.department,
                        required: true
                      )
                    }
                  )
                }
              ),
              /* Single-checkbox pattern per choice-field-patterns.md:
                 local!isContractor stays null (uninitialised) when unchecked.
                 NOT initialised to false() — that would be a different state. */
              a!checkboxField(
                label: "Employment type",
                labelPosition: "COLLAPSED",
                choiceLabels: {"Contractor (instead of full-time)"},
                choiceValues: {true()},
                value: local!employee.isContractor,
                saveInto: local!employee.isContractor
              )
            }
          )
        },
        style: "NONE",
        showBorder: true,
        showShadow: false,
        shape: "ROUNDED",
        padding: "STANDARD"
      )
    },
    buttons: a!buttonLayout(
      primaryButtons: {
        /* TODO-CONVERTER: Set isActive to true */
        /* TODO-CONVERTER: Set createdBy to loggedInUser() */
        /* TODO-CONVERTER: Set createdOn to now() */
        a!buttonWidget(
          label: if(a!defaultValue(local!isUpdate, false()), "Update", "Submit"),
          submit: true(),
          style: "SOLID",
          color: "ACCENT"
        )
      },
      secondaryButtons: {
        /* TODO-CONVERTER: Set local!cancel to true, transform to ri!cancel */
        a!buttonWidget(
          label: "Cancel",
          saveInto: a!save(local!cancel, true()),
          style: "OUTLINE"
        )
      }
    )
  )
)
