import os
import buildbot
import buildbot.status.html
import buildbot.status.mail
import buildbot.status.words

import config
from zorg.buildbot.util.ConfigEmailLookup import ConfigEmailLookup
from zorg.buildbot.util.InformativeMailNotifier import InformativeMailNotifier

# Returns a list of Status Targets. The results of each build will be
# pushed to these targets. buildbot/status/*.py has a variety to choose from,
# including web pages, email senders, and IRC bots.

def get_status_targets(standard_builders):

    from buildbot.status import html
    from buildbot.status.web import auth, authz
    authz_cfg=authz.Authz(
                      # change any of these to True to enable; see the manual for more
                      # options
                      gracefulShutdown   = False,
                      forceBuild         = True, # use this to test your slave once it is set up
                      forceAllBuilds     = False,
                      pingBuilder        = True,
                      stopBuild          = True,
                      stopAllBuilds      = False,
                      cancelPendingBuild = True,
                      )

    default_email = config.options.get('Master Options', 'default_email')

    return [
        buildbot.status.html.WebStatus(
            http_port = 8011, authz=authz_cfg),
        buildbot.status.mail.MailNotifier(
            fromaddr = "llvm.buildmaster@lab.llvm.org",
            extraRecipients = [default_email],
            lookup = ConfigEmailLookup(os.path.join(os.path.dirname(__file__),
                                                    "llvmauthors.cfg"),
                                       default_email),
            mode = "problem",
            builders = standard_builders),
        buildbot.status.words.IRC(
            host = "irc.oftc.net", nick = "llvmbb", channels = ["#llvm"],
            allowForce = True,
            notify_events = ['successToFailure', 'failureToSuccess']),
        InformativeMailNotifier(
            fromaddr = "llvm.buildmaster@lab.llvm.org",
            sendToInterestedUsers= False,
            extraRecipients = ["baldrick@free.fr"],
            subject="Build %(builder)s Failure",
            mode = "failing",
            builders = ["dragonegg-i386-linux", "dragonegg-x86_64-linux"],
            addLogs=False,
            num_lines = 15),
        InformativeMailNotifier(
            fromaddr = "llvm.buildmaster@lab.llvm.org",
            sendToInterestedUsers= False,
            extraRecipients = ["tobias@grosser.es"],
            subject="Build %(builder)s Failure",
            mode = "failing",
            builders = ["polly-amd64-linux"],
            addLogs=False,
            num_lines = 15),
        InformativeMailNotifier(
            fromaddr = "llvm.buildmaster@lab.llvm.org",
            sendToInterestedUsers= False,
            extraRecipients = ["dblaikie@gmail.com", "echristo@gmail.com",
                               "daniel.malea@intel.com", "matt.kopec@intel.com",
                               "andrew.kaylor@intel.com", "ashok.thirumurthi@intel.com"],
            subject="Build %(builder)s Failure",
            mode = "failing",
            builders = ["clang-x86_64-darwin10-gdb", "clang-x86_64-ubuntu-gdb-75"],
            addLogs=False,
            num_lines = 15),
        InformativeMailNotifier(
            fromaddr = "llvm.buildmaster@lab.llvm.org",
            sendToInterestedUsers= False,
            extraRecipients = ["gribozavr@gmail.com"],
            subject="Build %(builder)s Failure",
            mode = "failing",
            builders = ["clang-x86_64-debian-fast"],
            addLogs=False,
            num_lines = 15),
        ]
