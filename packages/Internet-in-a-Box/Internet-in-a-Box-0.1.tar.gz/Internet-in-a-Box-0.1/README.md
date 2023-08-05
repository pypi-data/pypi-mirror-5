Internet In A Box
=================

2013

Project Homepage: http://internet-in-a-box.org

*THIS PROJECT IS UNDER HEAVY INITIAL CONSTRUCTION*
Please come back in a few weeks. :)


Abstract
--------

The Internet-in-a-Box is a small, inexpensive device which provides essential
Internet resources without any Internet connection.  It provides a local copy
of half a terabyte of the world's Free information.

An Internet-in-a-Box provides:

- *Wikipedia*: Complete Wikipedia in a dozen different languages
- *Maps*: Zoomable world-wide maps down to street level
- *E-books*: Over 35 thousand e-books in a variety of languages
- *Software*: Huge library of Open Source Software, including installable Ubuntu Linux OS with all software package repositories.  Includes full source code for study or modification.
- *Video*: Hundreds of hours of instructional videos
- *Chat*: Simple instant messaging across the community


OpenStreetMap
-------------

We are installing on an Ubuntu 12.04 quad-core 3GHz machine with
16 GB RAM and a 500GB SSD.  Planet import took 91 hours.

You must have a beefy machine.  Note that on an quad-core 8GB RAM
2.5GHz machine the planet import time was TWO WEEKS!

More detailed instructions are available from the switch2osm.org project.  This is generally what I followed:
http://switch2osm.org/serving-tiles/building-a-tile-server-from-packages/

They also have instructions to have you build all tools from source:
http://switch2osm.org/serving-tiles/manually-building-a-tile-server-12-04/

To understand what you are doing, and how to optimize performance, see:
http://www.geofabrik.de/media/2012-09-08-osm2pgsql-performance.pdf

1. Download Planet File

Download the latest OSM Planet file.  Use the newer "pbf" format (which is
binary), and not the "bz2" format (which is XML).

The latest planet.osm.pbf.torrent can be downloaded via bittorrent from:
http://osm-torrent.torres.voyager.hr/files/planet-latest.osm.pbf.torrent

planet.osm.pbf is about 20 GB in size.



2. Install OSM Software

    add-apt-repository ppa:kakrueger/openstreetmap
    apt-get update
    apt-get remove --purge postgresql-9.1-postgis postgresql-client-9.1 postgresql-client-common postgresql-common
    apt-get install libapache2-mod-tile osm2pgsql openstreetmap-postgis-db-setup
    dpkg-reconfigure openstreetmap-postgis-db-setup


Not sure how much of the following is actually required:

    sudo apt-get install subversion git-core tar unzip wget bzip2 build-essential autoconf libtool libxml2-dev libgeos-dev libpq-dev libbz2-dev proj munin-node munin libprotobuf-c0-dev protobuf-c-compiler libfreetype6-dev libpng12-dev libtiff4-dev libicu-dev libboost-all-dev libgdal-dev libcairo-dev libcairomm-1.0-dev apache2 apache2-dev libagg-dev

(Make sure to install from ppa:kakrueger and not the outdated
versions in the main Ubuntu repositories or things will be bad)

    osm2pgsql -v
    osm2pgsql SVN version 0.81.0


3. Prepare a swap file on the SSD

Create a 20 GB swap file on the SSD.

    dd if=/dev/zero of=/mnt/ssd/swapfile bs=1024 count=20000000
    mkswap -L ssdswap /mnt/ssd/swapfile
Add line to /etc/fstab, and comment out existing swap
    /mnt/ssd/swapfile none            swap    sw              0       0
Activate swap
    swapoff -a  # Turn off existing swap
    swapon -a  # Turn on new SSD swap


4. Move Postgres database to SSD

    /etc/init.d/postgresql stop
    mv -v /var/lib/postgresql /mnt/ssd/
    ln -s /mnt/ssd/postgresql /var/lib/postgresql
    /etc/init.d/postgresql start


5. Tune Postgresql

See section "Tuning your system" in http://switch2osm.org/serving-tiles/manually-building-a-tile-server/ 


6. Import planet (will takes days)

    time osm2pgsql --number-processes 4 --slim -C 12000 planet-130206.osm.pbf

--slim is only needed if you want to do incremental updates, but has a performance penalty.

osm2pgsql took 91 hours to complete WITHOUT --number-processes and WITH --slim.

See the performance (and options) of others at:
http://wiki.openstreetmap.org/wiki/Osm2pgsql/benchmarks

Note you can get statistics on number of nodes, ways, and relations at:
http://www.openstreetmap.org/stats/data_stats.html

Wikipedia
---------

