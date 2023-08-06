% Overview

*etm* is an acronym for event and task manager. It provides a format for using plain text files to store actions, events, notes, and tasks and a PyQt based GUI for creating and modifying items as well as viewing them. Available data types are discussed in the *Data* tab. Possible views include *Day*, *Week*, *Month*, *Now*, *Next*, *Folder*, *Keyword* and *Tag*.  These are discussed in the *Views* tab. Custom, report views that can be exported and printed are discussed in the *Reports* tab. There are keyboard shortcuts for all actions which are discussed in the *Shortcuts* tab. Possible user preference settings are discussed in the *Preferences* tab.

The main window is illustrated below with the *Day* view selected.

<center>
![](images/mainview.png "main view")
</center>

<!-- <center>
<img src="file:///Users/dag/etm-qt/etmQt/help/images/mainview.png" alt="" title="main view" style="max-width: 500px; height: auto; " />
</center>
 -->

Use Control-J to jump to a fuzzy parsed date, e.g., "-1/1" to go the first day of the previous month or "+90" to go to the date that is 90 days from today. The *Day*, *Week* and *Month* views will all change to show the selected date.

### GTD with etm

*etm's* main goal is to make *Getting Things Done* easier. Commonly abbreviated as *GTD*, *Getting Things Done* is an action management method, and the title of a  popular book by [David Allen][]. It rests on the common sense notion that with a complete and current inventory of all commitments, organized and reviewed in a systematic way, the mind is freed from the job of remembering everything that needs to be done, and can focus on actually performing those tasks.

[David Allen]: http://www.davidco.com/

Three observations are critical:

1. Projects usually involve a series of steps, some of which must be carried out consecutively, e.g., parts must be acquired before assembly can begin.

2. The steps of a project are carried out in a context which may vary from step to step, e.g., parts may be acquired in the context 'errands' but assembly may be in the context 'workshop'.

3. While focusing on projects is great for planning, for actually doing things it would be more convenient to focus on context so that, for example, you could see all actions from all projects with context 'errands' before you drive off. To focus on what needs to be done, it would also be useful to be able to deemphasize actions that are not yet *available* so that, for example, 'assemble parts' is not prominently displayed until 'acquire parts' is complete.

*GTD* thus requires convenient methods for:

planning
:   storing and organizing all the bits.

acting
:   displaying just the information you need, when you need it.

reviewing
:   checking the status of all items your projects.

etm allows you to store and organize your commitments using a simple,
intuitive format using plain text files. Here, for example, is a simple task

    - pay bills @s Oct 25

and here is a task group in which the individual jobs must be finished in `@q` (queue) order, i.e., assemble is a prerequisite for paint.

    + dog house
      @j pickup lumber and paint      &q 1
      @j cut pieces                   &q 2
      @j assemble                     &q 3
      @j paint                        &q 4

Day view shows your commitments grouped and sorted by date. Now view shows your past due tasks grouped into available, waiting and delegated categories and sorted by due date. Next view shows your undated tasks grouped by context and sorted by priority and estimated completion time. Folder view provides project review in a glance by showing your commitments grouped by project file (folder) and displaying the *relevant* datetimes, i.e., the past due date for past due tasks, the starting datetime for non-repeating items and the datetime of the next instance for any repeating items. Keyword view provides another heirarchial view of your commitments again displaying relevant datetimes but grouped by keyword rather than folder. Tag view shows your commitments grouped by tag. Within each of these views, a filter can be used to limit the display to items matching a case-insensitive, regular expression.

In addition to these built-in views, report view gives you complete freedom to group, sort and filter your data in any way you wish.

In short, etm makes it easy for you to store and organize all the bits and to display just the information you need, when you need it.


### Starting etm

etm can be started using the command `etm_qt.py [arguments]` in a terminal window. With no arguments, etm will use settings from the configuration file `~/.etm/etm.cfg` and open the GUI.

If the first argument is the path to a directory which contains a file named `etm.cfg`, then settings from that file will be used instead.

If the first argument, other than the optional path, is either "a", "c", "m", "s", "?" or "l" (lower case L), then the remaining arguments will be executed by etm without opening the GUI.

- a: display an action report using the remaining arguments as the report specification.
- c: display a custom report using the remaining arguments as the report specification.
- m: display a report using the remaining argument, which must be a positive integer, to display a report using the corresponding entry from the file given by `report_specifications` in `etm.cfg`. Use `? m` or `m ?` to display the numbered list of entries from this file.
- s: display the next few days from the day view combined with any items in the now and next views.
- ?: display command line help information or, if followed by a, c, m or s, then display help information about the specified command.
- l: begin an interactive shell loop in which the above commands are available and can be adjusted and run again without reloading the data files.

See the report help tab for details about creating reports and the preferences help tab for details about the possible settings for `etm.cfg`.

### New items

Details about item types and options are available in the *Data* tab.

- To create a new item, either click on the new item button or press Control-N. This will open an edit window for your entry. When done, click on the Save Icon or press Control-S to save your entry and choose a file from the dialog.

- Need to schedule an event? Use the week view to find a free period and then double click on the desired date and time. The editor will open with the date and time you selected already entered.

- To create a new action, either click on the new action button or press Control-T to create a new action timer.

    <center>
    ![](images/action_start.png "action timer start")
    </center>

    Enter a summary of your new action and press Return to start the timer. The display will change to show timer control buttons and elapsed time:

    <center>
    ![](images/action_running.png "action timer running")
    </center>

    When you are finished, either click on the stop timer button or press Shift + Control-T to stop the timer and open an edit window to record the action. Your summary, the date and time you began the action and the elapsed time will automatically be entered:

    <center>
    ![](images/action_finish.png "action timer finish")
    </center>


