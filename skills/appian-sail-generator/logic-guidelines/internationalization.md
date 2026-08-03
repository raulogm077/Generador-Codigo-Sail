# Internationalization in Appian Interfaces

> **Parent guide:** `/logic-guidelines/LOGIC-PRIMARY-REFERENCE.md`
>
> **Related:** `/logic-guidelines/documentation-patterns.md` - Comment patterns for requirements

---

## Appian's Built-In Internationalization

Appian handles internationalization automatically through:
- **Locale detection** from user preferences (no manual detection needed)
- **Translation sets** containing strings in multiple languages
- **Automatic language switching** based on user's configured locale

---

## Wrong - Manual Language Toggle in Mockups

**DO NOT implement manual language selection in mockups:**

```sail
/* DON'T DO THIS - Manual language switching */
local!currentLanguage: "en",  /* Appian handles this automatically */

a!buttonArrayLayout(
  buttons: {
    a!buttonWidget(
      label: "English",
      saveInto: a!save(local!currentLanguage, "en")  /* NOT NEEDED */
    ),
    a!buttonWidget(
      label: "Espanol",
      saveInto: a!save(local!currentLanguage, "es")  /* NOT NEEDED */
    )
  }
)

/* DON'T: Inline conditional translations */
a!textField(
  label: if(
    local!currentLanguage = "es",
    "Nombre",
    "First Name"
  ),  /* Creates code bloat and maintenance burden */
  value: local!firstName,
  saveInto: local!firstName
)
```

**Problems with manual approach:**
1. Code bloat - Every text label requires conditional logic
2. Maintenance burden - Adding a language means updating every conditional
3. No centralized translation management
4. Inconsistent translations across the application
5. Doesn't follow Appian best practices

---

## Correct - Use English Text in Mockups

**Write all UI text in English - production will use translation sets:**

```sail
/* DO THIS - English text only */
a!textField(
  label: "First Name",  /* TODO: Replace with translation set reference in production */
  value: local!firstName,
  saveInto: local!firstName
)

a!buttonWidget(
  label: "Submit Application",  /* TODO: Use translation set in production */
  style: "SOLID",
  saveInto: {}
)

a!richTextDisplayField(
  labelPosition: "COLLAPSED",
  value: a!richTextItem(
    text: "Welcome to the Dashboard",  /* TODO: Translation set reference needed */
    size: "LARGE",
    style: "STRONG"
  )
)
```

---

## Best Practices for Production-Ready Code

In production implementations:
1. **Reference translation sets** instead of hardcoded strings
2. **Use the user's locale** (automatic - no code needed)
3. **No language toggle buttons** required
4. **Centralize translations** in translation set objects

---

## Comment Pattern for Mockups

```sail
/* All user-facing text should include TODO comments */
label: "Application Status",  /* TODO: Replace with translation set in production */
```

---

## Related Documentation

- `/logic-guidelines/documentation-patterns.md` - Comment patterns for requirements
