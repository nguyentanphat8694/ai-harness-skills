# Dependency tracing checklist (follow every direction to the leaves)

`scripts/trace_deps.py` produces leads for most items; this list says what each means. Its `project_calls` section lists every call into a class defined in the project (data layer, caches, services, static helpers), whatever the naming convention, so follow those first: they lead to the SQL, tables and shared state. Do not assume the project follows names like `*BLL`/`*DAL`; check how the project actually layers its code.

1. **UI**: `*.Designer.cs` (controls, properties, TabIndex, anchors, data bindings), `*.resx` (strings, images, captions), parent/base form (`: frmBase`). Logic in the base form belongs to this form too.
2. **Code-behind**: every partial class, every `#region`, every event handler (both `+=` wired in Designer and VB `Handles`).
3. **Entry/exit**: constructor/parameters, public properties, `DialogResult`, return values; **who opens this form** and what they pass.
4. **Child forms/UserControls** opened or embedded; dynamically created controls (`new Button`, `Controls.Add`).
5. **Business/data layer**: BLL/Service/DAL/Repository/Helper called, followed method by method, not just class name.
6. **Database**: `SqlCommand`/`CommandText`/hand-concatenated SQL/TableAdapter/DataSet (`.xsd`)/ORM; stored procedures, triggers, views, functions (read the body when a script exists).
7. **Reports/printing**: `.rdlc`, `.rpt`, `ReportViewer`, `PrintDocument`, Excel/PDF export.
8. **Global state**: `Session`/`CurrentUser`/`Global`/static classes, `Settings.Default`, `app.config`, Registry, `.ini` files.
9. **Permissions**: where `Visible/Enabled/ReadOnly` is set by role, the permission table, check functions.
10. **External integrations**: printers, scales, barcode readers, COM/Interop, email, web services, FTP, file system.
11. **Hidden behavior**: `ProcessCmdKey`, `KeyDown/KeyPress/KeyPreview`, shortcuts (`ShortcutKeys`), `Timer`, `BackgroundWorker`/`Thread`/`Task`, drag-drop, context menus, `FormClosing/Load/Shown/Activated`, tab order, auto-complete, date/number/currency formatting by culture.
12. **Third-party UI libraries** (DevExpress, Telerik, Infragistics, Syncfusion...): grid configuration (grouping, summaries, formats, lookups, editor validation) also holds business logic.
13. **Auto-calculated / auto-filled fields** (see [functions-fn.md](functions-fn.md)): handlers assigning `.Text/.Value/.SelectedValue/.Checked/.Visible` of one control from another; helper functions returning derived values; `DataColumn.Expression`; unbound/summary grid columns; formulas in SQL/SP/computed columns.

Searching: use `scripts/search_code.py` (decodes UTF-16 and legacy code pages) instead of raw grep; raw grep returns nothing for UTF-16 files and looks like absence. The `grep` lines below are fine only after `search_code.py --list-encodings` shows no hard encodings.

Mechanical gate helpers:
```bash
grep -c "_Click\|_Changed\|_Validating\|_KeyDown\|_CellValidating\|_Load\|_FormClosing" FormX.cs
grep -n "MessageBox.Show\|MsgBox" FormX.cs
grep -n "CommandText\|ExecuteReader\|ExecuteNonQuery\|StoredProcedure\|SqlDataAdapter\|TableAdapter" FormX.cs Bll/*.cs Dal/*.cs
```
