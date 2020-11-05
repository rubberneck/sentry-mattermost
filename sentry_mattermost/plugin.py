# Copyright (c) 2015 NDrive SA
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2

from sentry import tagstore
from sentry.plugins.bases import notify
from sentry_plugins.base import CorePluginMixin
from sentry.utils import json
from sentry.integrations import FeatureDescription, IntegrationFeatures

import sentry_mattermost


def get_rules(rules, group, project):
    rules_list = []
    for rule in rules:
        rules_list.append(rule.label.encode('utf-8'))
    return ', '.join('%s' % r for r in rules_list)


def get_tags(event):
    tag_list = event.get_tags()
    if not tag_list:
        return ()

    return ((tagstore.get_tag_key_label(k), tagstore.get_tag_value_label(k, v))
            for k, v in tag_list)


class PayloadFactory:
    @classmethod
    def render_text(cls, params):
        template = "__{project}__\n__[{title}]({link})__ \n{culprit}\n"
        return template.format(**params)

    @classmethod
    def create(cls, plugin, event, rules):
        group = event.group
        project = group.project

        if group.culprit:
            culprit = group.culprit.encode("utf-8")
        else:
            culprit = None
        project_name = project.get_full_name().encode("utf-8")

        params = {
            "title": group.message_short.encode('utf-8'),
            "link": group.get_absolute_url(),
            "culprit": culprit,
            "project": project_name
        }

        if plugin.get_option('include_rules', project):
            params["rules"] = get_rules(rules, group, project)

        if plugin.get_option('include_tags', project):
            params["tags"] = get_tags(event)

        text = cls.render_text(params)

        payload = {
            "username": "Sentry",
            "icon_url": "https://myovchev.github.io/sentry-slack/images/logo32.png",  # noqa
            "text": text
        }
        return payload


def request(url, payload):
    data = "payload=" + json.dumps(payload)
    # Prevent servers from rejecting webhook calls by adding a existing user agent
    req = urllib2.Request(url, data, headers={'User-Agent' : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"})
    response = urllib2.urlopen(req)
    return response.read()


class Mattermost(CorePluginMixin, notify.NotificationPlugin):
    title = 'Mattermost'
    slug = 'mattermost'
    description = 'Enables notifications for Mattermost Open Source Chat'
    version = sentry_mattermost.VERSION
    author = 'Andre Freitas <andre.freitas@ndrive.com>, Guillaume Lastecoueres<px9e@gmx.fr>'
    author_url = 'https://github.com/Biekos/sentry-mattermost'
    required_field = "webhook"
    conf_key = "mattermost"

    feature_descriptions = [
        FeatureDescription(
            """
            Enables notifications for Mattermost Open Source Chat.  
            """,
            IntegrationFeatures.ALERT_RULE,
        )
    ]

    def get_config(self, project, **kwargs):
        return [
            {
                "name": "webhook",
                "label": "Webhook URL",
                "type": "url",
                "placeholder": "e.g. https://mattermost.example.com/hooks/00000000000000000",
                "required": True,
                "help": "Your custom mattermost webhook URL.",
            },
            {
                "name": "include_rules",
                "label": "Include Rules",
                "type": "bool",
                "required": False,
                "help": "Include rules with notifications.",
            },
            {
                "name": "include_tags",
                "label": "Include tags",
                "type": "bool",
                "required": False,
                "help": "Include tags with notifications."
            }]

    def is_configured(self, project):
        return bool(self.get_option("webhook", project))

    def notify_users(self, group, event, triggering_rules, fail_silently=False, **kwargs):
        project = event.group.project
        if not self.is_configured(project):
            return

        webhook = self.get_option('webhook', project)
        payload = PayloadFactory.create(self, event, triggering_rules)
        return request(webhook, payload)
