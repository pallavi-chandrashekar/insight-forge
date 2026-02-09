# Manual Testing Guide - Chart Interactivity

**Status:** Requires Browser Testing
**Tasks:** TS-15 to TS-17 - Chart Interactivity

---

## Prerequisites

1. **Services Running:**
   - Frontend: http://localhost:5174
   - Backend: http://localhost:8000
   - Database: PostgreSQL (healthy)

2. **Login Credentials:**
   - Email: test@insightforge.com
   - Password: testpass123

3. **Test Data:**
   - Dataset uploaded with visualizations created
   - Access existing charts or create new ones

---

## TS-15: Zoom and Pan Functionality

### Test Steps:

1. **Open a Visualization**
   - Navigate to http://localhost:5174
   - Login with test credentials
   - Go to "Visualizations" or create a new chart
   - Select any bar, line, scatter, or area chart

2. **Test Zoom**
   - **Click and drag** on the chart to select a region
   - Expected: Chart zooms into the selected area
   - Expected: Axis scales adjust to show selected range
   - Expected: Zoom controls appear (if using Plotly)

3. **Test Pan**
   - After zooming in, **drag the chart** to move around
   - Expected: View shifts while maintaining zoom level
   - Expected: Can explore different parts of the data

4. **Test Reset**
   - **Double-click** anywhere on the chart
   - Expected: Chart resets to original full view
   - Expected: All data visible again

### Screenshot Checklist:
- [ ] Chart in default view
- [ ] Chart zoomed in (show selected region)
- [ ] Chart panned to different area
- [ ] Chart after reset to default

### Pass Criteria:
- ✅ Zoom works on all applicable chart types
- ✅ Pan works after zooming
- ✅ Reset returns to original view
- ✅ Smooth, responsive interactions

---

## TS-16: Hover Tooltips and Data Display

### Test Steps:

1. **Hover Over Data Points (Bar Chart)**
   - Open a bar chart
   - Hover mouse over each bar
   - Expected: Tooltip appears showing:
     - Category name
     - Exact value
     - Any additional data (color group, etc.)

2. **Hover Over Lines (Line Chart)**
   - Open a line chart
   - Hover over the line at different points
   - Expected: Tooltip shows:
     - X-axis value (date/category)
     - Y-axis value (number)
     - Point highlighted on line

3. **Hover Over Scatter Points**
   - Open a scatter plot
   - Hover over individual points
   - Expected: Tooltip shows:
     - X and Y values
     - Color group if applicable
     - Point highlighted

4. **Hover Over Pie Slices**
   - Open a pie chart
   - Hover over each slice
   - Expected: Tooltip shows:
     - Category name
     - Value
     - Percentage
     - Slice highlights

5. **Test Tooltip Positioning**
   - Hover over points near edges of chart
   - Expected: Tooltips don't go off-screen
   - Expected: Readable formatting

### Screenshot Checklist:
- [ ] Bar chart with tooltip
- [ ] Line chart with tooltip
- [ ] Scatter plot with tooltip
- [ ] Pie chart with tooltip
- [ ] Tooltip near edge (positioning test)

### Pass Criteria:
- ✅ Tooltips appear on all chart types
- ✅ Correct data displayed
- ✅ Tooltips positioned properly
- ✅ Clear, readable formatting
- ✅ No flickering or delays

---

## TS-17: Export and Download Functionality

### Test Steps:

1. **Find Export Button**
   - Open any chart
   - Look for Plotly's mode bar (top right of chart)
   - Expected: Icons for export options visible

2. **Export as PNG**
   - Click the "Download plot as png" icon (camera)
   - Expected: PNG file downloads
   - Expected: Filename is descriptive
   - Open downloaded file
   - Expected: Chart renders correctly
   - Expected: Resolution is good quality

3. **Export as SVG (if available)**
   - Right-click on chart or use export menu
   - Select SVG format
   - Expected: SVG file downloads
   - Open in browser or image viewer
   - Expected: Vector graphics, scalable

4. **Test Export from Different Chart Types**
   - Repeat for:
     - Bar chart
     - Line chart
     - Scatter plot
     - Pie chart
     - Heatmap
   - Expected: All export successfully

