% Views

### Day

All scheduled (dated) items appear in this view, grouped by date and sorted by starting time and item type.  Hovering the mouse over an item brings up a tooltip with details.

<center>
![](images/day_view.png "day view")
</center>

Double clicking on an item or pressing *Return* with an item selected opens a details dialog for the item with further options. Press F1 when the details dialog is active for help information on that view.

<center>
![](images/details_view.png "details view")
</center>

Begin by warnings for upcoming events and tasks also appear in this view on the current date when the current date falls within the range of the begin by warning.

### Week

A graphical view of a week showing scheduled events and free periods. Hovering over a busy period brings up a tooltip with the details of the event.

<center>
![](images/week_view.png "week view")
</center>

Double clicking on a busy period opens the details dialog for the item. Double clicking on a free period opens a dialog to create a new event for that date and time.

This view conforms to the iso standard in which weeks begin on Monday and the first week in a year is the week that contains the first Thursday. This first week is assigned number 1 and the last week number in the year will then either be 52 or 53.  E.g., in 2015, week number 1 is December 29, 2014 --- January 4, 2015 and week number 53 is December 28, 2015 --- January 3, 2016.

If you have an entry for `calendars` in your `etm.cfg`, then busy times from your default calendars will appear in one color and busy times from your non-default calendars will appear in another color.

Need to tell someone when you are available during a given week? Select the week in this view, press Control-B to display the periods during the week when you are busy and then copy and paste these into an email.

<center>
![](images/busy_times.png "scheduled times")
</center>


### Month

A monthly calendar view with the date numbers colored to indicate the amount of scheduled time for events for that date.

<center>
![](images/month_view.png "month view")
</center>

Double clicking on a date, switches to the week view for that date and scrolls the day view to that date as well. Month view also conforms to the iso standard in which weeks begin on Monday.

### Now

Tasks requiring attention now. All *scheduled* (dated) tasks whose due dates have passed including delegated tasks and waiting tasks (tasks with unfinished prerequisites) grouped by available, delegated and waiting and, within each group, by the due date.

When there are tasks in this view, a red warning button appears in the lower, right-hand corner of the main display --- see, for example, the week and month view screen shots above. This button disappears when there are no tasks in this view.

### Next

All *unscheduled* (undated) tasks grouped by context (home, office, phone, computer, errands and so forth) and sorted by priority and extent. These tasks correspond to GTD's *next actions*. These are tasks which don't really have a deadline and can be completed whenever a convenient  opportunity arises.  Check this view, for example, before you leave to run errands for opportunities to clear other errands.

Items without contexts are automatically assigned the context "none".

"In basket" and "someday maybe" items are also displayed in this view.

### Folder

All items grouped by folder (project file path) and sorted by type and *relevant datetime*. Use this view to review the status of your projects.

The *relevant datetime* is the past due date for any past due tasks, the starting datetime for any non-repeating items and the datetime of the next instance for any repeating items.

### Keyword

All items grouped by keyword and sorted by type and *relevant datetime*.

Items without keywords are automatically assigned the keyword "none".

### Tag

All items with tag entries grouped by tag and sorted by type and *relevant datetime*. Note that items with multiple tags will be listed under each tag.
