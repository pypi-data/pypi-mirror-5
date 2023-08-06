% Data

*etm* data entries (events, tasks, and so forth) are kept in text files with the extension `.txt` in the directory `datadir` specified in your `etm.cfg` file. Items begin with a type character such as `*` (event) and continue on one or more lines either until the end of the file is reached or another line is found that begins with a type character. The beginning type character for each item is followed by the item summary and then, perhaps, by one or more `@key value` pairs.

The discussion of possible entry types below is followed by a discussion of the possible `@key value` pairs.

## Entry types

### ~ Action

A record of the time-consuming action required to complete a task or participate in an event. Actions are not reminders, they are instead records of how time was actually spent. Action lines begin with a tilde, `~`.

        ~ work on sales presentation @s mon 3p @e 1h15m

Entries such as `@s mon 3p` and `@e 1h15m` are discussed below under *Item details*.

### * Event

Something that will happen on particular day(s) and time(s).  Event lines begin with an asterick, `*`.

        * dinner with Karen and Al @s sat 7p @e 3h

Events have a starting datetime, `@s` and an extent, `@e`. The ending datetime is given implicitly as the sum of the starting datetime and the extent. Events that span more than one day are possible, e.g.,

        * Sales meeting @s 9a wed @e 2d8h

begins at 9am on Wednesday and ends at 5pm on Friday.

An event without an `@e` entry or with `@e 0` is regarded as a *reminder* and, since there is no extent, will not be displayed in the *week view*. Additionally, if the reminder is repeated and the repetition uses either `&h` (byhour) or `&n` (byminute) so that the reminder repeats more than once on the days it occurs, then only one instance of the reminder will be displayed in *day view* on each day that it occurs.

### ^ Occasion

Holidays, anniversaries, birthdays and the like. Like an event with a date but no starting time and no extent. Occasions begin with a caret sign, `^`.

        ^ The !1776! Independence Day @s 2010-07-04 @r y &M 7 &m 4

On July 4, 2013, this would appear as `The 237th Independence Day`.

### ! Note

A record of some useful information. Note lines begin with an exclamation point, `!`.

    ! xyz software @d user: dnlg, pw: abd123gef

### - Task

Something that needs to be done. It may or may not have a due date. Task lines begin with a minus sign, `-`.

    - pay bills @s Oct 25

A task with an `@s` entry becomes due on that date and past due when that date has passed.

### % Delegated task

A task that is assigned to someone else, usually the person(s) designated in an `@u` entry. Delegated tasks begin with a percent sign, `%`.

        % make reservations for trip @u joe @s fri

### + Task group

A collection of related tasks, some of which may be prerequities for others. Task groups begin with a plus sign, `+`.

        + dog house
          @j pickup lumber and paint      &q 1
          @j cut pieces                   &q 2
          @j assemble                     &q 3
          @j paint                        &q 4

Note that a task group is a single item and is treated as such. E.g., if any job is selected for editing then the entire group is displayed.

Individual jobs are given by the `@j` entries. The *queue* entries, `&q`, set the order --- tasks with smaller &q values are prerequisites for subsequent tasks with larger &q values. In the example above, neither "pickup lumber" nor "pickup paint" have any prerequisites. "Pickup lumber", however, is a prerequisite for "cut pieces" which, in turn, is a prerequisite for "assemble". Both "assemble" and "pickup paint" are prerequisites for "paint".

The way a task group is displayed is illustrated below. Note that jobs are numbered and that jobs with unfinished prerequisites are labeled with a different icon.
<center>
![](images/doghouse1.png "no finished jobs")
</center>

When a job is completed, its icon is changed and it is displayed on the date the job was completed. Note that completing "pickup lumber" makes "cut pieces" available for completion.
<center>
![](images/doghouse2.png "one finished job")
</center>

### $ In basket

A quick, don't worry about the details item to be edited later when you have the time. In basket entries begin with a dollar sign, `$`.

        $ joe 919 123-4567

If you create an item using *etm* and forget to provide a type character, an `$` will automatically be inserted.


### ? Someday maybe

