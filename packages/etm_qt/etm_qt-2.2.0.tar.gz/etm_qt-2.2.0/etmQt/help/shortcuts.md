% Shortcuts

Note: On Mac OS X, use the *Command* key instead of the *Control* key.

### General

F1
:   Show this help information.
F2
:   Show information about etm.
F3
:   Check for a newer version of etm.
F4
:   Display a twelve month calendar. Use *Left* and *Right* cursor keys to change years and *Space* to return to the current year.

<center>
![](images/12monthcalendar.png "12 month calendar")
</center>

F5
:   Open the datetime calculator.

<center>
![](images/date_calculator1.png "date calculator")
![](images/date_calculator2.png "date calculator")
</center>

<center>
![](images/date_calculator3.png "date calculator")
![](images/date_calculator4.png "date calculator")
</center>

F6
:   Show local Yahoo weather information. (Requires "weather_location" in `etm.cfg`.)

<center>
![](images/weather.png "weather information")
</center>

F7
:   Show local USNO sun and moon data. (Requires "sunmoon_location" in `etm.cfg`.)

<center>
![](images/sunmoon.png "sun and moon information")
</center>

F8
:   Export items in vcalendar format to `~/.etm/etm.ics`. (Requires the python module "vobject".) If *calendars* is set in your *etm.cfg*, only items in selected calendars will be exported, otherwise all items will be exported.


Comma
:   Switch to the *day* view.
Period
:   Switch to the *week due* view.
Slash
:   Switch to the *month* view.
Semicolon
:   Switch to the *now* view.
Apostrophe
:   Switch to the *next* view.
Left Bracket
:   Switch to the *folder* view.
Right Bracket
:   Switch to the *keyword* view.
Back Slash
:   Switch to the *tag* view.
Escape
:   In the main window, clear the pattern filter and activate the view menu.
:   In dialogs, cancel any changes and close the dialog.
Tab
:   Toggle the focus between the view menu and the main window.
Space
:   Display the current date in the day, week and month views. See also *Control-J* below.
Control-A
:   Show the remaining alerts for today, if any.
Control-C
:   If you have a entry for *calendars* in your *etm.cfg* file, then open a dialog to choose which calendars to display.

<center>
![](images/calendar_selection.png "calendar selection")
</center>
Control-E
:   Show the list of file loading error messages.
Control-F
:   Enter an expression in the pattern filter to limit the display to items with matching summaries (titles) or branches. See *Filtering* in the *Overview* tab.
Control-J
:   Jump to a fuzzy parsed date in the day, week and month views. Relative days and months can be entered in this dialog. E.g., *+21* to go forward 21 days or *-1/1* to go to the first day of the previous month. See also *Space* above. *If nothing is scheduled for the specified date, the last date with scheduled items before the specified date will be selected in the day view.*
Control-L
:   Activate the view menu pop up list. You can then select a view using the up and down arrow keys or the first letter of the view name.
Control-N
:   Create a new event, note or task.
Control-P
:   Open the etm scratch pad.
Control-R
:   Create a custom report.
Control-S
:   Show the current schedule.
Control-T
:   If the action timer is inactive, create a new action timer. Otherwise toggle the timer between paused and running.
Shift Control-O
:   Open *etm.cfg* for editing.
Shift Control-C
:   Open your *auto_completions* file for editing.
Shift Control-R
:   Open your *report_specifications* file for editing.
Shift Control-T
:   If the action timer is active, stop the timer and record the action.

### Day View

Return
:   If a leaf is selected, open the details view for the leaf.
LeftArrow
:   Display the last date with scheduled items before the current. Display the week containing this date in week view and the month containing this date in month view.
RightArrow
:   Display the first date with scheduled items after the current. Display the week containing this date in week view and the month containing this date in month view.

### Week View

Double-Click
:   In a busy time slot, open the details dialog for the relevant event.
:   In an empty time slot, open a dialog to create a new event for the relevant date and time.
LeftArrow
:   Display the previous week.
RightArrow
:   Display the next week.
Control-B
:   Open a display showing the periods during the week when you are busy.


### Month View

Double-Click
:   Make the selected date visible in both the day and week views and switch to the week view.
LeftArrow
:   Move the selection to the previous month.
RightArrow
:   Move the selection to the next month.
UpArrow
:   Move the selection to the previous week.
DownArrow
:   Move the selection to the next week.


### Tree Views

The following apply to all views other than the week and month views. Hovering the mouse over a leaf displays a tooltip with the details of the relevant item.

Double-Click
:   On a branch, toggle between expanded and collapsed.
:   On a leaf, open the details dialog for the selected item.
Return
:   When a leaf is selected, open the details dialog for the selected item.
Control-/
:   Open a dialog to choose the level of expansion for the tree.
UpArrow
:   Moves the cursor to the item in the same column on the previous row. If the parent of the current item has no more rows to navigate to, the cursor moves to the relevant item in the last row of the sibling that precedes the parent.
DownArrow
:   Moves the cursor to the item in the same column on the next row. If the parent of the current item has no more rows to navigate to, the cursor moves to the relevant item in the first row of the sibling that follows the parent.
LeftArrow
:   Hides the children of the current item (if present) by collapsing a branch.
Minus
:   Same as LeftArrow.
RightArrow
:   Reveals the children of the current item (if present) by expanding a branch.
Plus
:   Same as RightArrow.
Asterisk
:   Expands all children of the current item (if present).
PageUp
:   Moves the cursor up one page.
PageDown
:   Moves the cursor down one page.
Home
:   Moves the cursor to an item in the same column of the first row of the first top-level item in the model.
End
:   Moves the cursor to an item in the same column of the last row of the last top-level item in the model.

Alphabetic and/or numeric character(s)
:   Jump to the next appearance of the character(s).

### Details view

Return
:   Edit this item.
Control-C
:   Edit a copy of this item.
Control-D
:   Delete this item.
Control-E
:   Edit the file containing this item.
Control-F
:   If the selected item is a task, enter a finish date.
Control-G
:   If the item has an *@g* entry, open it using the system default application.
Control-H
:   Show the history of changes to this item's file.
Control-M
:   Move this item to a different file.
Control-P
:   Print.
Control-R
:   If this is a repeating item, show its repetitions.
Control-T
:   Start the timer for a new action based on the selected item.
Space
:   In the "edit which instance" dialog, move the selection to the next alernative.

### Reports dialog

Escape
:   If the list of report specifications is open, close it.
Return
:   In the report specification field, add the current specification to the list if it is not already included. Use Control-S to save such changes to the list.
Control-D
:   Remove the current report specification from the list if it is included.  Use Control-S to save such changes to the list.
Control-E
:   Export the current report in CSV format.
Control-L
:   Open the list of report specifications.
Control-P
:   Print.
Control-R
:   Refresh the report using the selected report options setting.
Control-S
:   Save changes to the list of report options settings.


### Editor

Control-Return
:   Save changes if modified and close the editor.
Control-C
:   Copy selection to clipboard.
Control-I
:   Insert the contents of the *etm* scratch pad at the cursor position.
Control-P
:   Print.
Control-S
:   Save changes.
Control-V
:   Paste clipboard at cursor position.
Control-W
:   Close the editor, prompting to save changes if modified.
Control-X
:   Delete selection and copy to clipboard.
Control-Z
:   Undo.
Shift Control-Z
:   Redo.
