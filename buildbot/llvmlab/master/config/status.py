import buildbot
import buildbot.status.html
import buildbot.status.mail
import buildbot.status.words
import config
import os

from zorg.buildbot.PhasedBuilderUtils import set_config_option
from zorg.buildbot.util.ConfigEmailLookup import ConfigEmailLookup
from zorg.buildbot.util.InformativeMailNotifier import InformativeMailNotifier 


def get_status_targets(standard_builders):
    # Get from/to email addresses.
    from_email = set_config_option('Master Options', 'from_email')
    default_email = set_config_option('Master Options', 'default_email')

    # Check whether we are in testing mode, if so, just add minimal and verbose
    # status clients.
    if True:
        return [
            buildbot.status.html.WebStatus(
                http_port = 8013, allowForce = True),

            InformativeMailNotifier(fromaddr = from_email,
                                    extraRecipients = ['david_dean@apple.com'],
                                    sendToInterestedUsers = False,
                                    mode = 'change',
                                    addLogs = False,
                                    num_lines = 15)]

    # Get the path to the authors file we use for email lookup.
    llvm_authors_path = os.path.join(os.path.dirname(__file__), 
                                     set_config_option('Master Options',
                                                        'llvm_authors_path'))

    # Construct a lookup object to be used for public builders.
    public_lookup = ConfigEmailLookup(
        llvm_authors_path, default_address = 'llvm-testresults@cs.uiuc.edu')

    return [
        buildbot.status.html.WebStatus(
            http_port = 8013, allowForce = True),
        buildbot.status.words.IRC('irc.oftc.net', 'llvmlab',
                  port=6668,
                  channels=['llvm'],
                  allowForce=False,
                  password='smooshy',
                  notify_events=['successToFailure', 'failureToSuccess'],
                  categories=['build', 'test']),

        # Experimental failing build notifier.
        #
        # These emails only go to the catch-all list.
        InformativeMailNotifier(
            fromaddr = from_email,
            extraRecipients = ['llvm-testresults@cs.uiuc.edu'],
            sendToInterestedUsers = False,
            mode = 'failing',
            categories = ['experimental'],
            addLogs = False,
            num_lines = 15),

        # Regular problem build notifier.
        #
        # These emails go to the interested (internal users), and the catch-all
        # list.
        InformativeMailNotifier(
            fromaddr = from_email,
            lookup = internal_lookup,
            extraRecipients = ['llvm-testresults@cs.uiuc.edu'],
            sendToInterestedUsers = True,
            mode = 'problem',
            categories = ['build', 'test'],
            addLogs = False,
            num_lines = 15),

        # Regular failing build notifier.
        #
        # These emails only go to the catch-all list.
        #
        # FIXME: Eventually, these should also go to the current build czars.
        # TODO: change subject to differentiate these from the problem emails
        InformativeMailNotifier(
            fromaddr = from_email,
            sendToInterestedUsers = False,
            extraRecipients = ['llvm-testresults@cs.uiuc.edu'],
            mode = 'failing',
            categories = ['build', 'test'],
            addLogs = False,
            num_lines = 15),

        # Phase status change notifier.
        #
        # These emails only go to the catch-all list.
        buildbot.status.mail.MailNotifier(
            fromaddr = from_email,
            sendToInterestedUsers = False,
            extraRecipients = ['llvm-testresults@cs.uiuc.edu'],
            mode = 'change',
            categories = ['status']),]

