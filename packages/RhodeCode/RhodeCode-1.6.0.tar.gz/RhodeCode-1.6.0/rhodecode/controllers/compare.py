# -*- coding: utf-8 -*-
"""
    rhodecode.controllers.compare
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    compare controller for pylons showing differences between two
    repos, branches, bookmarks or tips

    :created_on: May 6, 2012
    :author: marcink
    :copyright: (C) 2010-2012 Marcin Kuzminski <marcin@python-works.com>
    :license: GPLv3, see COPYING for more details.
"""
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
import traceback

from webob.exc import HTTPNotFound
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.i18n.translation import _

from rhodecode.lib.vcs.exceptions import EmptyRepositoryError, RepositoryError
from rhodecode.lib import helpers as h
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.lib.auth import LoginRequired, HasRepoPermissionAnyDecorator
from rhodecode.lib import diffs

from rhodecode.model.db import Repository
from rhodecode.model.pull_request import PullRequestModel
from webob.exc import HTTPBadRequest
from rhodecode.lib.diffs import LimitedDiffContainer
from rhodecode.lib.vcs.backends.base import EmptyChangeset

log = logging.getLogger(__name__)


class CompareController(BaseRepoController):

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def __before__(self):
        super(CompareController, self).__before__()

    def __get_cs_or_redirect(self, rev, repo, redirect_after=True,
                             partial=False):
        """
        Safe way to get changeset if error occur it redirects to changeset with
        proper message. If partial is set then don't do redirect raise Exception
        instead

        :param rev: revision to fetch
        :param repo: repo instance
        """

        try:
            type_, rev = rev
            return repo.scm_instance.get_changeset(rev)
        except EmptyRepositoryError, e:
            if not redirect_after:
                return None
            h.flash(h.literal(_('There are no changesets yet')),
                    category='warning')
            redirect(url('summary_home', repo_name=repo.repo_name))

        except RepositoryError, e:
            log.error(traceback.format_exc())
            h.flash(str(e), category='warning')
            if not partial:
                redirect(h.url('summary_home', repo_name=repo.repo_name))
            raise HTTPBadRequest()

    def index(self, org_ref_type, org_ref, other_ref_type, other_ref):
        # org_ref will be evaluated in org_repo
        org_repo = c.rhodecode_db_repo.repo_name
        org_ref = (org_ref_type, org_ref)
        # other_ref will be evaluated in other_repo
        other_ref = (other_ref_type, other_ref)
        other_repo = request.GET.get('other_repo', org_repo)
        # If merge is True:
        #   Show what org would get if merged with other:
        #   List changesets that are ancestors of other but not of org.
        #   New changesets in org is thus ignored.
        #   Diff will be from common ancestor, and merges of org to other will thus be ignored.
        # If merge is False:
        #   Make a raw diff from org to other, no matter if related or not.
        #   Changesets in one and not in the other will be ignored
        merge = bool(request.GET.get('merge'))
        # fulldiff disables cut_off_limit
        c.fulldiff = request.GET.get('fulldiff')
        # partial uses compare_cs.html template directly
        partial = request.environ.get('HTTP_X_PARTIAL_XHR')
        # as_form puts hidden input field with changeset revisions
        c.as_form = partial and request.GET.get('as_form')
        # swap url for compare_diff page - never partial and never as_form
        c.swap_url = h.url('compare_url',
            repo_name=other_repo,
            org_ref_type=other_ref[0], org_ref=other_ref[1],
            other_repo=org_repo,
            other_ref_type=org_ref[0], other_ref=org_ref[1],
            merge=merge or '')

        org_repo = Repository.get_by_repo_name(org_repo)
        other_repo = Repository.get_by_repo_name(other_repo)

        if org_repo is None:
            log.error('Could not find org repo %s' % org_repo)
            raise HTTPNotFound
        if other_repo is None:
            log.error('Could not find other repo %s' % other_repo)
            raise HTTPNotFound

        if org_repo != other_repo and h.is_git(org_repo):
            log.error('compare of two remote repos not available for GIT REPOS')
            raise HTTPNotFound

        if org_repo.scm_instance.alias != other_repo.scm_instance.alias:
            log.error('compare of two different kind of remote repos not available')
            raise HTTPNotFound

        self.__get_cs_or_redirect(rev=org_ref, repo=org_repo, partial=partial)
        self.__get_cs_or_redirect(rev=other_ref, repo=other_repo, partial=partial)

        c.org_repo = org_repo
        c.other_repo = other_repo
        c.org_ref = org_ref[1]
        c.other_ref = other_ref[1]
        c.org_ref_type = org_ref[0]
        c.other_ref_type = other_ref[0]

        c.cs_ranges, c.ancestor = PullRequestModel().get_compare_data(
            org_repo, org_ref, other_repo, other_ref, merge)

        c.statuses = c.rhodecode_db_repo.statuses([x.raw_id for x in
                                                   c.cs_ranges])
        if partial:
            assert c.ancestor
            return render('compare/compare_cs.html')

        if c.ancestor:
            assert merge
            # case we want a simple diff without incoming changesets,
            # previewing what will be merged.
            # Make the diff on the other repo (which is known to have other_ref)
            log.debug('Using ancestor %s as org_ref instead of %s'
                      % (c.ancestor, org_ref))
            org_ref = ('rev', c.ancestor)
            org_repo = other_repo

        diff_limit = self.cut_off_limit if not c.fulldiff else None

        _diff = diffs.differ(org_repo, org_ref, other_repo, other_ref)

        diff_processor = diffs.DiffProcessor(_diff or '', format='gitdiff',
                                             diff_limit=diff_limit)
        _parsed = diff_processor.prepare()

        c.limited_diff = False
        if isinstance(_parsed, LimitedDiffContainer):
            c.limited_diff = True

        c.files = []
        c.changes = {}
        c.lines_added = 0
        c.lines_deleted = 0
        for f in _parsed:
            st = f['stats']
            if st[0] != 'b':
                c.lines_added += st[0]
                c.lines_deleted += st[1]
            fid = h.FID('', f['filename'])
            c.files.append([fid, f['operation'], f['filename'], f['stats']])
            diff = diff_processor.as_html(enable_comments=False, parsed_lines=[f])
            c.changes[fid] = [f['operation'], f['filename'], diff]

        return render('compare/compare_diff.html')
