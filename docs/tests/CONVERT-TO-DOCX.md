# Converting Test Documentation to DOCX Format

The test documentation has been created in Markdown format (.md files). To convert to Microsoft Word (.docx) format with screenshots, follow the instructions below.

---

## Quick Conversion Method

### Using Pandoc (Best Quality)

```bash
# Install pandoc (one-time setup)
# macOS:
brew install pandoc

# Linux:
sudo apt-get install pandoc

# Windows:
# Download from https://pandoc.org/installing.html

# Convert the main test plan
cd docs/tests
pandoc query-engine-test-plan.md \
  -o query-engine-test.docx \
  --toc \
  --toc-depth=3 \
  --highlight-style=tango \
  --reference-doc=template.docx  # Optional: use custom template

# Convert the manual testing guide
pandoc MANUAL-TESTING-GUIDE.md \
  -o manual-testing-guide.docx \
  --toc \
  --toc-depth=2
```

---

## Alternative Methods

### Method 1: Microsoft Word (Native)

1. **Open Word**
2. **File → Open**
3. Browse to `docs/tests/query-engine-test-plan.md`
4. Word will automatically convert Markdown
5. **File → Save As → Word Document (.docx)**
6. Edit and add screenshots as needed

### Method 2: Google Docs

1. **Upload to Google Drive**
   - Go to drive.google.com
   - Upload `query-engine-test-plan.md`

2. **Open with Google Docs**
   - Right-click the file
   - "Open with" → "Google Docs"
   - Markdown will be converted

3. **Download as DOCX**
   - File → Download → Microsoft Word (.docx)

### Method 3: Visual Studio Code

1. **Install Extension**
   - Open VS Code
   - Install "Markdown PDF" or "Markdown to Word" extension

2. **Convert**
   - Open markdown file
   - Right-click → "Markdown to Word"
   - Or use Command Palette (Cmd/Ctrl+Shift+P) → "Markdown: Export to DOCX"

### Method 4: Online Converters

**Recommended Sites:**
- https://www.markdowntoword.com/ (Free, no registration)
- https://cloudconvert.com/md-to-docx (High quality)
- https://dillinger.io/ (Live preview + export)
- https://www.zamzar.com/ (Batch conversion)

**Steps:**
1. Go to any converter site
2. Upload `.md` file
3. Click "Convert"
4. Download `.docx` file

---

## Adding Screenshots to DOCX

### After Conversion

1. **Open the DOCX file**

2. **Find Screenshot Placeholders**
   - Look for text like `[Insert screenshot: Query results]`
   - These are marked with 📸 emoji in the manual guide

3. **Insert Actual Screenshots**
   - Delete placeholder text
   - Insert → Picture → This Device
   - Select your screenshot
   - Resize and position as needed

4. **Add Captions**
   - Right-click image → Insert Caption
   - Use format: "Figure X.Y: Description"

5. **Format Consistently**
   - Same width for all screenshots (e.g., 6 inches)
   - Center alignment
   - Add border if desired (Picture Format → Picture Border)

### Screenshot Checklist

For comprehensive documentation, capture these screenshots:

#### Query Execution (10 screenshots)
- [ ] 1.1 - Login page
- [ ] 1.2 - Upload dialog
- [ ] 1.3 - Upload success
- [ ] 1.4 - Query page interface
- [ ] 1.5 - SQL query entered
- [ ] 1.6 - Loading indicator
- [ ] 1.7 - Query results table
- [ ] 1.8 - Execution time display
- [ ] 1.9 - Save query dialog
- [ ] 1.10 - Success message

#### Pandas Operations (7 screenshots)
- [ ] 3.1 - Pandas interface
- [ ] 3.2 - Filter operation
- [ ] 3.3 - Sort operation
- [ ] 3.4 - Head operation
- [ ] 3.5 - Operations chain
- [ ] 3.6 - Results display
- [ ] 3.7 - Generated code

#### Natural Language (6 screenshots)
- [ ] 4.1 - NL interface
- [ ] 4.2 - Question entered
- [ ] 4.3 - Processing indicator
- [ ] 4.4 - Generated SQL
- [ ] 4.5 - NL results
- [ ] 4.6 - Results table

#### Query History (6 screenshots)
- [ ] 5.1 - History page
- [ ] 5.2 - Query list
- [ ] 5.3 - Filtered history
- [ ] 5.4 - Query details modal
- [ ] 5.5 - Rerun results
- [ ] 5.6 - Save As dialog

#### Error Handling (3 screenshots)
- [ ] 6.1 - Invalid SQL
- [ ] 6.2 - Error message
- [ ] 6.3 - Error state

#### Additional (5 screenshots)
- [ ] 7.1 - Column selection
- [ ] 8.1 - Complex WHERE
- [ ] 9.1 - Export options
- [ ] 9.2 - Downloaded CSV
- [ ] 10.1 - Performance metrics

**Total: 37 screenshots needed for complete documentation**

---

## Professional Formatting Tips

### Document Structure

1. **Title Page**
   - Add company logo
   - Document title
   - Version number
   - Date
   - Author/Team name

2. **Table of Contents**
   - Auto-generated in Word
   - References → Table of Contents → Automatic
   - Update after adding screenshots

3. **Headers and Footers**
   - Header: Document title
   - Footer: Page numbers, date, confidential notice

4. **Styling**
   - Use consistent heading styles (Heading 1, 2, 3)
   - Code blocks: Courier New, 10pt, gray background
   - Tables: Grid table style
   - Callouts: Use text boxes for important notes