This section describes how to make a complete Mediawiki-based Wikipedia mirror
for many languages.  This is not necessary if you are using kiwix - see the
section on Kiwiz ZIM File Download instead.

Install:
    apt-get install mysql-server php5 apache2 php5-mysql

First relocate the mysql directory.
    mv /var/lib/mysql /var/lib/mysql.orig
    ln -s /knowledge/processed/mysql /var/lib/mysql

Had to inform AppArmor of the new path (make sure there are no symlinks, or
modify this to provide a full path).
    cat >>/etc/apparmor.d/local/usr.sbin.mysqld  <<EOF
    /knowledge/processed/mysql rwk,
    /knowledge/processed/mysql/** rwk,
    EOF

Use wp-download to download the latest wikipedia dumps for various languages.
There is a wpdownloadrc config file in Heritage/wpdownloadrc

    Edit wpdownloadrc to comment out languages you don't want
    pip install wp-download
    wp-download -c wpdownloadrc /knowledge/data/wikipedia/dumps

Once downloaded, you need to import the wikipedia dump data into mysql
databases and mediawiki installations.  To do this use Heritage/scripts/make_wiki.py 

    sudo scripts/make_wiki.py -p mypassword -r rootpassword ar fr ru vi zh

By default, this script will look for wikipedia dumps as organized by
wp-download in /knowledge/data/wikipedia/dumps and select the latest downloaded
dump for each language specified on the command line.  It will create mysql
databases for each language.  It will create a stand-alone mediawiki
installation under /knowledge/processed/wiki/, which should be linked from
/var/www/wiki for proper operation.

    ln -s /knowledge/processed/wiki /var/www/wiki

After this is complete your new wikis should be accessible at http://localhost/wiki/arwiki (for example)


Building a patched zimdump
--------------------------

Due to a bug in zimdump, we need a patched version.

    git clone https://gerrit.wikimedia.org/r/p/openzim.git
    cd openzim/zimlib
    patch -p2 </knowledge/internet-in-a-box/patches/openzim.diff
    ./autogen.sh
    ./configure
    make -j4
    cp src/tools/zimdump /knowledge/sys/bin-amd64/zimdump-patched

To turn on the use of zimdump:

    cd /knowledge/internet-in-a-box
    cat &lt;&lt;EOF >local.ini
    [KIWIX]
    url = /iiab/zim
    zimdump = /knowledge/sys/bin-amd64/zimdump-patched


Kiwix ZIM File Download
-----------------------

1. Install Firefox plugin "Download Them All"
2. http://www.kiwix.org/index.php/Template:ZIMdumps
3. Tools->Download Them All->DownloadThemAll
4. In DTA dialog, open "Fast Filtering"
5. Enter Fast Filter "*.zim.torrent"
6. Start!
7. mv ~/Downloads/*.zim.torrent /knowledge/data/zim/torrents/
8. Open Transmission Bitorrent client
9. Open -> select all *.zim.torrent in file dialog
10. Select download destination /knowledge/data/zim/downloads/


Ubuntu Software Repository
--------------------------

    apt-get install apt-mirror
    apt-mirror scripts/mirror.list
(will mirror into /knowledge/data/ubuntu/12.04)


Project Gutenberg Mirror
------------------------

    cd /knowledge/data/gutenberg  (?)
    while (true); do (date; . ../../Heritage/rsync_gutenberg; sleep 3600) | tee -a 20120823.log; done


Khan Academy
------------

For the latest torrent, see the newest comments on the official Khan Academy issue ticket:

    http://code.google.com/p/khanacademy/issues/detail?id=191

As of 3/17/2013 the lastest most complete torrent by Zurd is at:

    http://www.legittorrents.info/index.php?page=torrent-details&id=f388128c5f528d248235b4c7b67eb81c3804eb43

Install some codec dependencies (Ubuntu 12.04):

    sudo -E wget --output-document=/etc/apt/sources.list.d/medibuntu.list http://www.medibuntu.org/sources.list.d/$(lsb_release -cs).list && sudo apt-get --quiet update && sudo apt-get --yes --quiet --allow-unauthenticated install medibuntu-keyring && sudo apt-get --quiet update
    apt-get install ffmpeg libfaac0 libavcodec-extra-53 libx264-120

Move downloaded webm format videos to the final modules directory:

    mkdir /knowledge/modules/khanacademy
    mv /knowledge/data/khanacadey.org/Khan\ Academy/ /knowledge/modules/khanacademy/webm 

Convert webm to a more mobile friendly format:

    scripts/video_convert.py --extension .webm --threads 4 /knowledge/data/khanacademy.org/Khan\ Academy/ /knowledge/modules/khanacademy/h264

video_convert.py is designed to be run efficiently on multiple NFS-mounted computers simultaneously in parallel.

(this takes approximately 20 hours on two four-core CPUs)


We must create a tree of symlinks to our video.
The purpose of building a tree of symlinks is to that the front end
web server can serve the video files directly, allowing Accept-Ranges
and other features to work with the finicky video browser clients

    ipython
    import iiab.khan
    iiab.khan.make_symlinks('/knowledge/modules/khanacademy/webm/', '/knowledge/modules/khanacademy/h264/', '/knowledge/modules/khanacademy/khanlinks')


Rsync to Device
---------------

    mkdir /knowledge
    cd /knowledge
    time rsync --delete -avrP rsync://orlop/knowledge/modules/ modules


Web Service
-----------

We run nginx as our front end web service:

    apt-get install nginx
    cp iiab_nginx.conf /etc/nginx/sites-enabled/

Basic Python requirements:

    cd internet-in-a-box
    pip install -r requirements.txt
    ./run.py

Launch kiwix

    cd /knowledge/modules/wikipedia-kiwix
    ../../sys/bin-arm/kiwix-serve --library library.xml --port 25001


Rsync Server
------------

    apt-get install rsyncd
    ln -s /knowledge/internet-in-a-box/conf/rsyncd.conf /etc/rsyncd.conf
    Edit /etc/default/rsync and set RSYNC_ENABLE=true
    /etc/init.d/rsyncd start


Installing on the GoFlex Home
-----------------------------

First we hack the firmware, re-format the drive, and install our Debian image on the device.

If this is a used device with an unknown username and password, reset the
device by booting it, and then pressing with a paperclip the reset button in
the hole on the side for 15 seconds.  Then go to the IP address and you will be
able to setup from factory defaults.

In general, follow the Arch Linux Arm instructions at:

http://archlinuxarm.org/platforms/armv5/seagate-goflex-home

*Except* in step 12, instead of installing the Arch Linux
tarball, install our Debian tarball from /knowledge/sys/ instead.

    cd alarm
    scp braddock@192.168.1.105:/knowledge/sys/debian-squeeze-20130501a.tgz .
    tar xvzf debian-squeeze-20130501a.tgz
    rm debian-squeeze-20130501a.tgz
    sync

After reboot: 

1. connect drive to SATA on orlop.

2. Format second partition to ext3 fs with label "data"

3. Mount "data"

    mount /dev/sda2 /mnt/mnt

4. Copy knowledge dataset to "data" (using rsync - which is slow)

    sudo -i
    cd /mnt/mnt
    mkdir knowledge
    time rsync --delete -avrP /knowledge/modules /knowledge/internet-in-a-box /knowledge/sys knowledge
    (takes about 10 hours)

4. Copy knowledge dataset to "data" (using tar)

    sudo -i
    mkdir /mnt/mnt/knowledge
    cd /knowledge
    time tar cBf - modules internet-in-a-box sys | (cd /mnt/mnt/knowledge; tar xvBf -)


Installing on an OLPC XO Laptop
-------------------------------

Installation of the Internet-in-a-Box server on an XO-4 running OLPC OS 13.1

1. Flash the OS with a USB key, boot, connect to your wireless network

2. Open Terminal, sudo -i

3. Enable SSHD (optional)

    vi /etc/ssh/sshd_config
    Uncomment line "PermitRootLogin yes"
    systemctl restart sshd
    passwd root  # Create a root password
    The rest of these instructions can now be executed via ssh
 
4.  Install compilers and build essentials:

    (This is overkill - we don't need all these dependencies)
    yum -y groupinstall "Development Tools"
    yum -y install python-devel python-pip nginx xz-devel screen vim 

5. Install python dependencies

    python-pip install Flask-Babel whoosh 
    (You must clean up the pip-build-root dir before SQLAlchemy
    or you will run out of /tmp space)
    rm -rvf /tmp/pip-build-root
    python-pip install Flask-SQLAlchemy

6. Plug in the Internet-in-a-Box USB Hard Drive

    It will auto-mount at /run/media/olpc/knowledge

7. Create a link from /knowledge

    ln -s /run/media/olpc/knowledge/knowledge /knowledge

8. Link nginx configuration

    ln -s /knowledge/internet-in-a-box/conf/iiab_nginx.conf /etc/nginx/conf.d/

9. Create a local.ini configuration file

    cd /knowledge/internet-in-a-box 
    cat <<EOF >local.ini
    [KIWIX]
    url = /iiab/zim
    zimdump = /knowledge/sys/bin-arm/zimdump-patched
    EOF


10. Run!

    scripts/startup-xo.sh


----
