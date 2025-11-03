---
name: presentation-template
description: Create professional presentations using a predefined template with 27 slide layouts. Use this skill when creating PowerPoint presentations that require consistent design and structured layouts, including title slides, section dividers, bullet points, photo layouts, quotes, and more.
---

# Presentation Template

## Overview

This skill enables creation of professional PowerPoint presentations using a predefined template with 27 carefully designed slide layouts. The template ensures visual consistency and provides appropriate layouts for various content types including titles, sections, bullet points, images, quotes, and custom arrangements.

## Core Principles

**CRITICAL: Always use the template's predefined slide layouts.** The template contains slide master layouts that must be used to maintain design consistency. Never create slides with custom layouts outside of the provided 27 options.

**Template location:** `assets/template.pptx`

**Layout reference:** See `references/layouts.md` for detailed information about all 27 layouts

## Quick Start

```python
from pptx import Presentation

# Load the template
template_path = "assets/template.pptx"
prs = Presentation(template_path)

# Add a title slide (layout 0)
title_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_layout)
title = slide.shapes.title
title.text = "プレゼンテーションのタイトル"

# Add a content slide (layout 8: bullets with slide number)
content_layout = prs.slide_layouts[8]
slide = prs.slides.add_slide(content_layout)

# Save the presentation
prs.save("output.pptx")
```

## Workflow

### Step 1: Initialize Presentation

Always start by loading the template:

```python
from pptx import Presentation
prs = Presentation("assets/template.pptx")
```

### Step 2: Select Appropriate Layout

Choose the layout based on content type. Common layout selections:

- **Title/Cover slide**: Layout 0 or 25
- **Section divider**: Layout 1 or 2
- **Bullet points (2-4 items)**: Layout 7, 8, or 20
- **Bullet points (5-7 items)**: Layout 9
- **Text + Image (image on right)**: Layout 12, 13, or 14
- **Text + Image (image on left)**: Layout 15-19
- **Quote/Message**: Layout 3, 4, 5, or 6
- **Key points (up to 5)**: Layout 10 or 11
- **Custom/Free layout**: Layout 21, 22, or 23

For detailed layout information, read `references/layouts.md`.

### Step 3: Add Content

Use placeholders from the selected layout:

```python
# Example: Adding a slide with bullets and image (layout 20)
layout = prs.slide_layouts[20]
slide = prs.slides.add_slide(layout)

# Find and fill placeholders
for shape in slide.placeholders:
    if shape.placeholder_format.type == 1:  # TITLE
        shape.text = "スライドタイトル"
    elif shape.placeholder_format.type == 2:  # BODY
        text_frame = shape.text_frame
        text_frame.text = "第一のポイント"
        # Add more bullet points as needed
```

### Step 4: Save Output

Save the presentation to the output directory:

```python
prs.save("/mnt/user-data/outputs/presentation.pptx")
```

## Layout Selection Guide

### By Content Type

**Narrative/Story-based presentation:**
- Start: Layout 0 (title)
- Sections: Layout 1 or 2 (section dividers)
- Content: Layout 12-19 (50-50 photo layouts)
- Quotes: Layout 3, 4, 5, or 6
- End: Layout 0 or 25

**Data/Analysis presentation:**
- Start: Layout 0 (title)
- Sections: Layout 1 or 2
- Content: Layout 8, 9 (bullets)
- Key findings: Layout 10, 11 (5 key points)
- Summary: Layout 21-23 (blank for custom charts)

**Educational/Training:**
- Start: Layout 0 (title)
- Topics: Layout 8, 20, 26 (bullets with optional image)
- Steps: Layout 24 (procedure)
- Practice: Layout 21-23 (blank layouts)

### By Number of Items

- **1 main message**: Layout 3, 4, 5, 6 (quotes)
- **2-4 items**: Layout 7, 8, 20, 26 (bullets)
- **5 items**: Layout 10, 11 (key points)
- **5-7 items**: Layout 9 (extended bullets)

## Best Practices

1. **Start with layout selection** - Always determine the appropriate layout before adding content
2. **Use helper script** - Utilize `scripts/presentation_helper.py` for common operations
3. **Maintain consistency** - Use the same layout style throughout each section
4. **Leverage placeholders** - Work with the predefined placeholders rather than adding custom shapes
5. **Test layout fit** - Ensure content fits within the placeholder constraints

## Helper Functions

The `scripts/presentation_helper.py` module provides convenient functions:

```python
from scripts.presentation_helper import (
    create_presentation_from_template,
    add_slide_with_layout,
    list_available_layouts,
    LAYOUT_TITLE,
    LAYOUT_BULLETS_WITH_NUMBER,
    LAYOUT_50_50_RIGHT_PHOTO
)

# Create presentation
prs = create_presentation_from_template("assets/template.pptx")

# Add slides using constants or names
slide1 = add_slide_with_layout(prs, LAYOUT_TITLE)
slide2 = add_slide_with_layout(prs, "箇条書き")  # Partial name match
slide3 = add_slide_with_layout(prs, 12)  # By index
```

## Troubleshooting

**Issue: Layout not found**
- Solution: Use `list_available_layouts(prs)` to see all available layouts and their indices

**Issue: Content doesn't fit**
- Solution: Choose a layout with more space or split content across multiple slides

**Issue: Placeholder not found**
- Solution: Iterate through `slide.placeholders` to identify available placeholders by type

## Resources

### scripts/
- `presentation_helper.py` - Helper functions for working with the template

### references/
- `layouts.md` - Comprehensive guide to all 27 slide layouts

### assets/
- `template.pptx` - The presentation template file (must always be used as the base)
