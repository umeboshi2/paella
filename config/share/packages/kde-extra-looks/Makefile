# URLs
# ksplash
# DebianEvolution
# http://www.kde-look.org/content/download.php?content=6385&id=1&tan=17583681
# DebianMoment
# http://www.kde-look.org/content/download.php?content=12558&id=1&tan=57573139
# FreeBSD_KDE
# http://www.kde-look.org/content/download.php?content=12323&id=1&tan=81020069
# Squirrel
# http://www.kde-look.org/content/download.php?content=10938&id=1&tan=31105419
# GNU_CooL
# http://www.kde-look.org/content/download.php?content=13192&id=1&tan=121375
#
# wallpapers
# http://www.kde-look.org/content/show.php/Brown+Bird?content=103664
# http://www.kde-look.org/content/show.php/Curly+Dock+1?content=103662
# http://www.kde-look.org/content/show.php/Curly+Dock+2?content=103663
# http://www.kde-look.org/content/show.php/English+Peas?content=103656
# http://www.kde-look.org/content/show.php/Fish+Splash?content=78924
# http://www.kde-look.org/content/show.php/Green+View+1?content=103654
# http://www.kde-look.org/content/show.php/Green+View+2?content=103655
# http://www.kde-look.org/content/show.php/honeysuckle?content=103648
# http://www.kde-look.org/content/show.php/Ladybug+on+Pecan+Flowers?content=103661
# http://www.kde-look.org/content/show.php/Little+White+Bell+Flowers?content=103666
# http://www.kde-look.org/content/show.php/Not+a+Dandeliion?content=103659
# http://www.kde-look.org/content/show.php/Poplar+Flowers?content=103667
# http://www.kde-look.org/content/show.php/Shiny+Leaves?content=103665
# http://www.kde-look.org/content/show.php/Thistle+1?content=103652
# http://www.kde-look.org/content/show.php/Thistle+2?content=103653
# http://www.kde-look.org/content/show.php/Yellow+Clover?content=78928
# http://www.kde-look.org/content/show.php/Yellow+Flower+with+Little+Bee?content=103658
# http://www.kde-look.org/content/show.php/Young+Rose?content=103668



# THE MINIMUM THAT'S REQUIRED IS LISTED HERE
# DebianMoment
# http://www.kde-look.org/content/download.php?content=12558&id=1&tan=57573139
# http://www.kde-look.org/content/show.php/honeysuckle?content=103648
# http://www.kde-look.org/content/show.php/English+Peas?content=103656

DEFAULT_BACKGROUND=desktop-background

INSTALL=install -m 0644 
COLORSCHEMES=$(wildcard color-schemes/*.kcsrc)
WALLPAPERS=$(wildcard wallpaper/*.jpg wallpaper/*.png)
APPDIR=usr/share/apps

#SPLASHES=DebianEvolution DebianMoment FreeBSD_KDE Squirrel GNU_CooL 
SPLASHES=DebianMoment
COLORSCHEMES=$(wildcard color-schemes/*.kcsrc)
COLORSCHEMES_DIR=$(APPDIR)/kdisplay/color-schemes
WALLPAPERS=$(wildcard wallpaper/*.jpg wallpaper/*.png)
WALLPAPERS_DIR=usr/share/wallpapers
KONSOLESCHEMAS=$(wildcard konsole-schemas/*.schema)
THEMEDIR=usr/share/apps/ksplash/Themes
DEBEVO=DebianEvolution
DEBMOM=DebianMoment
FBSDKDE=FreeBSD_KDE
SQUIRREL=Squirrel
GNUCOOL=GNU_Cool

all: 

install:	install-ksplash
# color schemes
	mkdir -p $(DESTDIR)/$(COLORSCHEMES_DIR)
	$(INSTALL) $(COLORSCHEMES) $(DESTDIR)/$(COLORSCHEMES_DIR)
#  wallpapers
	mkdir -p $(DESTDIR)/$(WALLPAPERS_DIR)
	$(INSTALL) $(WALLPAPERS) $(DESTDIR)/$(WALLPAPERS_DIR)
# konsole-schemas
	mkdir -p $(DESTDIR)/$(APPDIR)/konsole
	$(INSTALL) $(KONSOLESCHEMAS) $(DESTDIR)/$(APPDIR)/konsole

install-ksplash:
	mkdir -p $(DESTDIR)/$(APPDIR)/ksplash/Themes
	for dir in $(SPLASHES); do \
		mkdir -p $(DESTDIR)/$(THEMEDIR)/$$dir ; \
		here=`pwd` ; \
		cd ksplash/$$dir ; \
		allfiles=`ls` ; \
		cd $$here ; \
		for afile in $$allfiles ; do \
			$(INSTALL) ksplash/$$dir/$$afile $(DESTDIR)/$(THEMEDIR)/$$dir ; \
		cd $$here ; \
	done ; done
