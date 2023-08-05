# -*- coding: UTF-8 -*-

from django.core.management.base import BaseCommand
from optparse import make_option
import unicodedata
import shout
import daemon
import daemon.pidfile
from signal import SIGTSTP, SIGABRT
import sys, os
from jukebox.jukebox_core import api


class Command(BaseCommand):
    skipCurrentSong = False

    option_list = BaseCommand.option_list + (
        make_option(
            "--start",
            action="store_true",
            dest="start",
            help="Start shoutcast streaming"
        ),
        make_option(
            "--stop",
            action="store_true",
            dest="stop",
            help="Stop shoutcast streaming"
        ),
        make_option(
            "--fg",
            action="store_true",
            dest="fg",
            help="Start shoutcast streaming in foreground"
        ),
        make_option(
            "--host",
            action="store",
            dest="host",
            help="Host of shoutcast server"
        ),
        make_option(
            "--port",
            action="store",
            dest="port",
            help="Port of shoutcast server"
        ),
        make_option(
            "--password",
            action="store",
            dest="password",
            help="Source password of shoutcast server"
        ),
    )

    def handle(self, *args, **options):
        pidFile = os.path.dirname(
            os.path.abspath(__file__)
        ) + "/../../daemon.pid"

        if options["start"] or options["fg"]:
            if (options["host"] is None or
                options["port"] is None or
                options["password"] is None
            ):
                print "Required arguments: host, port, password"
                self.print_help("jukebox_shout", "help")
                return

            if os.path.exists(pidFile):
                print "Daemon already running, pid file exists"
                return

            pid = daemon.pidfile.TimeoutPIDLockFile(
                pidFile,
                10
            )

            self.shout = shout.Shout()
            print "Using libshout version %s" % shout.version()

            self.shout.audio_info = {
                shout.SHOUT_AI_BITRATE: "128",
                shout.SHOUT_AI_SAMPLERATE: "44100",
                shout.SHOUT_AI_CHANNELS: "2"
            }
            self.shout.name = "Democratic Jukebox"
            self.shout.url = "http://" + options["host"] + ":" + \
                 options["port"] + "/stream"
            self.shout.mount = "/stream"
            self.shout.port = int(options["port"])
            self.shout.user = "source"
            self.shout.password = options["password"]
            self.shout.genre = "Mixed"
            self.shout.description = "Your democratic music player"
            self.shout.host = options["host"]
            self.shout.ogv = 0
            self.shout.format = "mp3"
            try:
                self.shout.open()
                self.shout.close()
            except shout.ShoutException as exception:
                print "Error: " + str(exception)
                return

            if options["start"]:
                print "Starting jukebox_shout daemon..."
                self.daemon = daemon.DaemonContext(
                    uid=os.getuid(),
                    gid=os.getgid(),
                    pidfile=pid,
                    working_directory=os.getcwd(),
                    detach_process=True,
                    signal_map={
                        SIGTSTP: self.shutdown,
                        SIGABRT: self.skipSong
                    }
                )

                with self.daemon:
                    self.shout.open()

                    print "Register player"
                    pid = int(open(pidFile).read())
                    players_api = api.players()
                    players_api.add(pid)

                    songs_api = api.songs()
                    while 1:
                        self.sendfile(songs_api.getNextSong())

            elif options["fg"]:
               self.shout.open()

               print "Register player"
               pid = os.getpid()
               players_api = api.players()
               players_api.add(pid)

               songs_api = api.songs()
               while 1:
                   song = songs_api.getNextSong()
                   self.sendfile(song)

        elif options["stop"]:
            if not os.path.exists(pidFile):
                print "Daemon not running"
                return

            print "Stopping daemon..."
            pid = int(open(pidFile).read())
            os.kill(pid, SIGTSTP)

            print "Unregister player " + str(pid)
            players_api = api.players()
            players_api.remove(pid)
        else:
            self.print_help("jukebox_shout", "help")

    def shutdown(self, signal, action):
        self.shout.close()
        self.daemon.close()
        sys.exit(0)

    def skipSong(self, signal, action):
        self.skipCurrentSong = True

    def sendfile(self, song_instance):
        if not os.path.exists(song_instance.Filename.encode('utf8')):
            print "File not found: %s" % (
                song_instance.Filename.encode('utf8'))
            return

        print "Streaming file %s" % song_instance.Filename.encode('utf8')
        f = open(song_instance.Filename.encode('utf8'))
        self.shout.set_metadata({"song": self.getMetaData(song_instance)})
        while 1:
            if self.skipCurrentSong:
                print "skipping current song"
                self.shout.sync()
                self.skipCurrentSong = False
                break
            else:
                print "sending..."
                buf = f.read(4096)
                if not len(buf):
                    break
                try:
                    self.shout.send(buf)
                except shout.ShoutException, exc:
                    print "Error: " + str(exc)
                    break
                self.shout.sync()
        f.close()

    def getMetaData(self, song_instance):
        return unicodedata.normalize(
            "NFKD",
            song_instance.Artist.Name
        ).encode(
            "ascii",
            "ignore"
        ) + " - " + unicodedata.normalize(
            "NFKD",
            song_instance.Title
        ).encode(
            "ascii",
            "ignore"
        )