- Want to work on a task and record the time you spend? Select the task and then click on "create a new action timer based on this item" to start a timer with all the relevant details of the task already entered.

- Need to quickly enter some information before you forget? Press Control-S to open the scratch pad. Type whatever you want to remember. You can either leave the scratch pad open or press Control-Return to close it. When you next open the scratch pad, even if you have closed and restarted etm, your previous entry will be there for you to copy or edit. Additionally, when you are editing a item or an action, you can press Control-I to insert the contents of the scratch pad at the cursor.


### Details

To examine the details of an item, either select it and press *Return* or double click on it. The details of the selected item will be displayed along with a number of possible actions related to the item:

<center>
![](images/detailsview.png "details view")
</center>

With repeating items, choosing either edit or delete entails a further choice of what to change/delete:

Only the datetime of this instance
:   This option only applies to edit. Use it, for example, when you have a repeating event and you want to change the day or time for this instance only. This is a shortcut in which you simply enter the new fuzzy parsed datetime and the change is made without opening the editor.
This instance
:   Use this, for example, if you want to change the summary or add something to the description of this instance of the item or you want to delete this single instance.
This and all subsequent instances
:   Use this, for example, if a repeating event is changing to a new week day or time or a repeating event is ending and you want to remove all the future repetitions.
All instances
:   Use this, for example, to change the summary and have the change apply to all repetitions of the item.

### Filtering

You can enter an expression, either a plain string or a regular expression, in the pattern filter to limit the display in any of the tree (outline) views to items whose summaries (titles) or branches match the pattern. As each character is entered the display is updated to show only items that still match. Note the effect of changing the pattern from "v" to "vo" in the day view below:

<center>
![](images/pattern_filter1.png "v entered in pattern filter")
![](images/pattern_filter2.png "vo entered in pattern filter")
</center>

You can identify items with a particular tag by switching to the tag view and then entering a pattern for the tag(s) you want in the pattern filter. Only items from the matching tag branches will be displayed. This approach also works for filtering items in the keyword or folder view, the latter illustrated below. Note that the effect of entering "us" in the pattern filter is to expand the matching branches and summaries:

<center>
![](images/folder_view1.png "folder view")
![](images/folder_view2.png "folder view with pattern filter")
</center>

Press *Escape* to clear the filter and activate the *Select view* menu.

### Editing

The *etm* editor supports both syntax highlighting for etm data files and automatic completion. As illustrated below, different colors are provided for different item types and both `@key` and `&key` entries are highlighted. Entries using unsupported keys, such as `@h` below, are also highlighted as errors.

<center>
![](images/highlighting.png "Editor highlighting")
</center>

Automatic completion uses a list of possible completions in a text file specified by `auto_completions` in your `etm.cfg`. Each line in this file provides a possible completion, for example:

    @c computer
    @c home
    @c errands
    @c office
    @c phone
    @z US/Eastern
    @z US/Central
    @z US/Mountain
    @z US/Pacific
    dnlgrhm@gmail.com

As soon as you enter "@c", for example, a list of possible *context* completions will pop up and then, as you type further characters, the list will shrink to show only those that still match:

<center>
![](images/completion.png "Completion")
</center>

Up and down arrow keys change the selection and either *Tab* or *Return* inserts the selection.

### Working with other applications

Pressing *Ctrl-S* in the etm main window will open a schedule dialog showing items from your day view for the next few days plus items, if any, from your *now* and *next* views. This schedule can be printed or sent by email to an address you specify. Using settings for *agenda* in your *etm.cfg* the display can be customized to, for example, fit nicely in the display of your mobile phone:

<center>
![](images/agenda.png "etm schedule")
</center>

If you set `current_htmlfile` and/or `current_textfile` in your *etm.cfg* then etm will automatically update the contents of the relevant files with with your current schedule. You could then, for example, use the text file with *geektool* to display your current schedule on your desktop. Another option would be to place `current_textfile` in your Google Drive or Dropbox and thus have automatic access to your current schedule in your mobile device. Here's mine on my iPhone:

<center>
![](images/current.png "current_textfile on iPhone")
</center>


Both the schedule and report dialogs support exporting displayed items in CSV (comma separated values) format to a file you specify. Files in this format can be imported by most spreadsheet programs.

Provided that the python module *vobject* is installed on your system, pressing *F8* will export scheduled (dated) items in vcalendar format to `~/.etm/etm.ics`. If *calendars* is set in your *etm.cfg*, then only items from selected calendars will be exported, otherwise all items will be exported. This file can be imported by most calendar applications. Note that although tasks are exported as *VTODO* elements and notes as *VJOURNAL* elements, these elements will be ignored by most calendar applications.


### Version numbers

*etm*'s version numbering now uses the `major.minor.patch` format where each of the three components is an integer:

- Major version numbers change whenever there is a large or potentially backward-incompatible change.

- Minor version numbers change when a new, minor feature or a set of smaller features is introduced or when a status change has occured. A change in the minor version from zero to one, for example, indicates a change in the status of the major version from alpha to beta. Minor version numbers greater than one indicate production/stable status.

- Patch numbers change for new builds involving small bugfixes or the like. Some new builds may not be released.

When the major version number is incremented, both the minor version number and patch number will be reset to zero. Similarly, when the minor version number is incremented, the patch number will be reset to zero. All increments are by one.

<!-- ### License information

Copyright (c) 2009-2013 Daniel Graham, [daniel.graham@duke.edu][]. All rights
reserved.

[daniel.graham@duke.edu]: mailto:daniel.graham@duke.edu

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version. See [GNU License Information][] for details.

[GNU License Information]: http://www.gnu.org/licenses/gpl.html "GNU License Information"

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
 -->