Something are you don't want to forget about altogether but don't want to appear on your next or scheduled lists. Someday maybe items begin with a question mark, `?`.

        ? lose weight and exercise more

### # Hidden

Hidden items begin with a hash mark, `#`. Such items are ignored by etm save for appearing in the folder view.  Stick a hash mark in front of any item that you don't want to delete but don't want to see in your other views.

### = Defaults

Default entries begin with an equal sign, `=`. These entries consist of `@key value` pairs which then become the defaults for subsequent entries in the same file until another `=` entry is reached.

Suppose, for example, that a particular file contains items relating to "project_a" for "client_1". Then entering

    = @k client_1:project_a

on the first line of the file and

    =

on the twentieth line of the file would set the default keyword for entries between the first and twentieth line in the file.


## Dates

### Fuzzy dates and time periods

When either a *datetime* or an *time period* is to be entered, special formats are used in *etm*. Examples include entering a starting datetime for an item using `@s`, jumping to a date using Ctrl-J and calculating a date using F5.

Suppose, for example, that it is currently 8:30am on Friday, February 15, 2013. Then, *fuzzy dates* would expand into the values illustrated below.

- `mon 2p` or `mon 14h`: 2:00pm Monday, February 19
- `fri`: 12:00am Friday, February 15
- `9a -1/1` or `9h -1/1`: 9:00am Tuesday, January 1
- `+2/15`: 12:00am Monday, April 15 2013
- `8p +7` or `8h +7`: 8:00pm Friday, February 22
- `-14`: 12:00am Friday, February 1
- `now`: 8:30am Friday, February 15

To avoid ambiguity, always append either 'a', 'p' or 'h' when entering an hourly time such as `1p` or `13h`.

Time periods are entered using the format `DdHhMm` where D, H and M are integers and d, h and m refer to days, hours and minutes respectively. For example:

- `2h30m`: 2 hours, 30 minutes
- `7d`: 7 days
- `45m`: 45 minutes

As an example, if it is currently 8:50am on Friday February 15, 2013, then entering `now + 2d4h30m` into the date calculator would give `2013-02-17 1:20pm`. If, at the same time, an item were saved on a system in the `US/Eastern` time zone which contained the entry `@s now @z Australia/Sydney` then the expanded value would be `@s 2013-02-16 12:50am`, which is "now" in Sydney.

Dates and times are always stored in *etm* data files as times in the time zone given by the entry for `@z`. On the other hand, dates and times are always displayed in *etm* using the local time zone of the system. In the previous illustration, for example, the data file would contain `@s 2013-02-16 12:50am @z Australia/Sydney` but this item would be displayed as starting at `2013-02-15 8:50am` on a system in the `US/Eastern` time zone.

### Anniversary substitutions

An anniversary substitution is an expression of the form `!YYYY!` that appears in an item summary. Consider, for example, the occassion

    ^ !2010! anniversary @s 2011-02-20 @r y

This would appear on Feb 20 of 2011, 2012, 2013 and 2014, respectively, as *1st anniversary*, *2nd anniversary*, *3rd anniversary* and *4th anniversary*.The suffixes, *st*, *nd* and so forth, depend upon the translation file for the locale.

## @key-value pairs

### @a alert

The specification of the alert(s) to use with the item. One or more alerts can be specified in an item. E.g.,

    @a 10m, 5m
    @a 1h: s

would trigger the alert(s) specified by `default_alert` in your `etm.cfg` at 10 and 5 minutes before the starting time and a (s)ound alert one hour before the starting time.

The alert

    @a 2d: e; who@what.com, where2@when.org; filepath1, filepath2

would send an email to the two listed recipients exactly 2 days (48 hours) before the starting time of the item with the item summary as the subject, with file1 and file2 as attachments and with the body of the message composed using `email_template` from your `etm.cfg`.

Similarly, the alert

    @a 10m: t; 9191234567@vtext.com, 9197654321@txt.att.net

