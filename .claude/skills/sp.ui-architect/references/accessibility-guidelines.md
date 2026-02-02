# Accessibility Guidelines

WCAG AA compliance checklist and implementation guidance for web applications.

## Table of Contents
- Perceivable
- Operable
- Understandable
- Robust
- Quick Reference Checklist

---

## 1. Perceivable

Information and UI components must be presentable to users in ways they can perceive.

### 1.1 Text Alternatives

**Requirement**: Provide text alternatives for non-text content.

**Implementation**:
- Images: Add descriptive `alt` text
  - Decorative images: `alt=""` (empty)
  - Informative images: Describe content/function
  - Complex images: Provide long description
- Icons: Use `aria-label` or `aria-labelledby`
- Form inputs: Associate with `<label>` elements
- Buttons: Use text or `aria-label` for icon-only buttons

**Examples**:
```html
<!-- Good -->
<img src="chart.png" alt="Sales increased 25% in Q4">
<button aria-label="Close dialog">
  <XIcon />
</button>

<!-- Bad -->
<img src="chart.png" alt="chart">
<button><XIcon /></button>
```

### 1.2 Color Contrast

**Requirement**: Text and interactive elements must have sufficient contrast.

**Standards**:
- Normal text (< 18pt): 4.5:1 contrast ratio
- Large text (≥ 18pt or 14pt bold): 3:1 contrast ratio
- UI components and graphics: 3:1 contrast ratio
- Focus indicators: 3:1 contrast ratio

**Implementation**:
- Use contrast checker tools (WebAIM, Chrome DevTools)
- Test with dark mode if supported
- Avoid light gray text on white backgrounds
- Ensure link text is distinguishable

