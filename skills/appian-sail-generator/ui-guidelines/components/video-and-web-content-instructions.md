# a!videoField and a!webContentField — Usage Instructions

Two related media-embedding components:
- `a!videoField` — display a video inline using web URLs
- `a!webContentField` — embed an external web page (iframe-style)

Both are standalone display fields. They do **NOT** belong inside `a!richTextDisplayField`.

---

## a!videoField

### Function signature (per official Appian docs)

```sail
a!videoField(
  label,                  /* Text */
  labelPosition,          /* "ABOVE" (default) | "ADJACENT" | "JUSTIFIED" | "COLLAPSED" */
  instructions,           /* Text */
  videos,                 /* REQUIRED — built with a!webVideo() */
  helpTooltip,            /* Text */
  accessibilityText,      /* Text */
  showWhen,               /* Boolean, default true */
  marginAbove,            /* "NONE" (default), "EVEN_LESS", "LESS", "STANDARD", "MORE", "EVEN_MORE" */
  marginBelow             /* "NONE", "EVEN_LESS", "LESS", "STANDARD" (default), "MORE", "EVEN_MORE" */
)
```

> ⛔ **NO `size` parameter exists.** Do not invent one.
> ⛔ **Cannot display videos stored as Appian Documents** — must be web URLs.

### Example

```sail
a!videoField(
  label: "Welcome to the team",
  labelPosition: "ABOVE",
  videos: a!webVideo(
    source: "https://www.w3schools.com/html/mov_bbb.mp4"
  )
)
```

### Playlist of multiple videos

```sail
a!videoField(
  label: "Training series",
  videos: {
    a!webVideo(source: "https://...lesson1.mp4"),
    a!webVideo(source: "https://...lesson2.mp4"),
    a!webVideo(source: "https://...lesson3.mp4")
  }
)
```

### Supported video formats

| Platform | Formats |
|---|---|
| Chrome / Firefox | WebM, Ogg |
| iOS | MP4, 3gp, mov, mpv |
| Android | MP4, 3gp, webm, mkv |

For authenticated video sources, set up SSO between Appian and the video host.

### Feature compatibility

| Feature | Compatibility |
|---|---|
| Portals | ❌ Incompatible |
| Offline Mobile | ❌ Incompatible |
| Process Reports | ❌ Incompatible |

Docs: <https://docs.appian.com/suite/help/latest/Video_Component.html>

---

## a!webContentField

### Function signature (per official Appian docs)

```sail
a!webContentField(
  label,                  /* Text */
  labelPosition,          /* "ABOVE" (default) | "ADJACENT" | "JUSTIFIED" | "COLLAPSED" */
  instructions,           /* Text */
  helpTooltip,            /* Text */
  showWhen,               /* Boolean, default true */
  source,                 /* Safe URI — URL of external content */
  showBorder,             /* Boolean, default false */
  height,                 /* "SHORT" | "MEDIUM" (default) | "TALL" */
  altText,                /* Text — read by screen readers, shown if source fails */
  disabled,               /* Boolean, default false */
  accessibilityText,      /* Text */
  marginAbove,            /* standard margin enum */
  marginBelow             /* standard margin enum */
)
```

> ⛔ The URL parameter is called **`source`** (NOT `url`).
> ⛔ The `height` enum does NOT include `"AUTO"`. Only `SHORT`/`MEDIUM`/`TALL`.

### Example

```sail
a!webContentField(
  source: "https://example.com",
  height: "MEDIUM",
  showBorder: true,
  altText: "Example domain"
)
```

### When NOT to use a!webContentField

- ❌ Trying to embed YouTube/Vimeo → use `a!videoField` with `a!webVideo` for player controls and aspect ratio
- ❌ Internal Appian interfaces or Appian URLs — **not supported**
- ❌ Sites with `X-Frame-Options: DENY` or `frame-ancestors 'none'` — they block embedding; you'll see an empty frame
- ❌ Sites requiring OAuth/cookies from the parent window
- ❌ PDFs — many browsers will error

> 💡 **Safari handles iframe memory differently.** The web content component will display as an inline **link** when viewed in Safari. Plan your UX accordingly.

### `altText` vs `accessibilityText`

| Parameter | Purpose |
|---|---|
| `altText` | Short description, read by screen readers AND shown if source fails to load |
| `accessibilityText` | Additional info for screen readers only; never visible |

### Feature compatibility

| Feature | Compatibility |
|---|---|
| Portals | ✅ Compatible |
| Offline Mobile | ❌ Incompatible |
| Process Reports | ❌ Incompatible |

Docs: <https://docs.appian.com/suite/help/latest/Web_Content_Component.html>

---

## Validation Checklist

### For `a!videoField`
- [ ] `videos` is built with `a!webVideo(source: ...)`, not a raw URL string
- [ ] NO `size` parameter used
- [ ] NOT used in a Portal or Offline Mobile context
- [ ] Not used for Appian-hosted documents (must be web URLs)
- [ ] `labelPosition` uses the 4-value enum

### For `a!webContentField`
- [ ] Uses `source` (NOT `url`)
- [ ] `height` is one of `"SHORT"`, `"MEDIUM"`, `"TALL"`
- [ ] `source` is HTTPS (modern browsers block mixed content)
- [ ] No sensitive data in `source` query params (PII, tokens — they're logged)
- [ ] Target site is known to allow iframe embedding (no `X-Frame-Options: DENY`)
- [ ] `altText` describes the embedded content for screen readers
- [ ] NOT used for embedding videos (use `a!videoField` instead)
- [ ] NOT used for Appian-internal URLs
