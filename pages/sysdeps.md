# [System Dependencies](#)

## Short List

- [Vagrant](FIXME)

- [VirtualBox](http://virtualbox.org)

- [Debian Installer](FIXME)

- [Salt](http://github.com/saltstack/salt.git)

- [ACE](FIXME)

- [Pyramid](FIXME)

- [Cornice](FIXME)

- [wimlib](FIXME) - optional

- [ISC Bind](FIXME)

- [ISC DHCPD](FIXME)

- [tftp-hpa](FIXME)

- [Samba](http://samba.org)

- [Apache](http://apache.org)



First, there are the system dependencies.  This may not be the best term, but
these dependencies are the selection of implmentations of the various services
that paella needs to install and configure systems.  These are things like DNS,
DHCP, TFTP, HTTP, SMB, etc.  These are dependencies that used, rather than
used or called directly by the paella python code.  I have chosed
the [ISC](FIXME) implementations
of dns and dhcp, H. Peter Alvin's tftp server, the venerable Apache webserver,
as well as Samba for implenting stable and reliable services.  While some of
these services are much more difficult to configure an operate compared to
many of the alternatives I have seen chosen for similar environments, the
alternatives either do not provide the flexibility, or they don't appear to have
as many eyes on the code, as the selections that I have made.

Second, there are the libraries that have been chosen to work with the
paella application.  These can generally be divided into two classes, python
and javascript.  This is where the selection of dependencies becomes much
more difficult.

[Variations on a Theme](http://en.wikipedia.org/wiki/Variations_on_a_Theme)

[Fugue](http://en.wikipedia.org/wiki/Fugue)

I am hoping that the two links provided above come close to describing
the many alternatives that can be chosen to perform similar functions.  This
is very difficult, and many times I have been left with no choice but to gamble.

What is alive today can become dead and unmaintained quickly.  The effects
may not be felt until a long time after, but when this happens, something
has to be fixed.  What is stable, unchanged and predictable can also be
a sign of stagnation and a forecast for eventual removal from the
debian archive could be in the next release.  While it is impossible to
predict this and keep it from happening, a careful selection of dependencies
can drastically reduce the frequency of those types of problems occurring.

While some of the system services may be hard to work with and configure, the
selection of software libraries that paella directly executes has been chosen
to be as easy to work with as possible, without circumventing important things
that may potentially affect the predictability and reliabilty of the code.

Nevertheless, there should be at least one or two dependencies that will
have to be worked with in the next two years, if history and experience are
any guide, which is why the selection process is so important, and it has
taken much of my time.

## Trumpet Static Resources
 

# CSS Authoring

## Compass

This project uses [compass](http://compass-style.org) to create 
the [CSS](http://en.wikipedia.org/wiki/Cascading_Style_Sheets) resources 
that will be used by the web application.  I have chosen to 
use [Sassy CSS](http://sass-lang.com)
[docs](http://sass-lang.com/documentation/file.SASS_REFERENCE.html) 
as the syntax to author the css resources.  Being an extension of the 
syntax of CSS3, any valid css file can be used directly as a scss file,
developer to fully use the compass framework on css files that have 
already been designed for other sites.

### Plugins

This project uses the [bootstrap-sass](https://github.com/twbs/bootstrap-sass) 
plugin for compass, making it easier to customize pages that use the 
[bootstrap](http://getbootstrap.com/) framework.  Also, a helper for 
generating [jquery-ui](FIXME) themes,
[Compass UI](https://github.com/patrickward/compass-ui), is used in 
this probject.  At full size the bootstrap css file is 291K(120K,
compass compressed output), while the jqueryui css file is 77K(31k,
compass compressed output).  These sizes can be decreased by delving into
the scss provided by the plugins and only using what is needed for the
particular application.

This project provides an example of how both the 
bootstrap and jquery-ui plugins can be configured to use the same 
color themes, and there is a python script that generates the
scss files.  The example is imcomplete, but provides enough to 
direct the css developer on how to proceed.  A plugin for creating 
buttons, [Sassy Buttons](http://jaredhardy.com/sassy-buttons/), is also 
being used.

### CSS Framework

-  [Compass](http://compass-style.org/):  
   Compass is the tool I use to generate my CSS resources.

-  [Sassy Buttons](http://jaredhardy.com/sassy-buttons/): 
   This is a collection of mixins and defaults that help a developer make
   custom buttons very easily.

-  [Bootstrap for Sass](https://github.com/thomas-mcdonald/bootstrap-sass): 
   This wonderful package allows me to refrain from using the css that is 
   provided with bootstrap and quickly make a custom version that I can 
   integrate more closely with other objects on the page.  Having bootstrap 
   in this form allows me to adjust how bootstrap operates and allows me 
   to only choose the parts I need (Currently everything is included).
   
-  [FontAwesome](http://fontawesome.io/):
   Instead of just using the basic css, I have chosen to use the 
   fontawesome-sass distribution.  This provides scalable vector icons
   to websites.
   
-  [Compass UI](https://github.com/patrickward/compass-ui): 
   This compass plugin provides the ability to generate jQueryUI themes
   with a minimum of effort.  I have spent hours on the themeroller before
   trying to create a custom theme that would match the general colors that 
   I use on a web page.  With this plugin, all I have to do is set the 
   variables to correspond to the color variables that I use elsewhere on the 
   page and I instantly get themed widgets that don't look like they came 
   from another site.
   

### Icons
Finally, [FontAwesome](http://fontawesome.io/), is 
being used to provide icons.  The scss files are 
copied from the
[git repository](https://github.com/FortAwesome/Font-Awesome/tree/master/scss),
and may need to be updated.  In the future, I'd like to use
[font-awesome-sass](https://github.com/FortAwesome/font-awesome-sass) to
do this.  In the past, I had trouble integrating this into compass,
but it's possible that this problem has disappeared.  If it hasn't
disappeared, [bower](http://bower.io) can still be used to track the
upstream source and use a script to install the scss files into the
sass/partials directory.

### FullCalendar

The css file for [FullCalendar](http://arshaw.com/fullcalendar/),
has been copied verbatim and renamed to an scss file.  This was 
done to exemplify how easy it is to directly import css into 
the project.

## Goals for Authoring Environment

The primary goal for using compass and scss syntax is to provide 
a person who designs webpages the tools to design in a manner they 
are most likely to be comfortable with.  Stylesheets that they have 
developed in other projects can be directly imported, then manipulated 
very easily.

The author of this project is a web page designer, but merely a 
web service/application designer.  The example scss may not be 
the most pleasing to the eye, and there are many styles variables 
that have not been modified to match the other colors, and there 
is some work to be done to make the example themes more coherent 
and pleasant.


### Basic Javascript Libraries

-  [CoffeeScript](http://coffeescript.org/):
   The app is written with coffee script.
  
-  [Requirejs](http://requirejs.org):
   This library is required to load the other modules.
   
-  [jQuery](http://jquery.com/): 
   jQuery is a very good for selecting and maninpulating elements in the DOM.

-  [jQuery User Interface](http://jqueryui.com/): 
   jQueryUI is used for the fullcalendar widget, as well as for dialog boxes 
   and other user interface elements that aren't used through boostrap.  The 
   corresponding styles are maintained with compass.

-  [Bootstrap v3](http://getbootstrap.com/): 
   Bootstrap is a CSS/Javascript framework used to help make responsive 
   websites.  Bootstrap was selected to be used in order to serve to 
   mobile devices.  The CSS is handled through compass with bootstrap-sass.
   
-  [LoDash](FIXME): 
   I decided to use lodash instead of underscore.  Quite a few of the
   utilities provided by this library are easily handled with coffee script,
   however, backbone and marionette depend on this library.

-  [Backbone.js](http://backbonejs.org/): 
   Backbone is an excellent library that provides an api to make very 
   rich views tied to models that are seamlessly synchronized with 
   the server via a REST interface.

-  [Marionette](http://marionettejs.com/):
   "Backbone.Marionette is a composite application library for 
   Backbone.js that aims to simplify the construction of large scale 
   JavaScript applications," and it is very effective at doing this.
   This is the primary library used in this project for creating 
   single page applications.

-  [Ace Editor](http://ace.c9.io/#nav=about): 
   The ACE editor is a good text editor that is very useful for 
   editing html, css, java/coffee scripts, and other formats that
   aren't being used yet.
   
-  [Teacup](http://goodeggs.github.io/teacup/):
   I really like teacup.  This selection is a result of a
   very intensive search and test pattern that looked at
   many different javascript html templating solutions and
   teacup really stood out.
   
-  [FullCalendar](http://arshaw.com/fullcalendar/): 
   FullCalendar is a very good library that provides an interactive 
   calendar where events can be retrieved dynamically and grouped, 
   colored, or otherwised styled in many ways.  The calendar provides 
   monthly, weekly, and daily view models to interact with.
   **FullCalendar hasn't been used in paella**

-  [jQuery User Interface](http://jqueryui.com/): 
   jQueryUI is used for the fullcalendar widget, as well as for dialog boxes 
   and other user interface elements that aren't used through boostrap.  The 
   corresponding styles are maintained with compass.
   **JQueryUI hasn't been used in paella**

