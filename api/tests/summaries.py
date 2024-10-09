import pendulum

from api.tests.test import TestCase
from django.core.management import call_command


class SummaryTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/summaries.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pendulum.set_test_now(pendulum.datetime(2020, 9, 29, 11, 00))

    def test_daily(self):
        call_command('send_summaries', 'daily')

        self.assertEmailEquals([
            {
                'subject': 'MBuild Daily Summary – Quality Issue Report: Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.brad+1@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/daily_client.html'
            },
            {
                'subject': 'MBuild Daily Summary – Quality Issue Report: Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.brad+2wood@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/daily_consultant.html'
            },
            {
                'subject': 'MBuild Daily Summary – Quality Issue Report: Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.brad+33wood@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/daily_consultant_other_company.html'
            },
            {
                'subject': 'MBuild – Quality Critical Task Daily Summary – Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.brad@gmail.com', 'cool.manager+17@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/daily_task_company_admin_manager_admin.html'
            },
            {
                'subject': 'MBuild Daily Summary - Rework & Defect Report: Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.brad@gmail.com', 'cool.manager+17@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/daily_quality_issues_subtasks_company_admin_manager_admin.html'
            },
            {
                'subject': 'MBuild Daily Summary - Rework & Defect Report: Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.sub+17@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/daily_subcontractor.html'
            }
        ])

    def test_weekly(self):
        call_command('send_summaries', 'weekly')

        self.assertEmailEquals([
            {
                'subject': 'MBuild Weekly Summary – Quality Issue Report: Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.brad+1@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/weekly_client.html'
            },
            {
                'subject': 'MBuild Weekly Summary – Quality Issue Report: Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.brad+2wood@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/weekly_consultant.html'
            },
            {
                'subject': 'MBuild Weekly Summary – Quality Issue Report: Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.brad+33wood@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/weekly_consultant_other_company.html'
            },
            {
                'subject': 'MBuild – Quality Critical Task Weekly Summary – Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.brad@gmail.com', 'cool.manager+17@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/weekly_task_company_admin_manager_admin.html'
            },
            {
                'subject': 'MBuild Weekly Summary - Rework & Defect Report: Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.brad@gmail.com', 'cool.manager+17@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/weekly_quality_issues_subtasks_company_admin_manager_admin.html'
            },
            {
                'subject': 'MBuild Weekly Summary - Rework & Defect Report: Project 1',
                'from_email': 'MBuild Admin <admin@mbuild.global>',
                'to': ['cool.sub+17@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/summaries/weekly_subcontractor.html'
            }
        ])