would send a text message 10 minutes before the starting time of the item to the two mobile phones listed (using 10 digit area code and carrier mms extension) together with the settings for `sms` in `etm.cfg`. If no numbers are given, the number and mms extension specified in `sms.phone` will be used. Here are the mms extensions for the major US carriers:

    Alltel          @message.alltel.com
    AT&T            @txt.att.net
    Nextel          @messaging.nextel.com
    Sprint          @messaging.sprintpcs.com
    SunCom          @tms.suncom.com
    T-mobile        @tmomail.net
    VoiceStream     @voicestream.net
    Verizon         @vtext.com

Finally,

    @a 0: p; program_path

would execute `program_path` at the starting time of the item.

The format for each of these:

    @a <trigger times> [: action [; arguments]]

In addition to the default action used when the optional `: action` is not given, there are the following possible values for `action`:

- `d` Execute `alert_displaycmd` in `etm.cfg`.
- `e; recipients[;attachments]` Send an email to `recipients` (a comma separated list of email addresses) optionally attaching `attachments` (a comma separated list of file paths). The item summary is used as the subject of the email and the expanded value of `email_template` from `etm.cfg` as the body.
- `m` Display an internal etm message box using `alert_template`.
- `p; process` Execute the command given by `process`.
- `s` Execute `alert_soundcmd` in `etm.cfg`.
- `t [; phonenumbers]` Send text messages to `phonenumbers` (a comma separated list of 10 digit phone numbers with the sms extension of the carrier appended) with the expanded value of `sms.message` as the text message.
- `v` Execute `alert_voicecmd` in `etm.cfg`.

Note: either `e` or `p` can be combined with other actions in a single alert but not with one another.

### @b beginby

An integer number of days before the starting date time at which to begin displaying *begin by* notices. When notices are displayed they will be sorted by the item's starting datetime and then by the item's priority, if any.

### @c context

Intended primarily for tasks to indicate the context in which the task can be completed. Common contexts include home, office, phone, computer and errands. The "next view" supports this usage by showing undated tasks, grouped by context. If you're about to run errands, for example, you can open the "next view", look under "errands" and be sure that you will have no "wish I had remembered" regrets.

### @d description

An elaboration of the details of the item to complement the summary.

### @e extent

A time period string such as `1d2h` (1 day 2 hours). For an action, this would be the elapsed time. For a task, this could be an estimate of the time required for completion. For an event, this would be the duration. The ending time of the event would be this much later than the starting datetime.

### @f done; due

Datetimes; tasks, delegated tasks and task groups only. When a task is completed an `@f done; due` entry is added to the task. Similarly, when a job from a task group is completed in etm,  an `&f done; due` entry is appended to the job and it is removed from the list of prerequisites for the other jobs. In both cases `done` is the completion datetime and `due` is the datetime that the task or job was due. The completed task or job is shown as finished on the completion date. When the last job in a task group is finished an `@f done; due` entry is added to the task group itself reflecting the datetime that the last job was done and, if the task group is repeating, the `&f` entries are removed from the individual jobs.

Another step is taken for repeating task groups. When the first job in a task group is completed, the `@s` entry is updated using the setting for `@o` (above) to show the next datetime the task group is due and the `@f` entry is removed from the task group.  This means when some, but not all of the jobs for the current repetition have been completed, only these job completions will be displayed. Otherwise, when none of the jobs for the current repetition have been completed, then only that last completion of the task group itself will be displayed.

Consider, for example, the following repeating task group which repeats monthly on the last weekday on or before the 25th.

    + pay bills @s 11/23 @f 10/24;10/25
      @r m &w MO,TU,WE,TH,FR &m 23,24,25 &s -1
      @j organize bills &q 1
      @j pay on-line bills &q 3
      @j get stamps, envelopes, checkbook &q 1
      @j write checks &q 2
      @j mail checks &q 3

Here "organize bills" and "get stamps, envelopes, checkbook" have no prerequisites. "Organize bills", however, is a prerequisite for "pay on-line bills" and both "organize bills" and "get stamps, envelops, checkbook" are prerequisites for "write checks" which, in turn, is a prerequisite for "mail checks".

The repetition that was due on 10/25 was completed on 10/24. The next repetition was due on 11/23 and, since none of the jobs for this repetition have been completed, the completion of the group on 10/24 and the list of jobs due on 11/23 will be displayed initially. The following sequence of screen shots show the effect of completing the jobs for the 11/23 repetition one by one on 11/27.

