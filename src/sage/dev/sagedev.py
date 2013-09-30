- David Roe, Frej Drejhammar, Julian Rueth, Martin Raum, Nicolas M. Thiery, R.,
from patch import MercurialPatchMixin
# the name of the branch which holds the vanilla clone of sage
USER_BRANCH = re.compile(r"^u/([^/]+)/")
#
# The first line should contain a short summary of your changes, the
# following lines should contain a more detailed description. Lines
# starting with '#' are ignored.
class SageDev(MercurialPatchMixin):
      stored in ``DOT_SAGE/devrc``.
            self.git = GitInterface(self.config['git'], self._UI)
                self._UI.show('The developer scripts used to store some of their data in "{0}". This file has now moved to "{1}". I moved "{0}" to "{1}". This might cause trouble if this is a fresh clone of the repository in which you never used the developer scripts before. In that case you should manually delete "{1}" now.'.format(old_file, new_file))
    def create_ticket(self):
        Create a new ticket on trac.
            :meth:`checkout`, :meth:`pull`, :meth:`edit_ticket`
        This fails if the internet connection is broken::
            sage: dev.create_ticket()
        self._UI.info('To start work on ticket #{0}, create a branch for this ticket and check it out with "{1}".'
                      .format(ticket, self._format_command("checkout", ticket=ticket)))
        return ticket
    def checkout(self, ticket=None, branch=None, base=''):
        r"""
        Checkout another branch.
        If ``ticket`` is specified, and ``branch`` is an existing local branch,
        then ``ticket`` will be associated to it, and ``branch`` will be
        checked out into the working directory.
        Otherwise, if there is no local branch for ``ticket``, the branch
        specified on trac will be pulled to ``branch`` unless ``base`` is
        set to something other than the empty string ``''``. If the trac ticket
        does not specify a branch yet or if ``base`` is not the empty string,
        then a new one will be created from ``base`` (per default, the master
        branch).

        If ``ticket`` is not specified, then checkout the local branch
        ``branch`` into the working directory.

        INPUT:

        - ``ticket`` -- a string or an integer identifying a ticket or ``None``
          (default: ``None``)

        - ``branch`` -- a string, the name of a local branch; if ``ticket`` is
          specified, then this defaults to ticket/``ticket``.

        - ``base`` -- a string or ``None``, a branch on which to base a new
          branch if one is going to be created (default: the empty string
          ``''`` to create the new branch from the master branch), or a ticket;
          if ``base`` is set to ``None``, then the current ticket is used. If
          ``base`` is a ticket, then the corresponding dependency will be
          added. Must be ``''`` if ``ticket`` is not specified.

        .. SEEALSO::

            :meth:`pull`, :meth:`create_ticket`, :meth:`vanilla`

        TESTS:

        Set up a single user for doctesting::

            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()

        Create a few branches::

            sage: dev.git.silent.branch("branch1")
            sage: dev.git.silent.branch("branch2")

        Checking out a branch::

            sage: dev.checkout(branch="branch1")
            sage: dev.git.current_branch()
            'branch1'

        Create a ticket and checkout a branch for it::
            sage: UI.append("Summary: summary\ndescription")
            sage: dev.create_ticket()
            1
            sage: dev.checkout(ticket=1)
            sage: dev.git.current_branch()
            'ticket/1'
        """
        if ticket is not None:
            self.checkout_ticket(ticket=ticket, branch=branch, base=base)
        elif branch is not None:
            if base != '':
                raise SageDevValueError("base must not be specified if no ticket is specified.")
            self.checkout_branch(branch=branch)
        else:
            raise SageDevValueError("at least one of ticket or branch must be specified.")

    def checkout_ticket(self, ticket, branch=None, base=''):
        Checkout the branch associated to ``ticket``.
        associated to it, and ``branch`` will be checked out into the working directory.
        specified on trac will be pulled to ``branch`` unless ``base`` is
            :meth:`pull`, :meth:`create_ticket`, :meth:`vanilla`
        Alice tries to checkout ticket #1 which does not exist yet::
            sage: alice.checkout(ticket=1)
            ValueError: "1" is not a valid ticket name or ticket does not exist on trac.
            sage: bob.checkout(ticket=1)
        Now alice can check it out, even though there is no branch on the
            sage: alice.checkout(ticket=1)
        If Bob commits something to the ticket, a ``checkout`` by Alice
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.checkout(ticket=1)
        If Alice had not checked that ticket out before, she would of course
            sage: alice.checkout(ticket=1) # ticket #1 refers to the non-existant branch 'ticket/1'
            Ticket #1 refers to the non-existant local branch "ticket/1". If you have not manually interacted with git, then this is a bug in sagedev. Removing the association from ticket #1 to branch "ticket/1".
        Checking out a ticket with untracked files::
            sage: alice.checkout(ticket=2)
            sage: alice.checkout(ticket=1)
        Checking out a ticket with untracked files which make a checkout
            sage: alice.checkout(ticket=2)
            sage: alice.checkout(ticket=1)
            This happened while executing "git -c user.email=doc@test.test -c
            user.name=alice checkout ticket/1".
        Checking out a ticket with uncommited changes::
            sage: alice.checkout(ticket=2)
            The following files in your working directory contain uncommitted changes:
             tracked
            Do you want me to discard any changes which are not committed? Should
            the changes be kept? Or do you want to stash them for later? [discard/Keep/stash] d

        Now follow some single user tests to check that the parameters are interpreted correctly::

            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()
            sage: dev._wrap("_dependencies_for_ticket")

        First, create some tickets::

            sage: UI.append("Summary: ticket1\ndescription")
            sage: dev.create_ticket()
            1
            sage: dev.checkout(ticket=1)
            sage: UI.append("Summary: ticket2\ndescription")
            sage: dev.create_ticket()
            2
            sage: dev.checkout(ticket=2)
            sage: dev.git.silent.commit(allow_empty=True, message="second commit")
            sage: dev.git.commit_for_branch('ticket/2') != dev.git.commit_for_branch('ticket/1')
            True

        Check that ``base`` works::

            sage: UI.append("Summary: ticket3\ndescription")
            sage: dev.create_ticket()
            3
            sage: dev.checkout(ticket=3, base=2)
            sage: dev.git.commit_for_branch('ticket/3') == dev.git.commit_for_branch('ticket/2')
            True
            sage: dev._dependencies_for_ticket(3)
            (2,)
            sage: UI.append("Summary: ticket4\ndescription")
            sage: dev.create_ticket()
            4
            sage: dev.checkout(ticket=4, base='ticket/2')
            sage: dev.git.commit_for_branch('ticket/4') == dev.git.commit_for_branch('ticket/2')
            True
            sage: dev._dependencies_for_ticket(4)
            ()

        In this example ``base`` does not exist::

            sage: UI.append("Summary: ticket5\ndescription")
            sage: dev.create_ticket()
            5
            sage: dev.checkout(ticket=5, base=1000)
            ValueError: "1000" is not a valid ticket name or ticket does not exist on trac.

        In this example ``base`` does not exist locally::

            sage: UI.append("Summary: ticket6\ndescription")
            sage: dev.create_ticket()
            6
            sage: dev.checkout(ticket=6, base=5)
            ValueError: Branch field is not set for ticket #5 on trac.

        Creating a ticket when in detached HEAD state::

            sage: dev.git.super_silent.checkout('HEAD', detach=True)
            sage: UI.append("Summary: ticket detached\ndescription")
            sage: dev.create_ticket()
            7
            sage: dev.checkout(ticket=7)
            sage: dev.git.current_branch()
            'ticket/7'

        Creating a ticket when in the middle of a merge::

            sage: dev.git.super_silent.checkout('-b','merge_branch')
            sage: with open('merge', 'w') as f: f.write("version 0")
            sage: dev.git.silent.add('merge')
            sage: dev.git.silent.commit('-m','some change')
            sage: dev.git.super_silent.checkout('ticket/7')
            sage: with open('merge', 'w') as f: f.write("version 1")
            sage: dev.git.silent.add('merge')
            sage: dev.git.silent.commit('-m','conflicting change')
            sage: from sage.dev.git_error import GitError
            sage: try:
            ....:     dev.git.silent.merge('merge_branch')
            ....: except GitError: pass
            sage: UI.append("Summary: ticket merge\ndescription")
            sage: dev.create_ticket()
            8
            sage: UI.append("n")
            sage: dev.checkout(ticket=8)
            Your repository is in an unclean state. It seems you are in the middle of a merge of some sort. To complete this command you have to reset your repository to a clean state. Do you want me to reset your repository? (This will discard many changes which are not commited.) [yes/No] n
            Could not check out branch "ticket/8" because your working directory is not in a clean state.
            sage: dev.git.reset_to_clean_state()

        Creating a ticket with uncommitted changes::

            sage: open('tracked', 'w').close()
            sage: dev.git.silent.add('tracked')
            sage: UI.append("Summary: ticket merge\ndescription")
            sage: dev.create_ticket()
            9
            sage: UI.append("keep")
            sage: dev.checkout(ticket=9) # the new branch is based on master which is not the same commit as the current branch ticket/7 - so it is not a valid option to 'keep' changes
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? Your command can only be completed if you discard or stash your changes. [discard/Keep/stash] keep
            Could not check out branch "ticket/9" because your working directory is not clean.
            sage: UI.append("Summary: ticket merge\ndescription")
            sage: dev.create_ticket()
            10
            sage: UI.append("keep")
            sage: dev.checkout(ticket=10, base='ticket/7') # now we can keep changes because the base is the same commit as the current branch
            The following files in your working directory contain uncommitted changes:
             tracked
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? [discard/Keep/stash] keep
        # if branch points to an existing branch make it the ticket's branch and check it out
            self._UI.info('The branch for ticket #{0} is now "{1}".'.format(ticket, branch))
            self._UI.info('Now checking out branch "{0}".'.format(branch))
            self.checkout_branch(branch)
        # if there is a branch for ticket locally, check it out
                self._UI.info('Checking out branch "{0}".'.format(branch))
                self.checkout_branch(branch)
            raise SageDevValueError('currently on no ticket, "base" must not be None')
            base = self._local_branch_for_ticket(base, pull_if_not_found=True)
                    self._UI.info('The branch field on ticket #{0} is not set. Creating a new branch "{1}" off the master branch "{2}".'.format(ticket, branch, MASTER_BRANCH))
                    # pull the branch mentioned on trac
                        self._UI.error('The branch field on ticket #{0} is set to "{1}". However, the branch "{1}" does not exist. Please set the field on trac to a field value.'.format(ticket, remote_branch))
                        self.pull(remote_branch, branch)
                        self._UI.info('Created a new branch "{0}" based on "{1}".'.format(branch, remote_branch))
                        self._UI.error('Could not check out ticket #{0} because the remote branch "{1}" for that ticket could not be pulled.'.format(ticket, remote_branch))
                    if not self._UI.confirm('Creating a new branch for #{0} based on "{1}". The trac ticket for #{0} already refers to the branch "{2}". As you are creating a new branch for that ticket, it seems that you want to ignore the work that has already been done on "{2}" and start afresh. Is this what you want?'.format(ticket, base, remote_branch), default=False):
                        command += self._format_command("checkout", ticket=ticket)
                        self._UI.info('To work on a fresh copy of "{0}", use "{1}".'.format(remote_branch, command))
                self._UI.info('Creating a new branch for #{0} based on "{1}".'.format(ticket, base))
                self._UI.info('Deleting local branch "{0}".')
        self._UI.info('Checking out to newly created branch "{0}".'.format(branch))
        self.checkout_branch(branch)
    def checkout_branch(self, branch):
        Checkout to the local branch ``branch``.
        - ``branch`` -- a string, the name of a local branch
        Checking out a branch::
            sage: dev.checkout(branch="branch1")
            sage: dev.checkout(branch="branch3")
            ValueError: Branch "branch3" does not exist locally.
        Checking out branches with untracked files::
            sage: open("untracked", "w").close()
            sage: dev.checkout(branch="branch2")
        Checking out a branch with uncommitted changes::
            sage: open("tracked", "w").close()
            sage: dev.checkout(branch="branch1")
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? Your command can only be completed if you discard or stash your changes. [discard/Keep/stash] keep
            Could not check out branch "branch1" because your working directory is not clean.
            sage: dev.checkout(branch="branch1")
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? Your command can only be completed if you discard or stash your changes. [discard/Keep/stash] s
            Your changes have been recorded on a new branch "stash/1".
            sage: dev.checkout(branch='branch2')
            sage: UI.append("n")
            The changes recorded in "stash/1" have been restored in your working directory.  Would you like to delete the branch they were stashed in? [Yes/no] n
            sage: dev.checkout(branch="branch1")
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? Your command can only be completed if you discard or stash your changes. [discard/Keep/stash] d
        Checking out a branch when in the middle of a merge::
            sage: dev.checkout(branch='merge_branch')
            Your repository is in an unclean state. It seems you are in the middle of a merge of some sort. To complete this command you have to reset your repository to a clean state. Do you want me to reset your repository? (This will discard many changes which are not commited.) [yes/No] n
            Could not check out branch "merge_branch" because your working directory is not in a clean state.
        Checking out a branch when in a detached HEAD::
            sage: dev.checkout(branch='branch1')
            sage: dev.checkout(branch='branch1')
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? Your command can only be completed if you discard or stash your changes. [discard/Keep/stash] discard
        Checking out a branch with untracked files that would be overwritten by
        the checkout::
            sage: dev.checkout(branch='branch2')
            This happened while executing "git -c user.email=doc@test.test -c
            user.name=doctest checkout branch2".
            error: The following untracked working tree files would be overwritten 
            by checkout:
            self._UI.error('Could not check out branch "{0}" because your working directory is not in a clean state.'
                           .format(branch))
            self._UI.info('To checkout "{0}", use "{1}".'.format(branch, self._format_command("checkout",branch=branch)))
            raise

        current_commit = self.git.commit_for_ref('HEAD')
        target_commit = self.git.commit_for_ref(branch)
        try:
            self.clean(cancel_unless_clean = (current_commit != target_commit))
        except OperationCancelledError:
            self._UI.error('Could not check out branch "{0}" because your working directory is not clean.'.format(branch))
            # this leaves locally modified files intact (we only allow this to happen if current_commit == target_commit
    def pull(self, ticket_or_remote_branch=None, branch=None):
        Pull ``ticket_or_remote_branch`` to ``branch``.
            sage: alice.create_ticket()
            1
            sage: alice.checkout(ticket=1)
        Bob attempts to pull for the ticket but fails because there is no
            sage: bob.pull(1)
            sage: bob.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
        Bob pulls the changes for ticket 1::
            sage: bob.pull()
            Merging the remote branch "u/alice/ticket/1" into the local branch "ticket/1".
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
        Alice can now pull the changes by Bob without the need to merge
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            Merge branch 'u/bob/ticket/1' of ... into ticket/1
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
        Now, the pull fails; one would have to use :meth:`merge`::
            sage: alice._UI.append("abort")
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            There was an error during the merge. Most probably there were conflicts when merging. The following should make it clear which files are affected:
            Auto-merging alices_file
            CONFLICT (add/add): Merge conflict in alices_file
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] abort
        Undo the latest commit by alice, so we can pull again::
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
            sage: alice._UI.append("abort")
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
            There was an error during the merge. Most probably there were conflicts when merging. The following should make it clear which files are affected:
            Updating ...
            error: The following untracked working tree files would be overwritten by merge:
                bobs_other_file
            Please move or remove them before you can merge.
            Aborting
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] abort
                raise SageDevValueError("branch must be None")

        # merge into the current branch if ticket_or_remote_branch refers to the current ticket
        if branch is None and ticket_or_remote_branch is not None and self._is_ticket_name(ticket_or_remote_branch) and self._ticket_from_ticket_name(ticket_or_remote_branch) == self._current_ticket():
            raise SageDevValueError('No "ticket_or_remote_branch" specified to pull.')
        self._UI.info('Fetching remote branch "{0}" into "{1}".'.format(remote_branch, branch))
            self.merge(remote_branch, pull=True)
                self.git.super_silent.fetch(self.git._repository_anonymous, "{0}:{1}".format(remote_branch, branch))
                # then just nothing happened and we can abort the pull
                e.explain = 'Fetching "{0}" into "{1}" failed.'.format(remote_branch, branch)
                    e.advice = 'You can try to use "{2}" to checkout "{1}" and then use "{3}" to resolve these conflicts manually.'.format(remote_branch, branch, self._format_command("checkout",branch=branch), self._format_command("merge",remote_branch,pull=True))
                    e.explain += "We did not expect this case to occur.  If you can explain your context in sage.dev.sagedev it might be useful to others."
        This is most akin to mercurial's commit command, not git's,
        since we do not require users to add files.
            - :meth:`push` -- Push changes to the remote server.  This
              is the next step once you've committed some changes.
            - :meth:`diff` -- Show changes that will be committed.
            sage: dev.git.super_silent.checkout('-b', 'branch1')
            sage: dev._UI.extend(["added tracked", "y", "y", "y"])
            Do you want to add "tracked"? [yes/No] y
            Do you want to commit your changes to branch "branch1"? I will prompt you for a commit message if you do. [Yes/no] y
            Do you want to commit your changes to branch "branch1"? I will prompt you for a commit message if you do. [Yes/no] y
            self._UI.info('Use "{0}" to checkout a branch.'.format(self._format_command("checkout")))
            self._UI.info('Committing pending changes to branch "{0}".'.format(branch))
                            if self._UI.confirm('Do you want to add "{0}"?'.format(file), default=False):
                    self.git.echo.add(self.git._src, update=True)
                if not self._UI.confirm('Do you want to commit your changes to branch "{0}"?{1}'.format(branch, " I will prompt you for a commit message if you do." if message is None else ""), default=True):
                    self._UI.info('If you want to commit to a different branch/ticket, run "{0}" first.'.format(self._format_command("checkout")))
            - :meth:`push` -- To push changes after setting the remote
              branch
            sage: dev.checkout(ticket=1)
                self._UI.info('Checkout a branch with "{0}" or specify branch explicitly.'.format(self._format_command('checkout')))
        # If we add restrictions on which branches users may push to, we should append them here.
        m = USER_BRANCH.match(remote_branch)
        if remote_branch == 'master' or m and m.groups()[0] != self.trac._username:
            self._UI.warning('The remote branch "{0}" is not in your user scope. You might not have permission to push to that branch. Did you mean to set the remote branch to "u/{1}/{0}"?'.format(remote_branch, self.trac._username))
    def push(self, ticket=None, remote_branch=None, force=False):
        Push the current branch to the Sage repository.
          set to ``remote_branch`` after the current branch has been pushed there.
          branch to push to; if ``None``, then a default is chosen
        - ``force`` -- a boolean (default: ``False``), whether to push if
            - :meth:`commit` -- Save changes to the local repository.
            - :meth:`pull` -- Update a ticket with changes from the remote
              repository.
        TESTS:
        Alice tries to push to ticket 1 which does not exist yet::
            sage: alice.push(ticket=1)
            ValueError: "1" is not a valid ticket name or ticket does not exist on trac.
        Alice creates ticket 1 and pushes some changes to it::
            sage: alice.create_ticket()
            1
            sage: alice.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
        Now Bob can check that ticket out and push changes himself::
            sage: bob.checkout(ticket=1)
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
        Now Alice can pull these changes::
            sage: alice.pull()
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/1".
        After Alice pushed her changes, Bob can not set the branch field anymore::
            sage: alice.push()
            I will now push the following new commits to the remote branch "u/alice/ticket/1":
            I will now change the branch field of ticket #1 from its current value "u/bob/ticket/1" to "u/alice/ticket/1". Is this what you want? [Yes/no] y
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
            Not setting the branch field for ticket #1 to "u/bob/ticket/1" because "u/bob/ticket/1" and the current value of the branch field "u/alice/ticket/1" have diverged.
            sage: bob.pull()
            Merging the remote branch "u/alice/ticket/1" into the local branch "ticket/1".
            sage: bob.push()
            I will now push the following new commits to the remote branch "u/bob/ticket/1":
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
            sage: bob.push(2)
            ValueError: "2" is not a valid ticket name or ticket does not exist on trac.
            sage: bob.checkout(ticket=2)
            sage: bob.checkout(ticket=1)
            sage: bob.push(2)
            You are trying to push the branch "ticket/1" to "u/bob/ticket/2" for ticket #2. However, your local branch for ticket #2 seems to be "ticket/2". Do you really want to proceed? [yes/No] y
            The branch "u/bob/ticket/2" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: bob.push(remote_branch="u/bob/branch1")
            The branch "u/bob/branch1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/bob/ticket/1" to "u/bob/branch1". Is this what you want? [Yes/no] y
        Check that dependencies are pushed correctly::

            sage: bob.merge(2)
            Merging the remote branch "u/bob/ticket/2" into the local branch "ticket/1".
            Added dependency on #2 to #1.
            sage: bob._UI.append("y")
            sage: bob.push()
            I will now change the branch field of ticket #1 from its current value "u/bob/branch1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
            Uploading your dependencies for ticket #1: "" => "#2"
            sage: bob._sagedev._set_dependencies_for_ticket(1,())
            sage: bob._UI.append("keep")
            sage: bob.push()
            According to trac, ticket #1 depends on #2. Your local branch depends on no tickets. Do you want to upload your dependencies to trac? Or do you want to download the dependencies from trac to your local branch? Or do you want to keep your local dependencies and the dependencies on trac in its current state? [upload/download/keep] keep
            sage: bob._UI.append("download")
            sage: bob.push()
            According to trac, ticket #1 depends on #2. Your local branch depends on no tickets. Do you want to upload your dependencies to trac? Or do you want to download the dependencies from trac to your local branch? Or do you want to keep your local dependencies and the dependencies on trac in its current state? [upload/download/keep] download
            sage: bob.push()
            self._UI.error("Cannot push while in detached HEAD state.")
            raise OperationCancelledError("cannot push while in detached HEAD state")
                if user_confirmation or self._UI.confirm('You are trying to push the branch "{0}" to "{1}" for ticket #{2}. However, your local branch for ticket #{2} seems to be "{3}". Do you really want to proceed?'.format(branch, remote_branch, ticket, self._local_branch_for_ticket(ticket)), default=False):
                    self._UI.info('To permanently set the branch associated to ticket #{0} to "{1}", use "{2}".'.format(ticket, branch, self._format_command("checkout",ticket=ticket,branch=branch)))
                if user_confirmation or self._UI.confirm('You are trying to push the branch "{0}" to "{1}" for ticket #{2}. However, that branch is associated to ticket #{3}. Do you really want to proceed?'.format(branch, remote_branch, ticket, self._ticket_for_local_branch(branch))):
                    self._UI.info('To permanently set the branch associated to ticket #{0} to "{1}", use "{2}". To create a new branch from "{1}" for #{0}, use "{3}" and "{4}".'.format(ticket, branch, self._format_command("checkout",ticket=ticket,branch=branch), self._format_command("checkout",ticket=ticket), self._format_command("merge", branch=branch)))
        self._UI.info('Pushing your changes in "{0}" to "{1}".'.format(branch, remote_branch))
                if not self._UI.confirm('The branch "{0}" does not exist on the remote server yet. Do you want to create the branch?'.format(remote_branch), default=True):
                self.git.super_silent.fetch(self.git._repository_anonymous, remote_branch)
                    self._UI.error('Not pushing your changes because they would discard some of the commits on the remote branch "{0}".'.format(remote_branch))
                    self._UI.info('If this is really what you want, use "{0}" to push your changes.'.format(self._format_command("push",ticket=ticket,remote_branch=remote_branch,force=True)))
                self._UI.info('Not pushing your changes because the remote branch "{0}" is idential to your local branch "{1}". Did you forget to commit your changes with "{2}"?'.format(remote_branch, branch, self._format_command("commit")))
                            if not self._UI.confirm('I will now push the following new commits to the remote branch "{0}":\n{1}Is this what you want?'.format(remote_branch, commits), default=True):
                    self._upload_ssh_key() # make sure that we have access to the repository
            self._UI.info('Your changes in "{0}" have been pushed to "{1}".'.format(branch, remote_branch))
            self._UI.info("Did not push any changes.")
                self._UI.info('Not setting the branch field for ticket #{0} because it already points to your branch "{1}".'.format(ticket, remote_branch))
                self._UI.info('Setting the branch field of ticket #{0} to "{1}".'.format(ticket, remote_branch))
                    self.git.super_silent.fetch(self.git._repository_anonymous, current_remote_branch)
                        self._UI.error('Not setting the branch field for ticket #{0} to "{1}" because "{1}" and the current value of the branch field "{2}" have diverged.'.format(ticket, remote_branch, current_remote_branch))
                        self._UI.info('If you really want to overwrite the branch field use "{0}". Otherwise, you need to merge in the changes introduced by "{2}" by using "{1}".'.format(self._format_command("push",ticket=ticket,remote_branch=remote_branch,force=True), self._format_command("download", ticket=ticket), current_remote_branch))
                    if not self._UI.confirm('I will now change the branch field of ticket #{0} from its current value "{1}" to "{2}". Is this what you want?'.format(ticket, current_remote_branch, remote_branch), default=True):
        if ticket and self._has_ticket_for_local_branch(branch):
            old_dependencies_ = self.trac.dependencies(ticket)
            old_dependencies = ", ".join(["#"+str(dep) for dep in old_dependencies_])
            new_dependencies_ = self._dependencies_for_ticket(self._ticket_for_local_branch(branch))
            new_dependencies = ", ".join(["#"+str(dep) for dep in new_dependencies_])

            upload = True
                if old_dependencies:
                    sel = self._UI.select("According to trac, ticket #{0} depends on {1}. Your local branch depends on {2}. Do you want to upload your dependencies to trac? Or do you want to download the dependencies from trac to your local branch? Or do you want to keep your local dependencies and the dependencies on trac in its current state?".format(ticket,old_dependencies,new_dependencies or "no tickets"),options=("upload","download","keep"))
                    if sel == "keep":
                        upload = False
                    elif sel == "download":
                        self._set_dependencies_for_ticket(ticket, old_dependencies_)
                        self._UI.info("Setting dependencies for #{0} to {1}.".format(ticket, old_dependencies))
                        upload = False
                    elif sel == "upload":
                        pass
                    else:
                        raise NotImplementedError
            else:
                self._UI.info("Not uploading your dependencies for ticket #{0} because the dependencies on trac are already up-to-date.".format(ticket))
                upload = False

            if upload:
                self._UI.show('Uploading your dependencies for ticket #{0}: "{1}" => "{2}"'.format(ticket, old_dependencies, new_dependencies))
                # Don't send an e-mail notification
    def reset_to_clean_state(self, cancel_unless_clean=True):
        INPUT:

        - ``cancel_unless_clean`` -- a boolean (default: ``True``), whether to
          raise an :class:`user_interface_error.OperationCancelledError` if the
          directory remains in an unclean state; used internally.

            sage: dev._wrap("reset_to_clean_state")
            Your repository is in an unclean state. It seems you are in the middle of a merge of some sort. To complete this command you have to reset your repository to a clean state. Do you want me to reset your repository? (This will discard many changes which are not commited.) [yes/No] n
            Your repository is in an unclean state. It seems you are in the middle of a merge of some sort. To complete this command you have to reset your repository to a clean state. Do you want me to reset your repository? (This will discard many changes which are not commited.) [yes/No] y
        if not self._UI.confirm("Your repository is in an unclean state. It seems you are in the middle of a merge of some sort. {0}Do you want me to reset your repository? (This will discard many changes which are not commited.)".format("To complete this command you have to reset your repository to a clean state. " if cancel_unless_clean else ""), default=False):
            if not cancel_unless_clean:
                return
    def clean(self, cancel_unless_clean=True):
        INPUT:

        - ``cancel_unless_clean`` -- a boolean (default: ``True``), whether to
          raise an :class:`user_interface_error.OperationCancelledError` if the
          directory remains in an unclean state; used internally.

            sage: dev.clean()
            sage: dev.clean()
            sage: dev.clean()
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? Your command can only be completed if you discard or stash your changes. [discard/Keep/stash] discard
            sage: dev.clean()
            sage: dev.clean()
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? Your command can only be completed if you discard or stash your changes. [discard/Keep/stash] keep
            sage: dev.clean()
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? Your command can only be completed if you discard or stash your changes. [discard/Keep/stash] stash
            Your changes have been recorded on a new branch "stash/1".
            sage: dev.clean()
            self.reset_to_clean_state(cancel_unless_clean)
        sel = self._UI.select("The following files in your working directory contain uncommitted changes:\n{0}\nDo you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later?{1}".format(files, " Your command can only be completed if you discard or stash your changes." if cancel_unless_clean else ""), options=('discard','keep','stash'), default=1)
            if cancel_unless_clean:
                raise OperationCancelledError("User requested not to clean the working directory.")
                        self._UI.info('Creating a new branch "{0}" which contains your stashed changes.'.format(branch))
                        self._UI.info('Committing your changes to "{0}".'.format(branch))
                        self.git.super_silent.commit('-a', message="Changes stashed by clean()")
                        self.git.super_silent.branch("-D", branch)
            self._UI.show('Your changes have been recorded on a new branch "{0}".'.format(branch))
            self._UI.info('To recover your changes later use "{1}".'.format(branch, self._format_command("unstash",branch=branch)))
            raise NotImplementedError
    def unstash(self, branch=None, show_diff=False):
        - ``show_diff`` -- if ``True``, shows the diff stored in the
          stash rather than applying it.

            sage: dev.clean()
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? Your command can only be completed if you discard or stash your changes. [discard/Keep/stash] s
            Your changes have been recorded on a new branch "stash/1".
            sage: dev.clean()
            Do you want me to discard any changes which are not committed? Should the changes be kept? Or do you want to stash them for later? Your command can only be completed if you discard or stash your changes. [discard/Keep/stash] s
            Your changes have been recorded on a new branch "stash/2".
        See what's in a stash::

            sage: dev.unstash("stash/1", show_diff=True)
            diff --git a/tracked b/tracked
            new file mode 100644
            index 0000000...
            --- /dev/null
            +++ b/tracked
            @@ -0,0 +1 @@
            +foo
            \ No newline at end of file

            sage: UI.append("y")
            The changes recorded in "stash/1" have been restored in your working directory.  Would you like to delete the branch they were stashed in? [Yes/no] y
            ValueError: "HEAD" is not a valid name for a stash.
            The changes recorded in "stash/2" do not apply cleanly to your working directory.
            self._UI.info('Use "{0}" to apply the changes recorded in the stash to your working directory, or "{1}" to see the changes recorded in the stash, where "name" is one of the following.'.format(self._format_command("unstash", branch="name"), self._format_command("unstash",branch="name",show_diff=True), stashes))
        elif show_diff:
            self.git.echo.diff(branch + '^..' + branch)
            return
            try:
                self.git.super_silent.cherry_pick(branch, no_commit=True)
            finally:
                self.git.super_silent.reset()
            self._UI.error('The changes recorded in "{0}" do not apply cleanly to your working directory.'.format(branch))
            self._UI.info('Some of your files now have conflict markers. You should resolve the changes manually or use "{0}" to reset to the last commit, but be aware that this command will undo any uncommitted changes'.format(self._format_command("clean")))
        if self._UI.confirm('The changes recorded in "{0}" have been restored in your working directory.  Would you like to delete the branch they were stashed in?'.format(branch), True):
            self.git.branch(branch, D=True)
            :meth:`create_ticket`, :meth:`comment`,
            :meth:`set_needs_review`, :meth:`set_needs_work`,
            :meth:`set_positive_review`, :meth:`set_needs_info`
            sage: dev.checkout(ticket=1)
    def needs_review(self, ticket=None, comment=''):
        r"""
        Set a ticket on trac to ``needs_review``.

        INPUT:

        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.

        - ``comment`` -- a comment to go with the status change.

        .. SEEALSO::

            :meth:`edit_ticket`, :meth:`set_needs_work`,
            :meth:`set_positive_review`, :meth:`comment`,
            :meth:`set_needs_info`

        TESTS:

        Set up a single user for doctesting::

            sage: from sage.dev.test.sagedev import single_user_setup
            sage: dev, config, UI, server = single_user_setup()

        Create a ticket and set it to needs_review::

            sage: UI.append("Summary: summary1\ndescription")
            sage: dev.create_ticket()
            1
            sage: dev.checkout(ticket=1)
            sage: open("tracked", "w").close()
            sage: dev.git.super_silent.add("tracked")
            sage: dev.git.super_silent.commit(message="alice: added tracked")
            sage: dev._UI.append("y")
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: dev.needs_review(comment='Review my ticket!')
            sage: dev.trac._get_attributes(1)['status']
            'needs_review'
        """
        if ticket is None:
            ticket = self._current_ticket()
        if ticket is None:
            raise SageDevValueError("ticket must be specified if not currently on a ticket.")
        self._check_ticket_name(ticket, exists=True)
        self.trac.set_attributes(ticket, comment, notify=True, status='needs_review')
        self._UI.info("Ticket #%s marked as needing review"%ticket)

    def needs_work(self, ticket=None, comment=''):
        r"""
        Set a ticket on trac to ``needs_work``.

        INPUT:

        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.

        - ``comment`` -- a comment to go with the status change.

        .. SEEALSO::

            :meth:`edit_ticket`, :meth:`set_needs_review`,
            :meth:`set_positive_review`, :meth:`comment`,
            :meth:`set_needs_info`

        TESTS:

        Create a doctest setup with two users::

            sage: from sage.dev.test.sagedev import two_user_setup
            sage: alice, config_alice, bob, config_bob, server = two_user_setup()

        Alice creates a ticket and set it to needs_review::

            sage: alice._chdir()
            sage: alice._UI.append("Summary: summary1\ndescription")
            sage: alice.create_ticket()
            1
            sage: alice.checkout(ticket=1)
            sage: open("tracked", "w").close()
            sage: alice.git.super_silent.add("tracked")
            sage: alice.git.super_silent.commit(message="alice: added tracked")
            sage: alice._UI.append("y")
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.needs_review(comment='Review my ticket!')

        Bob reviews the ticket and finds it lacking::

            sage: bob._chdir()
            sage: bob.checkout(ticket=1)
            sage: bob.needs_work(comment='Need to add an untracked file!')
            sage: bob.trac._get_attributes(1)['status']
            'needs_work'
        """
        if ticket is None:
            ticket = self._current_ticket()
        if ticket is None:
            raise SageDevValueError("ticket must be specified if not currently on a ticket.")
        self._check_ticket_name(ticket, exists=True)
        if not comment:
            comment = self._UI.get_input("Please add a comment for the author:")
        self.trac.set_attributes(ticket, comment, notify=True, status='needs_work')
        self._UI.info("Ticket #%s marked as needing work"%ticket)

    def needs_info(self, ticket=None, comment=''):
        r"""
        Set a ticket on trac to ``needs_info``.

        INPUT:

        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.

        - ``comment`` -- a comment to go with the status change.

        .. SEEALSO::

            :meth:`edit_ticket`, :meth:`needs_review`,
            :meth:`positive_review`, :meth:`comment`,
            :meth:`needs_work`

        TESTS:

        Create a doctest setup with two users::

            sage: from sage.dev.test.sagedev import two_user_setup
            sage: alice, config_alice, bob, config_bob, server = two_user_setup()

        Alice creates a ticket and set it to needs_review::

            sage: alice._chdir()
            sage: alice._UI.append("Summary: summary1\ndescription")
            sage: alice.create_ticket()
            1
            sage: alice.checkout(ticket=1)
            sage: open("tracked", "w").close()
            sage: alice.git.super_silent.add("tracked")
            sage: alice.git.super_silent.commit(message="alice: added tracked")
            sage: alice._UI.append("y")
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.needs_review(comment='Review my ticket!')

        Bob reviews the ticket and finds it lacking::

            sage: bob._chdir()
            sage: bob.checkout(ticket=1)
            sage: bob.needs_info(comment='Why is a tracked file enough?')
            sage: bob.trac._get_attributes(1)['status']
            'needs_info'
        """
        if ticket is None:
            ticket = self._current_ticket()
        if ticket is None:
            raise SageDevValueError("ticket must be specified if not currently on a ticket.")
        self._check_ticket_name(ticket, exists=True)
        if not comment:
            comment = self._UI.get_input("Please specify what information is required from the author:")
        self.trac.set_attributes(ticket, comment, notify=True, status='needs_info')
        self._UI.info("Ticket #%s marked as needing info"%ticket)

    def positive_review(self, ticket=None, comment=''):
        r"""
        Set a ticket on trac to ``positive_review``.

        INPUT:

        - ``ticket`` -- an integer or string identifying a ticket or
          ``None`` (default: ``None``), the number of the ticket to
          edit.  If ``None``, edit the :meth:`_current_ticket`.

        - ``comment`` -- a comment to go with the status change.

        .. SEEALSO::

            :meth:`edit_ticket`, :meth:`needs_review`,
            :meth:`needs_info`, :meth:`comment`,
            :meth:`needs_work`

        TESTS:

        Create a doctest setup with two users::

            sage: from sage.dev.test.sagedev import two_user_setup
            sage: alice, config_alice, bob, config_bob, server = two_user_setup()

        Alice creates a ticket and set it to needs_review::

            sage: alice._chdir()
            sage: alice._UI.append("Summary: summary1\ndescription")
            sage: alice.create_ticket()
            1
            sage: alice.checkout(ticket=1)
            sage: open("tracked", "w").close()
            sage: alice.git.super_silent.add("tracked")
            sage: alice.git.super_silent.commit(message="alice: added tracked")
            sage: alice._UI.append("y")
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: alice.needs_review(comment='Review my ticket!')

        Bob reviews the ticket and finds it good::

            sage: bob._chdir()
            sage: bob.checkout(ticket=1)
            sage: bob.positive_review()
            sage: bob.trac._get_attributes(1)['status']
            'positive_review'
        """
        if ticket is None:
            ticket = self._current_ticket()
        if ticket is None:
            raise SageDevValueError("ticket must be specified if not currently on a ticket.")
        self._check_ticket_name(ticket, exists=True)
        self.trac.set_attributes(ticket, comment, notify=True, status='positive_review')
        self._UI.info("Ticket #%s reviewed!"%ticket)

    def comment(self, ticket=None):
            sage: dev.checkout(ticket=1)
            sage: dev.comment()
            :meth:`edit_ticket`, :meth:`comment`,
            :meth:`sage.dev.trac_interface.TracInterface.show_ticket`,
            :meth:`sage.dev.trac_interface.TracInterface.show_comments`
            sage: dev.checkout(ticket=1)
            Your branch "ticket/1" has 0 commits.
        After pushing the local branch::
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            Your branch "ticket/1" has 0 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 0 commits. It does not differ from "ticket/1".
            Your branch "ticket/1" has 1 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 0 commits. "ticket/1" is ahead of "u/doctest/ticket/1" by 1 commits:
        Pushing them::
            sage: dev.push()
            I will now push the following new commits to the remote branch "u/doctest/ticket/1":
            Your branch "ticket/1" has 1 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 1 commits. It does not differ from "ticket/1".
            Your branch "ticket/1" has 0 commits.
            The trac ticket points to the branch "u/doctest/ticket/1" which has 1 commits. "u/doctest/ticket/1" is ahead of "ticket/1" by 1 commits:
            sage: dev.push(remote_branch="u/doctest/branch1", force=True)
            The branch "u/doctest/branch1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            Your branch "ticket/1" has 2 commits.
            The trac ticket points to the branch "u/doctest/branch1" which has 3 commits. "u/doctest/branch1" is ahead of "ticket/1" by 1 commits:
            Your remote branch "u/doctest/ticket/1" has 1 commits. The branches "u/doctest/ticket/1" and "ticket/1" have diverged.
            "u/doctest/ticket/1" is ahead of "ticket/1" by 1 commits:
            "ticket/1" is ahead of "u/doctest/ticket/1" by 2 commits:
        self._is_master_uptodate(action_if_not="warning")

                return 'It does not differ from "{0}".'.format(b)
                return '"{0}" is ahead of "{1}" by {2} commits:\n{3}'.format(a,b,len(b_to_a), "\n".join(b_to_a))
                return '"{0}" is ahead of "{1}" by {2} commits:\n{3}'.format(b,a,len(a_to_b),"\n".join(a_to_b))
                return 'The branches "{0}" and "{1}" have diverged.\n"{0}" is ahead of "{1}" by {2} commits:\n{3}\n"{1}" is ahead of "{0}" by {4} commits:\n{5}'.format(a,b,len(b_to_a),"\n".join(b_to_a),len(a_to_b),"\n".join(a_to_b))
        merge_base_local = None
            merge_base_local = self.git.merge_base(MASTER_BRANCH, branch).splitlines()[0]
            master_to_branch = commits(merge_base_local, branch)
            local_summary = 'Your branch "{0}" has {1} commits.'.format(branch, len(master_to_branch))
                ticket_summary = 'The trac ticket points to the branch "{0}" which does not exist.'
                self.git.super_silent.fetch(self.git._repository_anonymous, ticket_branch)
                merge_base_ticket = self.git.merge_base(MASTER_BRANCH, 'FETCH_HEAD').splitlines()[0]
                master_to_ticket = commits(merge_base_ticket, 'FETCH_HEAD')
                ticket_summary = 'The trac ticket points to the' \
                    ' branch "{0}" which has {1} commits.'.format(ticket_branch, len(master_to_ticket))
                if branch is not None:
                    if merge_base_local != merge_base_ticket:
                        ticket_summary += ' The branch can not be compared to your local' \
                            ' branch "{0}" because the branches are based on different versions' \
                            ' of sage (i.e. the "master" branch).'
                    else:
            self.git.super_silent.fetch(self.git._repository_anonymous, remote_branch)
            merge_base_remote = self.git.merge_base(MASTER_BRANCH, 'FETCH_HEAD').splitlines()[0]
            master_to_remote = commits(merge_base_remote, 'FETCH_HEAD')
            remote_summary = 'Your remote branch "{0}" has {1} commits.'.format(
                remote_branch, len(master_to_remote))
            if branch is not None:
                if merge_base_remote != merge_base_local:
                    remote_summary += ' The branch can not be compared to your local' \
                        ' branch "{0}" because the branches are based on different version' \
                        ' of sage (i.e. the "master" branch).'
                else:
            sage: dev.checkout(ticket=1)
                : master
            * #1: ticket/1 summary
                : master
            * #1: ticket/1 summary
            Can not delete "ticket/1" because you are currently on that branch.
            Moved your branch "ticket/1" to "trash/ticket/1".
            - :meth:`prune_closed_tickets` -- abandon tickets that have
              been closed.
            - :meth:`local_tickets` -- list local non-abandoned tickets.
            sage: dev.checkout(ticket=1)
            sage: UI.append("y")
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server
            yet. Do you want to create the branch? [Yes/no] y
            Can not delete "ticket/1" because you are currently on that branch.
            Moved your branch "ticket/1" to "trash/ticket/1".
        Start to work on a new branch for this ticket::

            sage: from sage.dev.sagedev import MASTER_BRANCH
            sage: UI.append("y")
            sage: dev.checkout(ticket=1, base=MASTER_BRANCH)
            Creating a new branch for #1 based on "master". The trac ticket for #1
            already refers to the branch "u/doctest/ticket/1". As you are creating
            a new branch for that ticket, it seems that you want to ignore the work
            that has already been done on "u/doctest/ticket/1" and start afresh. Is
            this what you want? [yes/No] y
                raise SageDevValueError("Can not abandon #{0}. You have no local branch for this ticket."
                                        .format(ticket))
                if not self._UI.confirm('I will delete your local branch "{0}". Is this what you want?'
                                        .format(branch), default=False):
                    self._UI.error('Can not delete "{0}" because you are currently on that branch.'
                                   .format(branch))
                    self._UI.info('Use "{0}" to move to a different branch.'
                                  .format(self._format_command("vanilla")))
            self._UI.show('Moved your branch "{0}" to "{1}".'
                          .format(branch, new_branch))
            self._set_dependencies_for_ticket(ticket, None)
            self._UI.info('If you want to work on #{0} starting from a fresh copy of the master branch, use "{1}".'
                          .format(ticket, self._format_command("checkout",ticket=ticket,base=MASTER_BRANCH)))
            - :meth:`merge` -- merge into the current branch rather
              than creating a new one
            sage: dev.checkout(ticket=1)
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server
            yet. Do you want to create the branch? [Yes/no] y
            self.clean()
        self._UI.info('Creating a new branch "{0}".'.format(branch))
                self._UI.info('Merging {2} branch "{0}" into "{1}".'
                              .format(branch_name, branch, local_remote))
                self.merge(branch, pull=local_remote=="remote")
            self._UI.info('Deleted branch "{0}".'.format(branch))
    def merge(self, ticket_or_branch=MASTER_BRANCH, pull=None, create_dependency=None):
          ticket, if ``pull`` is ``False``), for the name of a local or
          dependencies are merged in one by one.
        - ``pull`` -- a boolean or ``None`` (default: ``None``); if
          ``ticket_or_branch`` identifies a ticket, whether to pull the
          ``ticket_or_branch`` is a branch name, then ``pull`` controls
          whether it should be interpreted as a remote branch (``True``) or as
          a local branch (``False``). If it is set to ``None``, then it will
          take ``ticket_or_branch`` as a remote branch if it exists, and as a
          local branch otherwise.
            the remote server during :meth:`push` and :meth:`pull`.
            - :meth:`show_dependencies` -- see the current
              dependencies.
            - :meth:`GitInterface.merge` -- git's merge command has
              more options and can merge multiple branches at once.
            - :meth:`gather` -- creates a new branch to merge into
              rather than merging into the current branch.
        TESTS:
            sage: alice.checkout(ticket=1)
            sage: alice.checkout(ticket=2)
            sage: alice.checkout(ticket=1)
            sage: alice.push()
            The branch "u/alice/ticket/1" does not exist on the remote server
            yet. Do you want to create the branch? [Yes/no] y
            sage: alice.checkout(ticket=2)
            sage: alice.merge("#1", pull=False)
            Merging the local branch "ticket/1" into the local branch "ticket/2".
        Check that merging dependencies works::

            sage: alice.merge("dependencies")
            Merging the remote branch "u/alice/ticket/1" into the local branch "ticket/2".

            Merging the local branch "ticket/1" into the local branch "ticket/2".
        A remote branch for a local branch is only merged in if ``pull`` is set::
            Merging the local branch "ticket/1" into the local branch "ticket/2".
            sage: alice.merge("ticket/1", pull=True)
            ValueError: Branch "ticket/1" does not exist on the remote system.
            sage: bob.checkout(ticket=1)
            sage: bob.push()
            The branch "u/bob/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            I will now change the branch field of ticket #1 from its current value "u/alice/ticket/1" to "u/bob/ticket/1". Is this what you want? [Yes/no] y
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/2".
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] abort
            Merging the remote branch "u/bob/ticket/1" into the local branch "ticket/2".
            Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge. [resolved/abort] resolved
        We cannot merge a ticket into itself::

            sage: alice.merge(2)
            ValueError: cannot merge a ticket into itself
            self.clean()
            self._UI.error('You are currently not on any branch. Use "{0}" to checkout a branch.'.format(self._format_command("checkout")))
        if ticket_or_branch == 'dependencies':
            if current_ticket == None:
                raise SageDevValueError("dependencies can only be merged if currently on a ticket.")
            if pull == False:
                raise SageDevValueError('"pull" must not be "False" when merging dependencies.')
            if create_dependency != None:
                raise SageDevValueError('"create_dependency" must not be set when merging dependencies.')
            for dependency in self._dependencies_for_ticket(current_ticket):
                self._UI.info("Merging dependency #{0}.".format(dependency))
                self.merge(ticket_or_branch=dependency, pull=True)
            return
        elif self._is_ticket_name(ticket_or_branch):
            if ticket == current_ticket:
                raise SageDevValueError("cannot merge a ticket into itself")
            if pull is None:
                pull = True
            if pull:
        elif pull == False or (pull is None and not self._is_remote_branch_name(ticket_or_branch, exists=True)):
            # ticket_or_branch should be interpreted as a local branch name
            self._check_local_branch_name(branch, exists=True)
            pull = False
            if create_dependency == True:
                if self._has_ticket_for_local_branch(branch):
                    ticket = self._ticket_for_local_branch(branch)
                else:
                    raise SageDevValueError('"create_dependency" must not be "True" if "ticket_or_branch" is a local branch which is not associated to a ticket.')
            # ticket_or_branch should be interpreted as a remote branch name
            self._check_remote_branch_name(remote_branch, exists=True)
            pull = True
                raise SageDevValueError('"create_dependency" must not be "True" if "ticket_or_branch" is a local branch.')
            create_dependency = False
        if pull:
                self._UI.error('Can not merge remote branch "{0}". It does not exist.'
                               .format(remote_branch))
            self._UI.show('Merging the remote branch "{0}" into the local branch "{1}".'
                          .format(remote_branch, current_branch))
            self.git.super_silent.fetch(self.git._repository_anonymous, remote_branch)
            self._UI.show('Merging the local branch "{0}" into the local branch "{1}".'
                          .format(branch, current_branch))
            local_merge_branch = branch
                lines.append('Please fix conflicts in the affected files (in a different terminal) and type "resolved". Or type "abort" to abort the merge.')
                if self._UI.select("\n".join(lines), ['resolved', 'abort']) == 'resolved':
                self._UI.info("Not recording dependency on #{0} because #{1} already depends on #{0}."
                              .format(ticket, current_ticket))
    def local_tickets(self, include_abandoned=False, cached=True):
        - ``cached`` -- boolean (default: ``True``), whether to try to pull the
          summaries from the ticket cache; if ``True``, then the summaries
          might not be accurate if they changed since they were last updated.
          To update the summaries, set this to ``False``.

            - :meth:`abandon_ticket` -- hide tickets from this method.
            - :meth:`remote_status` -- also show status compared to
              the trac server.
            - :meth:`current_ticket` -- get the current ticket.
            * : master
            sage: dev.checkout(ticket=1)
            sage: dev.checkout(ticket=2)
                : master
              #1: ticket/1 summary
            * #2: ticket/2 summary
        from git_error import DetachedHeadError
        try:
            current_branch = self.git.current_branch()
        except DetachedHeadError:
            current_branch = None
        ret = []
        for branch in branches:
            ticket = None
            ticket_summary = ""
            extra = " "
            if self._has_ticket_for_local_branch(branch):
                ticket = self._ticket_for_local_branch(branch)
                try:
                    try:
                        ticket_summary = self.trac._get_attributes(ticket, cached=cached)['summary']
                    except KeyError:
                        ticket_summary = self.trac._get_attributes(ticket, cached=False)['summary']
                except TracConnectionError:
                    ticket_summary = ""
            if current_branch == branch:
                extra = "*"
            ret.append(("{0:>7}: {1} {2}".format("#"+str(ticket) if ticket else "", branch, ticket_summary), extra))
        while all([info.startswith(' ') for (info, extra) in ret]):
            ret = [(info[1:],extra) for (info, extra) in ret]
        ret = sorted(ret)
        ret = ["{0} {1}".format(extra,info) for (info,extra) in ret]
        self._UI.show("\n".join(ret))

    def vanilla(self, release=MASTER_BRANCH):
        Return to a clean version of Sage.
        - ``release`` -- a string or decimal giving the release name (default:
          ``'master'``).  In fact, any tag, commit or branch will work.  If the
          tag does not exist locally an attempt to fetch it from the server
          will be made.
            - :meth:`checkout` -- checkout another branch, ready to
              develop on it.
            - :meth:`pull` -- pull a branch from the server and merge
              it.
        release = str(release)
            self.clean()
            self._UI.error("Cannot checkout a release while your working directory is not clean.")
                self.git.super_silent.fetch(self.git._repository_anonymous, release)
                self._UI.error('"{0}" does not exist locally or on the remote server.'.format(release))
            - :meth:`commit` -- record changes into the repository.
            - :meth:`local_tickets` -- list local tickets (you may
              want to commit your changes to a branch other than the
              current one).
            sage: dev.checkout(ticket=1)
            sage: dev.push()
            The branch "u/doctest/ticket/1" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: dev.checkout(ticket=2)
            sage: dev.push()
            The branch "u/doctest/ticket/2" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            sage: dev.checkout(ticket=3)
            sage: dev.push()
            The branch "u/doctest/ticket/3" does not exist on the remote server yet. Do you want to create the branch? [Yes/no] y
            Merging the remote branch "u/doctest/ticket/1" into the local branch "ticket/3".
            Merging the remote branch "u/doctest/ticket/2" into the local branch "ticket/3".
            sage: dev.checkout(ticket="#1")
            sage: dev.checkout(ticket="#2")
            sage: dev.push()
            I will now push the following new commits to the remote
            branch "u/doctest/ticket/2":
            sage: dev.checkout(ticket="#3")
            sage: dev.push()
            I will now push the following new commits to the remote branch "u/doctest/ticket/3":
            Uploading your dependencies for ticket #3: "" => "#1, #2"