**Common Issues**:
- Gray text (#999) on white (#FFF): 2.85:1 ❌ (fails)
- Dark gray (#595959) on white: 7:1 ✅ (passes)
- Blue links (#0066CC) on white: 7.7:1 ✅ (passes)

### 1.3 Color Independence

**Requirement**: Don't use color as the only means of conveying information.

**Implementation**:
- Add icons to status indicators (✓ success, ⚠ warning, ✗ error)
- Use patterns or textures in charts
- Underline links in body text
- Add text labels to color-coded items

**Examples**:
```html
<!-- Good -->
<span class="status-success">
  <CheckIcon /> Completed
</span>

<!-- Bad -->
<span class="text-green">Completed</span>
```

### 1.4 Responsive and Zoom

**Requirement**: Content must be accessible at different sizes and zoom levels.

**Implementation**:
- Support 200% zoom without horizontal scrolling
- Use relative units (rem, em) instead of px for text
- Ensure touch targets are ≥44x44px
- Test at different viewport sizes
- Avoid fixed positioning that breaks at zoom

---

## 2. Operable

UI components and navigation must be operable.

### 2.1 Keyboard Accessibility

**Requirement**: All functionality available via keyboard.

**Implementation**:
- All interactive elements focusable (Tab key)
- Logical tab order (follows visual order)
- Skip links for navigation
- No keyboard traps (can Tab out of all elements)
- Custom controls handle keyboard events

**Key Patterns**:
- **Tab**: Move forward through interactive elements
- **Shift+Tab**: Move backward
- **Enter/Space**: Activate buttons and links
- **Esc**: Close modals and dropdowns
- **Arrow keys**: Navigate within components (menus, tabs, lists)

**Examples**:
```jsx
// Good: Custom button with keyboard support
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
>
  Click me
</div>

// Better: Use native button
<button onClick={handleClick}>Click me</button>
```

### 2.2 Focus Management

**Requirement**: Focus must be visible and managed appropriately.

**Implementation**:
- Visible focus indicators (outline, ring, border)
- Focus indicator contrast ≥3:1
- Don't remove focus styles without replacement
- Manage focus in dynamic content:
  - Modal opens: Focus first interactive element
  - Modal closes: Return focus to trigger
  - Content loads: Announce to screen readers
  - Error occurs: Focus error message

**CSS Example**:
```css
/* Good: Visible focus indicator */
button:focus-visible {
  outline: 2px solid #0066CC;
  outline-offset: 2px;
}

/* Bad: Removing focus styles */
button:focus {
  outline: none; /* ❌ Don't do this */
}
```

### 2.3 Timing

**Requirement**: Users have enough time to read and interact with content.

**Implementation**:
- No time limits, or allow users to extend/disable
- Pause, stop, or hide auto-updating content
- Warn before session timeout (with option to extend)
- Auto-save form data

**Examples**:
- Session timeout: Show warning 2 minutes before, allow extension
- Carousel: Provide pause button
- Notifications: Don't auto-dismiss critical messages

### 2.4 Navigation

**Requirement**: Provide ways to navigate and find content.

**Implementation**:
- Skip links to main content
- Descriptive page titles
- Logical heading hierarchy (h1 → h2 → h3)
- Breadcrumbs for deep navigation
- Search functionality
- Consistent navigation across pages

**Heading Structure**:
```html
<h1>Page Title</h1>
  <h2>Section 1</h2>
    <h3>Subsection 1.1</h3>
    <h3>Subsection 1.2</h3>
  <h2>Section 2</h2>
    <h3>Subsection 2.1</h3>
```

---

## 3. Understandable

Information and UI operation must be understandable.

### 3.1 Readable

**Requirement**: Text content must be readable and understandable.

**Implementation**:
- Set language attribute: `<html lang="en">`
- Use clear, simple language
- Define abbreviations on first use
- Provide pronunciation for unusual words
- Reading level appropriate for audience

### 3.2 Predictable

**Requirement**: Web pages appear and operate in predictable ways.

**Implementation**:
- Consistent navigation across pages
- Consistent component behavior
- No unexpected context changes on focus
- Warn before opening new windows/tabs
- Form submission requires explicit action (button click)

**Examples**:
```html
<!-- Good: Explicit action -->
<button type="submit">Submit Form</button>

<!-- Bad: Auto-submit on change -->
<select onChange={submitForm}> <!-- ❌ Unexpected -->
```

### 3.3 Input Assistance

**Requirement**: Help users avoid and correct mistakes.

**Implementation**:
- Label all form inputs
- Provide clear error messages
- Suggest corrections for errors
- Allow review before final submission
- Prevent errors (validation, constraints)
- Confirm destructive actions

**Error Message Pattern**:
```html
<label for="email">Email</label>
<input
  id="email"
  type="email"
  aria-invalid="true"
  aria-describedby="email-error"
>
<span id="email-error" role="alert">
  Please enter a valid email address (e.g., name@example.com)
</span>
```

---

## 4. Robust

Content must be robust enough to work with assistive technologies.

### 4.1 Semantic HTML

**Requirement**: Use valid, semantic HTML.

**Implementation**:
- Use semantic elements: `<nav>`, `<main>`, `<article>`, `<aside>`, `<header>`, `<footer>`
- Use native form controls when possible
- Validate HTML (no duplicate IDs, proper nesting)
- Use ARIA only when semantic HTML isn't sufficient

**Semantic Structure**:
```html
<header>
  <nav aria-label="Main navigation">
    <!-- Navigation links -->
  </nav>
</header>

<main>
  <article>
    <h1>Article Title</h1>
    <!-- Content -->
  </article>
</main>

<footer>
  <!-- Footer content -->
</footer>
```

### 4.2 ARIA (Accessible Rich Internet Applications)

**Requirement**: Use ARIA to enhance accessibility when semantic HTML isn't enough.

**ARIA Principles**:
1. Use semantic HTML first
2. Don't override native semantics
3. All interactive ARIA controls must be keyboard accessible
4. Don't use `role="presentation"` or `aria-hidden="true"` on focusable elements

**Common ARIA Patterns**:

**Buttons**:
```html
<button aria-label="Close">×</button>
<button aria-expanded="false" aria-controls="menu">Menu</button>
```

**Live Regions** (dynamic content):
```html
<div role="status" aria-live="polite">
  Loading...
</div>

<div role="alert" aria-live="assertive">
  Error: Form submission failed
</div>
```

**Modal Dialog**:
```html
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-desc"
>
  <h2 id="dialog-title">Confirm Delete</h2>
  <p id="dialog-desc">Are you sure you want to delete this item?</p>
  <button>Cancel</button>
  <button>Delete</button>
</div>
```

**Tabs**:
```html
<div role="tablist" aria-label="Settings">
  <button role="tab" aria-selected="true" aria-controls="panel-1">
    General
  </button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">
    Privacy
  </button>
</div>
<div role="tabpanel" id="panel-1">
  <!-- General settings -->
</div>
```

---

## Quick Reference Checklist

Use this checklist when designing UI components:

### Visual Design
- [ ] Text contrast ≥4.5:1 (normal text) or ≥3:1 (large text)
- [ ] Focus indicators visible with ≥3:1 contrast
- [ ] Touch targets ≥44x44px
- [ ] Information not conveyed by color alone
- [ ] Content readable at 200% zoom

### Keyboard
- [ ] All interactive elements keyboard accessible
- [ ] Logical tab order
- [ ] Visible focus indicators
- [ ] No keyboard traps
- [ ] Esc closes modals/dropdowns

### Screen Readers
- [ ] Images have alt text
- [ ] Form inputs have labels
- [ ] Icon-only buttons have aria-label
- [ ] Semantic HTML used (nav, main, article, etc.)
- [ ] Headings in logical order (h1 → h2 → h3)
- [ ] ARIA labels for dynamic content

### Forms
- [ ] All inputs have associated labels
- [ ] Error messages clear and specific
- [ ] Errors announced to screen readers
- [ ] Required fields marked
- [ ] Validation doesn't rely on color alone

### Dynamic Content
- [ ] Loading states announced (aria-live)
- [ ] Focus managed on content changes
- [ ] Errors announced (role="alert")
- [ ] Modal traps focus, returns on close

### Navigation
- [ ] Skip link to main content
- [ ] Consistent navigation across pages
- [ ] Descriptive page titles
- [ ] Breadcrumbs for deep navigation

### Testing
- [ ] Test with keyboard only (unplug mouse)
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Test at 200% zoom
- [ ] Test with browser extensions (axe DevTools)
- [ ] Test with real users with disabilities

---

## Testing Tools

**Browser Extensions**:
- axe DevTools (Chrome, Firefox)
- WAVE (Chrome, Firefox)
- Lighthouse (Chrome DevTools)

**Screen Readers**:
- NVDA (Windows, free)
- JAWS (Windows, paid)
- VoiceOver (macOS, iOS, built-in)
- TalkBack (Android, built-in)

**Contrast Checkers**:
- WebAIM Contrast Checker
- Chrome DevTools (Inspect → Accessibility)
- Contrast Ratio (online tool)

**Automated Testing**:
- jest-axe (Jest integration)
- @axe-core/react (React integration)
- pa11y (CLI tool)

---

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Articles](https://webaim.org/articles/)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