<center>
![](images/paybills1.png "Completion 1")
![](images/paybills2.png "Completion 2")
</center>

<center>
![](images/paybills3.png "Completion 1")
![](images/paybills4.png "Completion 2")
</center>

<center>
![](images/paybills5.png "Completion 1")
![](images/paybills6.png "Completion 2")
</center>



### @g goto

The path to a file or a URL to be opened using the system default application when the user presses *Control-G* in the GUI.

### @j job

Component tasks or jobs within a task group are given by `@j job` entries. `@key value` entries prior to the first `@j` become the defaults for the jobs that follow. `&key value` entries given in jobs use `&` rather than `@` and apply only to the specific job.

Many key-value pairs can be given either in the group task using `@` or in the component jobs using `&`:

- `@c` or `&c`: context
- `@d` or `&d`: description
- `@e` or `&e`: extent
- `@f` or `&f`: done; due (datetimes)
- `@k` or `&k`: keyword
- `@l` or `&l`: location

The key-value pair `&q` (queue position) can *only* be given in component jobs where it is required.  Key-values other than `&q` and those listed above, can *only* be given in the initial group task entry and their values are inherited by the component jobs.

### @k keyword

A heirarchical classifier for the item. Intended for actions to support time billing where a common format would be `client:job:category`. *etm* treats such a keyword as a heirarchy so that an action report grouped by month and then keyword might appear as follows

        27.5h) Client 1 (3)
            4.9h) Project A (1)
            15h) Project B (1)
            7.6h) Project C (1)
        24.2h) Client 2 (3)
            3.1h) Project D (1)
            21.1h) Project E (2)
                5.1h) Category a (1)
                16h) Category b (1)
        4.2h) Client 3 (1)
        8.7h) Client 4 (2)
            2.1h) Project F (1)
            6.6h) Project G (1)

An arbitrary number of heirarchical levels in keywords is supported.

### @l location

The location at which, for example, an event will take place.

### @m memo

Further information about the item not included in the summary or the description. Since the summary is used as the subject of an email alert and the descripton is commonly included in the body of an email alert, this field could be used for information not to be included in the email.

### @o overdue

Repeating tasks only. One of the following choices: k) keep, r) restart, or s) skip. Details below.

### @p priority

Either 0 (no priority) or an intger between 1 (highest priority) and 9 (lowest priority). Primarily used with undated tasks.

### @r repetition rule

The specification of how an item is to repeat. Repeating items **must** have an `@s` entry as well as one or more `@r` entries. Generated datetimes are those satisfying any of the `@r` entries and falling **on or after** the datetime given in `@s`.

A repetition rule begins with

    @r frequency

where `frequency` is one of the following characters:

- `y`: yearly
- `m`: monthly
- `m`: weekly
- `d`: daily
- `l`: list (a list of datetimes will be provided using `@+`)

The `@r frequency` entry can, optionally, be followed by one or more `&key value` pairs:

- `&i`: interval (positive integer, default = 1) E.g, with frequency `w`, interval 3 would repeat every three weeks.
- `&t`: total (positive integer) Include no more than this total number of repetitions.
- `&s`: bysetpos (integer) See the payday example below for an illustration of bysetpos.
- `&u`: until  (datetime) Only include repetitions falling *before* (not including) this datetime.
- `&M`: bymonth (1, 2, ..., 12)
- `&m`: bymonthday (1, 2, ..., 31) Use, e.g., -1 for the last day of the month.
- `&W`: byweekno (1, 2, ..., 53)
- `&w`: byweekday (*English* weekday abbreviation SU ... SA). Use, e.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the month.
- `&h`: byhour (0 ... 23)
- `&n`: byminute (0 ... 59)

Repetition examples:

- 1st and 3rd Wednesdays of each month.

        ^ 1st and 3rd Wednesdays
          @r m &w 1WE, 3WE

- Payday (an occasion) on the last week day of each month. (The `&s -1` entry extracts the last date which is both a weekday and falls within the last three days of the month.)

        ^ payday @s 2010-07-01
          @r m &w MO, TU, WE, TH, FR &m -1, -2, -3 &s -1