5. **Verify Export Quality**
   - Check exported images include:
     - All data points
     - Axis labels
     - Chart title
     - Legend (if applicable)
     - Proper colors

### Screenshot Checklist:
- [ ] Plotly mode bar with export icons
- [ ] Download dialog/confirmation
- [ ] Downloaded PNG file opened
- [ ] Downloaded file showing quality
- [ ] Export from each chart type

### Pass Criteria:
- ✅ Export button visible and accessible
- ✅ PNG export works for all chart types
- ✅ Downloaded files are complete and readable
- ✅ Good resolution (not pixelated)
- ✅ Filenames are descriptive

---

## Additional Interactive Features to Test

### Legend Interactions

1. **Click Legend Items**
   - On charts with legends (scatter, line with groups)
   - Click individual legend items
   - Expected: Toggle visibility of that data series
   - Click again
   - Expected: Series reappears

2. **Double-Click Legend**
   - Double-click a legend item
   - Expected: Isolate that series (hide all others)
   - Double-click again
   - Expected: Show all series

### Axis Interactions

1. **Axis Drag (if available)**
   - Try dragging axis labels
   - Expected: Pan along that axis
   - Or: No action (depends on Plotly config)

2. **Axis Zoom**
   - Some charts allow axis-specific zoom
   - Test if available

### Mode Bar Tools

Test each tool in the Plotly mode bar:
- 🏠 Reset axes (same as double-click)
- 📷 Download plot as png
- 🔍 Zoom (box select)
- ➕ Zoom in
- ➖ Zoom out
- ↔️ Pan
- 📌 Toggle spike lines
- 🔄 Toggle hover mode

---

## Browser Testing Checklist

### Browsers to Test:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (on macOS)
- [ ] Edge (if available)

### Device Types:
- [ ] Desktop (large screen)
- [ ] Tablet view (medium screen)
- [ ] Mobile view (small screen, if responsive)

---

## Known Issues to Watch For

1. **Performance with Large Datasets**
   - Charts with >1000 points may be slow
   - Tooltips may lag
   - Expected: Still functional but slower

2. **SVG Export**
   - May not be available by default in Plotly Express
   - PNG should always work

3. **Mobile Touch**
   - Touch gestures may differ from mouse
   - Pinch-to-zoom, two-finger pan
   - May not work identically

---

## Documentation Format

For each test scenario, document:

```
Test ID: TS-15
Test Name: Zoom and Pan Functionality
Date: [Date]
Tester: [Name]
Browser: [Chrome/Firefox/etc.]

Steps Performed:
1. [Step]
2. [Step]

Result: ✅ PASS / ❌ FAIL
Issues Found: [None / Description]
Screenshots: [Filename(s)]
Notes: [Any observations]
```

---

## Screenshot Organization

Save screenshots with clear names:
- `TS15_zoom_default_view.png`
- `TS15_zoom_selected_region.png`
- `TS15_zoom_panned_view.png`
- `TS16_tooltip_bar_chart.png`
- `TS16_tooltip_pie_chart.png`
- `TS17_export_button.png`
- `TS17_downloaded_png.png`

Store in: `/Users/pallavichandrashekar/Codex/insight-forge/.nodes/visualization/docs/tests/screenshots/`

---

## Final Checklist

Before marking as complete:

- [ ] All 3 test scenarios executed (TS-15, TS-16, TS-17)
- [ ] Screenshots taken for each scenario
- [ ] Results documented (PASS/FAIL)
- [ ] Issues logged (if any)
- [ ] Tested on at least 2 browsers
- [ ] Works on desktop screen size
- [ ] All chart types tested for interactivity
- [ ] Export functionality verified

---

## Next Steps After Completion

1. Update `visualization-test.docx` with results
2. Add screenshots to documentation
3. Mark Task #6 as completed
4. Create final test report
5. Document any bugs found for fixing

---

**Ready to Test!** 🧪

All backend functionality is working. The interactive features are provided by Plotly.js and should work out-of-the-box. Focus on verifying they work correctly with the InsightForge interface.