### Screenshot Best Practices

1. **Capture Quality**
   - Use full-resolution screenshots
   - Crop to show only relevant area
   - Ensure text is readable

2. **Annotation**
   - Use arrows to highlight important elements
   - Add text boxes for explanations
   - Use consistent colors (e.g., red for errors, green for success)

3. **Consistency**
   - Same zoom level for similar screenshots
   - Same window size
   - Same theme/appearance

4. **Tools**
   - macOS: Cmd+Shift+4 (area), Cmd+Shift+5 (options)
   - Windows: Win+Shift+S (Snipping Tool)
   - Chrome: Full page screenshot extensions
   - Annotation: Skitch, Snagit, macOS Markup

---

## Complete Workflow

### 1. Convert Markdown to DOCX

```bash
# Using Pandoc with table of contents
pandoc query-engine-test-plan.md \
  -o query-engine-test.docx \
  --toc \
  --toc-depth=3 \
  --highlight-style=tango
```

### 2. Run Manual Tests

```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Start frontend (in new terminal)
cd frontend
npm run dev

# Follow MANUAL-TESTING-GUIDE.md
# Capture screenshots at each step
```

### 3. Insert Screenshots

- Open `query-engine-test.docx`
- Find placeholder text
- Insert corresponding screenshot
- Add caption and format

### 4. Final Polish

- Update table of contents
- Check page breaks
- Verify all images are visible
- Spell check
- Review formatting

### 5. Save Final Version

```
query-engine-test-FINAL-v1.0-2026-01-26.docx
```

---

## File Locations

### Source Files (Markdown)
```
docs/tests/
├── README.md                      # Overview
├── query-engine-test-plan.md      # Main test plan (44 scenarios)
├── MANUAL-TESTING-GUIDE.md        # Step-by-step guide (10 workflows)
├── IMPLEMENTATION-SUMMARY.md      # Implementation summary
└── CONVERT-TO-DOCX.md            # This file
```

### Target Files (After Conversion)
```
docs/tests/
├── query-engine-test.docx         # Main test documentation with screenshots
├── manual-testing-guide.docx      # Manual testing workflows
└── implementation-summary.docx    # Summary report
```

### Screenshots Directory (Create this)
```
docs/tests/screenshots/
├── 01-query-execution/
│   ├── 01-login.png
│   ├── 02-upload.png
│   └── ...
├── 02-pandas-operations/
│   └── ...
├── 03-natural-language/
│   └── ...
├── 04-query-history/
│   └── ...
└── 05-error-handling/
    └── ...
```

---

## Batch Conversion Script

Save this as `convert_all.sh`:

```bash
#!/bin/bash
# Convert all test documentation to DOCX

echo "Converting test documentation to DOCX..."

cd docs/tests

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "Error: pandoc is not installed"
    echo "Install with: brew install pandoc"
    exit 1
fi

# Convert each file
echo "Converting test plan..."
pandoc query-engine-test-plan.md \
  -o query-engine-test.docx \
  --toc --toc-depth=3 --highlight-style=tango

echo "Converting manual guide..."
pandoc MANUAL-TESTING-GUIDE.md \
  -o manual-testing-guide.docx \
  --toc --toc-depth=2 --highlight-style=tango

echo "Converting implementation summary..."
pandoc IMPLEMENTATION-SUMMARY.md \
  -o implementation-summary.docx \
  --toc --toc-depth=2 --highlight-style=tango

echo ""
echo "✓ Conversion complete!"
echo ""
echo "Created files:"
echo "  - query-engine-test.docx"
echo "  - manual-testing-guide.docx"
echo "  - implementation-summary.docx"
echo ""
echo "Next steps:"
echo "  1. Open DOCX files in Microsoft Word"
echo "  2. Run manual tests and capture screenshots"
echo "  3. Insert screenshots at placeholder locations"
echo "  4. Add captions and final formatting"
echo "  5. Save final version"
```

Run with:
```bash
chmod +x convert_all.sh
./convert_all.sh
```

---

## Template DOCX (Optional)

Create a custom Word template with your company branding:

1. **Create template.docx**
   - Set fonts, colors, styles
   - Add header with logo
   - Set footer format
   - Save as `template.docx`

2. **Use template in conversion**
   ```bash
   pandoc query-engine-test-plan.md \
     -o query-engine-test.docx \
     --reference-doc=template.docx
   ```

---

## Quality Checklist

Before finalizing DOCX:

### Content
- [ ] All sections present
- [ ] All test cases documented
- [ ] All screenshots inserted
- [ ] All tables formatted
- [ ] All code blocks formatted
- [ ] All links working

### Formatting
- [ ] Consistent heading styles
- [ ] Table of contents updated
- [ ] Page numbers correct
- [ ] Headers/footers consistent
- [ ] Screenshots properly sized
- [ ] Captions added
- [ ] Page breaks appropriate

### Review
- [ ] Spell check passed
- [ ] Grammar check passed
- [ ] Technical accuracy verified
- [ ] Screenshots clear and relevant
- [ ] Version number correct
- [ ] Date updated

---

## Support

**Conversion Issues?**
- Check pandoc installation: `pandoc --version`
- Ensure file paths are correct
- Try online converter as backup
- Contact IT support for enterprise tools

**Need Help?**
- Slack: #insightforge-docs
- Email: docs@company.com
- Wiki: https://wiki.company.com/test-docs

---

**Happy Converting! 📄 → 📝**