- Take a prescribed medication daily (an event) from the 23rd through the 27th of the current month at 10am, 2pm, 6pm and 10pm and trigger an alert zero minutes before each event.

        * take Rx @d 10a 23  @r d &u 11p 27 &h 10, 14 18, 22 @a 0

- Vote for president (an occasion) every four years on the first Tuesday after a Monday in November. (The `&m range(2,9)` requires the month day to fall within 2 ... 8 and thus, combined with `&w TU` to be the first Tuesday following a Monday.)

        ^ Vote for president @s 2012-11-06
          @r y &i 4 &M 11 &m range(2,9) &w TU

Optionally, `@+` and `@-` entries can be given.

- `@+`: include (comma separated list to datetimes to be *added* to those generated by the `@r` entries)
- `@-`: exclude (comma separated list to datetimes to be *removed* from those generated by the `@r` entries)

A repeating *task* may optionally also include an `@o <k|s|r>` entry (default = k):

- `@o k`: Keep the current due date if it becomes overdue and use the next due date from the recurrence rule if it is finished early. This would be appropriate, for example, for the task 'file tax return'. The return due April 15, 2009 must still be filed even if it is overdue and the 2010 return won't be due until April 15, 2010 even if the 2009 return is finished early.

- `@o s`: Skip overdue due dates and set the due date for the next repetition to the first due date from the recurrence rule on or after the current date. This would be appropriate, for example, for the task 'put out the trash' since there is no point in putting it out on Tuesday if it's picked up on Mondays. You might just as well wait until the next Monday to put it out. There's also no point in being reminded until the next Monday.

- `@o r`: Restart the repetitions based on the last completion date. Suppose you want to mow the grass once every ten days and that when you mowed yesterday, you were already nine days past due. Then you want the next due date to be ten days from yesterday and not today. Similarly, if you were one day early when you mowed yesterday, then you would want the next due date to be ten days from yesterday and not ten days from today.



### @s starting datetime

When an action is started, an event begins or a task is due.

### @t tags

A tag or list of tags for the item.

### @u user

Intended to specify the person to whom a delegated task is assigned. Could also be used in actions to indicate the person performing the action.

### @v value

A key from `values` in your `etm.cfg`. Used in actions to apply a billing rate to time spent in an action. E.g., with

        values:
            br1: 45.0
            br2: 60.0

then entries of `@v br1` and `@e 2h30m` in an action would entail a value of `45.0 * 2.5 = 112.50`.

### @z time zone

The time zone of the item, e.g., US/Eastern. The starting and other datetimes in the item will be interpreted as belonging to this time zone.

### @+ include

A datetime or list of datetimes to be added to the repetitions generated by the `@r rrule` entry. If only a date is provided, 12:00am is assumed.

### @- exclude

A datetime or list of datetimes to be removed from the repetitions generated by the `@r rrule` entry. If only a date is provided, 12:00am is assumed.

Note that to exclude a datetime from the recurrence rule, the @- datetime *must exactly match both the date and time* generated by the recurrence rule.

## File paths

*etm* offers two heirarchical ways of organizing your data: by file path and by keyword. There are no hard and fast rules about how to use these heirarchies but the goal is a system that makes complementary uses of file path and keyword and fits your needs. As with any filing system, planning and consistency are paramount.

For example, one pattern of use for a business would be to use file path for people and keyword for client-project-category.

Similarly, a family could use file path to separate personal and shared items for family members, for example:

    root etm data directory
        dag
        erp
        shared
            holidays
            birthdays
            events

Here

    ~dag/.etm/etm.cfg
    ~erp/.etm/etm.cfg

would both contain `datadir` entries specifying the common root data directory. Additionally, if these configuration files contained, respectively, the entries

    calendars
    - [dag, true, dag]
    - [erp, false, erp]
    - [shared, true, shared]

and

    calendars
    - [erp, true, erp]
    - [dag, false, dag]
    - [shared, true, shared]

then, by default, both dag and erp would see the entries from their personal files as well as the shared entries and each could optionally view the entries from the other's personal files as well.  See the *Preferences* tab for details on the `calendars` entry.