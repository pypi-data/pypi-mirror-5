#!/usr/bin/env python
"""Pivotal Tools

A collection of tools to help with your pivotal workflow


changelog
---------------
List out projects stories that are delivered or finished (not accepted)

show_stories
---------------
Lists all stories for a given project (will prompt you if not specified)
Can filter by user with the `for` option
By default show the top 20 stories, can specify more (or less) with the _number_ option

show_story
---------------
Show the details for a given story.  passing the project-index parameter will make it faster

browser_open
---------------
Will open the given story in a browser.  passing the project-index parameter will make it faster

scrum
---------------
Will list stories and bugs that team members are working on.  Grouped by team member

poker
---------------
Help to facilitate a planning poker session


Usage:
  pivotal_tools changelog [--project-index=<pi>]
  pivotal_tools show_stories [--project-index=<pi>] [--for=<user_name>] [--number=<number_of_stories>]
  pivotal_tools show_story <story_id> [--project-index=<pi>]
  pivotal_tools browser_open <story_id> [--project-index=<pi>]
  pivotal_tools scrum [--project-index=<pi>]
  pivotal_tools poker [--project-index=<pi>]

Options:
  -h --help             Show this screen.
  --for=<user_name>     Username, or initials
  --project-index=<pi>  If you have multiple projects, this is the index that the project shows up in my prompt
                        This is useful if you do not want to be prompted, and then you can pipe the output

"""

#Core Imports
import urllib2
from urllib import quote
import xml.etree.ElementTree as ET
import os
import webbrowser
from itertools import islice


#3rd Party Imports
from docopt import docopt
from termcolor import colored
import requests

TOKEN = os.getenv('PIVOTAL_TOKEN', None)


def _perform_pivotal_get(url):
    headers = {'X-TrackerToken': TOKEN}
    # print url
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response


def _perform_pivotal_put(url):
    headers = {'X-TrackerToken': TOKEN, 'Content-Length': 0}
    response = requests.put(url, headers=headers)
    response.raise_for_status()
    return response


def _parse_text(node, key):
    """parses test from an ElementTree node, if not found returns empty string"""
    element = node.find(key)
    if element is not None:
        text = element.text
        if text is not None:
            return text.strip()
        else:
            return ''
    else:
        return ''


def _parse_int(node, key):
    """parses an int from an ElementTree node, if not found returns None"""
    element = node.find(key)
    if element is not None:
        return int(element.text)
    else:
        return None


class Note(object):
    """object representation of a Pivotal Note, should be accessed from story.notes"""
    def __init__(self, note_id, text, author):
        self.note_id = note_id
        self.text = text
        self.author = author


class Attachment(object):
    """object representation of a Pivotal attachment, should be accessed from story.attachments"""
    def __init__(self, attachment_id, description, url):
        self.attachment_id = attachment_id
        self.description = description
        self.url = url


class Story(object):
    """object representation of a Pivotal story"""
    def __init__(self):
        self.story_id = None
        self.project_id = None
        self.name = None
        self.description = None
        self.owned_by = None
        self.story_type = None
        self.estimate = None
        self.state = None
        self.url = None
        self.labels = None
        self.notes = []
        self.attachments = []


    @property
    def first_label(self):
        """returns the first label if any from labels.  Used for grouping"""
        return self.labels.split(',')[0]

    @classmethod
    def from_node(cls, node):
        """instantiates a Story object from an elementTree node, build child notes and attachment lists"""

        story = Story()
        story.story_id = _parse_text(node, 'id')
        story.name = _parse_text(node, 'name')
        story.owned_by = _parse_text(node, 'owned_by')
        story.story_type = _parse_text(node, 'story_type')
        story.state = _parse_text(node, 'current_state')
        story.description = _parse_text(node, 'description')
        story.estimate = _parse_int(node, 'estimate')
        story.labels = _parse_text(node, 'labels')
        story.url = _parse_text(node, 'url')
        story.project_id = _parse_text(node, 'project_id')

        note_nodes = node.find('notes')
        if note_nodes is not None:
            for note_node in note_nodes:
                note_id = _parse_text(note_node, 'id')
                text = _parse_text(note_node, 'text')
                author = _parse_text(note_node, 'author')
                story.notes.append(Note(note_id, text, author))

        attachment_nodes = node.find('attachments')
        if attachment_nodes is not None:
            for attachment_node in attachment_nodes:
                attachment_id = _parse_text(attachment_node, 'id')
                description = _parse_text(attachment_node, 'text')
                url = _parse_text(attachment_node, 'url')
                story.attachments.append(Attachment(attachment_id,description,url))



        return story

    def assign_estimate(self, estimate):
        """changes the estimate of a story"""
        update_story_url ="http://www.pivotaltracker.com/services/v3/projects/{}/stories/{}?story[estimate]={}".format(self.project_id, self.story_id, estimate)
        response = _perform_pivotal_put(update_story_url)
        print response.text


class Project(object):
    """object representation of a Pivotal Project"""

    def __init__(self, project_id, name):
        self.project_id = project_id
        self.name = name

    @classmethod
    def load_project(cls, project_id):
        url = "http://www.pivotaltracker.com/services/v3/projects/%s" % project_id
        response = _perform_pivotal_get(url)

        project_node = ET.fromstring(response.text)
        name = _parse_text(project_node, 'name')
        return Project(project_id, name)

    def get_stories(self, filter_string):
        """Given a filter strong, returns an list of stories matching that filter.  If none will return an empty list
        Look at [link](https://www.pivotaltracker.com/help/faq#howcanasearchberefined) for syntax

        """

        story_filter = quote(filter_string, safe='')
        stories_url = "http://www.pivotaltracker.com/services/v3/projects/{}/stories?filter={}".format(self.project_id, story_filter)

        response = _perform_pivotal_get(stories_url)
        stories_root = ET.fromstring(response.text)

        return [Story.from_node(story_node) for story_node in stories_root]

    def unestimated_stories(self):
        stories = self.get_stories('type:feature state:unstarted')
        return [story for story in stories if int(story.estimate) == -1]

    def in_progress_stories(self):
        return self.get_stories('state:started,rejected')

    def finished_features(self):
        return self.get_stories('state:delivered,finished type:feature')

    def finished_bugs(self):
        return self.get_stories('state:delivered,finished type:bug')

    def known_issues(self):
        return self.get_stories('state:unscheduled,unstarted,started,rejected type:bug')


## Main Methods
def generate_changelog(project):
    """Generate a Changelog for the current project.  It is grouped into 3 sections:
    * New Features
    * Bugs Fixed
    * Known Issues

    The new features section is grouped by label for easy comprehension
    """

    title_string = 'Change Log {}'.format(project.name)

    print
    print bold(title_string)
    print bold('=' * len(title_string))
    print

    print bold('New Features')
    print bold('============')

    finished_features = project.finished_features()
    features_by_label = group_stories_by_label(finished_features)

    for label in features_by_label:
        print bold(label.title())
        for story in features_by_label[label]:
            print '    * {:14s} {}'.format('[{}]'.format(story.story_id), story.name)


    def print_stories(stories):
        if len(stories) > 0:
            for story in stories:
                story_string = ""
                if story.labels is not None and len(story.labels) > 0:
                    story_string += "[{}] ".format(story.labels)

                story_string += story.name
                print '* {:14s} {}'.format('[{}]'.format(story.story_id), story_string)
        else:
            print 'None'
            print


    print
    print bold('Bugs Fixed')
    print bold('==========')
    print_stories(project.finished_bugs())

    print
    print bold('Known Issues')
    print bold('==========')
    print_stories(project.known_issues())


def show_stories(project, arguments):
    """Shows the top stories
    By default it will show the top 20.  But that change be changed by the --number arguement
    You can further filter the list by passing the --for argument and pass the initials of the user
    """

    search_string = 'state:unscheduled,unstarted,rejected,started'
    if arguments['--for'] is not None:
        search_string += " owner:{}".format(arguments['--for'])

    stories_root = project.get_stories(search_string)

    number_of_stories = 20
    if arguments['--number'] is not None:
        number_of_stories = int(arguments['--number'])
    else:
        print
        print "Showing the top 20 stories, if you want to show more, specify number with the --number option"
        print


    if len(stories_root) == 0:
        print "None"
    else:
        for child in islice(stories_root, number_of_stories):
            story = Story.from_node(child)
            print '{:14s}{:4s}{:9s}{:13s}{:10s} {}'.format('#{}'.format(story.story_id),
                                                           initials(story.owned_by),
                                                           story.story_type,
                                                           story.state,
                                                           estimate_visual(story.estimate),
                                                           story.name)


def show_story(story_id, arguments):
    """Shows the Details for a single story

    Will find the associate project, then look up the story and print of the details
    """
    project = find_project_for_story(story_id, arguments)
    story_url = "http://www.pivotaltracker.com/services/v3/projects/{}/stories/{}".format(project.project_id, story_id)
    resposne = _perform_pivotal_get(story_url)
    # print resposne.text
    root = ET.fromstring(resposne.text)
    story = Story.from_node(root)

    print
    print colored('{:12s}{:4s}{:9s}{:10s} {}'.format('#{}'.format(story.story_id),
                                                     initials(story.owned_by),
                                                     story.story_type,
                                                     estimate_visual(story.estimate),
                                                     story.name), 'white', attrs=['bold'])
    print
    print colored("Story Url: ", 'white', attrs=['bold']) + colored(story.url, 'blue', attrs=['underline'])
    print colored("Description: ", 'white', attrs=['bold']) + story.description

    if len(story.notes) > 0:
        print
        print bold("Notes:")
        for note in story.notes:
            print "[{}] {}".format(initials(note.author), note.text)

    if len(story.attachments) > 0:
        print
        print bold("Attachments:")
        for attachment in story.attachments:
            print "{} {}".format(attachment.description, colored(attachment.url,'blue',attrs=['underline']))

    print


def scrum(project):
    """ CLI Visual Aid for running the daily SCRUM meeting.
        Prints an list of stories that people are working on grouped by user
    """

    stories = project.in_progress_stories()
    stories_by_owner = group_stories_by_owner(stories)

    print bold("{} SCRUM -- {}".format(project.name, pretty_date()))
    print

    for owner in stories_by_owner:
        print bold(owner)
        for story in stories_by_owner[owner]:
            print "   #{:12s}{:9s} {:7s} {}".format(story.story_id,
                                                    estimate_visual(story.estimate),
                                                    story.story_type,
                                                    story.name)

        print


def poker(project):
    """CLI driven tool to help facilitate the periodic poker planning session

    Will loop through and display unestimated stories, and prompt the team for an estimate.
    You can also open the current story in a browser for additional editing
    """

    total_stories = len(project.unestimated_stories())
    for idx, story in enumerate(project.unestimated_stories()):
        clear()
        rows, cols = _get_column_dimensions()
        print "{} PLANNING POKER SESSION [{}]".format(project.name.upper(), bold("{}/{} Stories Estimated".format(idx+1, total_stories)))
        print "-" * cols
        pretty_print_story(story)
        prompt_estimation(story)
    else:
        print "KaBoom!!! Nice Work Team"


def browser_open(story_id, arguments):
    """Open the given story in a browser"""

    project_id = find_project_for_story(story_id, arguments)
    story_url = "https://www.pivotaltracker.com/s/projects/{}/stories/{}".format(project_id, story_id)
    webbrowser.open(story_url)




def bold(string):
    return colored(string, 'white', attrs=['bold'])





def get_project_by_index(index):
    projects_url = 'http://www.pivotaltracker.com/services/v3/projects'
    response = _perform_pivotal_get(projects_url)
    root = ET.fromstring(response.text)
    project_id = root[index].find('id').text
    return Project.load_project(project_id)


def prompt_project(arguments):
    """prompts the user for a project, if not passed in as a argument"""

    def list_projects():
        projects_url = 'http://www.pivotaltracker.com/services/v3/projects'
        response = _perform_pivotal_get(projects_url)
        root = ET.fromstring(response.text)

        i = 0
        for child in root:
            i += 1
            project_name = child.find('name').text
            project_id = child.find('id').text
            print "[{}] {}".format(i, project_name)


    if arguments['--project-index'] is not None:
        try:
            project = get_project_by_index(int(arguments['--project-index']) - 1)
            return project
        except:
            print 'Yikes, that did not work -- try again?'
            exit()

    while True:
        print "Select a Project:"
        list_projects()
        s = raw_input('>> ')

        try:
           project = get_project_by_index(int(s) - 1)
        except:
            print 'Hmmm, that did not work -- try again?'
            continue

        break

    return project


def check_api_token():
    """Check to see if the API Token is set, else give instructions"""

    token = os.getenv('PIVOTAL_TOKEN', None)
    if token is None:
        print """
        You need to have your pivotal developer token set to the 'PIVOTAL_TOKEN' env variable.

        I keep mine in ~/.zshenv
        export PIVOTAL_TOKEN='your token'

        If you do not have one, login to pivotal, and go to your profile page, and scroll to the bottom.
        You'll find it there.
        """
        exit()


def initials(full_name):
    """Return the initials of a passed in name"""

    if full_name is not None and len(full_name) > 0:
        return ''.join([s[0] for s in full_name.split(' ')]).upper()
    else:
        return ''


def estimate_visual(estimate):
    if estimate is not None:
        return '[{:8s}]'.format('*' * estimate)
    else:
        return '[        ]'


def find_project_for_story(story_id, arguments):
    """If we have multiple projects, will loop through the projects to find the one with the given story"""

    project = None
    if arguments['--project-index'] is not None:
        try:
            project = get_project_by_index(int(arguments['--project-index']) - 1)
        except:
            pass

    if project is not None:
        return project
    else:
        # Loop thorugh your projects to try to find the project where the story is:
        projects_url = 'http://www.pivotaltracker.com/services/v3/projects'
        response = _perform_pivotal_get(projects_url)
        root = ET.fromstring(response.text)
        for project_node in root:
            project_id = _parse_text(project_node,'id')

            try:
                story_url = "http://www.pivotaltracker.com/services/v3/projects/{}/stories/{}".format(project_id, story_id)
                response = _perform_pivotal_get(story_url)
            except requests.exceptions.HTTPError, e:
                if e.code == 404:
                    continue
                else:
                    raise e

            if response is not None:
                return Project.load_project(project_id)
        else:
            print "Could not find story"
            exit()


def group_stories_by_owner(stories):
    stories_by_owner = {}
    for story in stories:
        if story.owned_by is not None:
            if story.owned_by in stories_by_owner:
                stories_by_owner[story.owned_by].append(story)
            else:
                stories_by_owner[story.owned_by] = [story]
        else:
            continue
    return stories_by_owner


def group_stories_by_label(stories):
    stories_by_label = {}
    for story in stories:
        if story.first_label in stories_by_label:
            stories_by_label[story.first_label].append(story)
        else:
            stories_by_label[story.first_label] = [story]

    return stories_by_label


def pretty_date():
    from datetime import datetime
    return datetime.now().strftime('%b %d, %Y')


def clear():
    """Clears the terminal buffer"""
    os.system('cls' if os.name == 'nt' else 'clear')


def pretty_print_story(story):
    print
    print bold(story.name)
    if len(story.description) > 0:
        print
        print story.description
        print

    if len(story.notes) > 0:
        print
        print bold('Notes:')
        for note in story.notes:
            print "[{}] {}".format(initials(note.author), note.text)

    if len(story.attachments) > 0:
        print
        print bold('Attachments:')
        for attachment in story.attachments:
            if len(attachment.description) > 0:
                print "Description: {}".format(attachment.description)
            print "Url: {}".format(colored(attachment.url, 'blue'))

    if len(story.labels) > 0:
        print
        print "{} {}".format(bold('Labels:'), story.labels)


def prompt_estimation(story):
    print
    print bold("Estimate: [0,1,2,3,5,8, (s)kip, (o)pen, (q)uit]")
    input_value = raw_input(bold('>> '))

    if input_value in ['s', 'S']:
        #skip move to the next
        return
    elif input_value in ['o', 'O']:
        webbrowser.open(story.url)
        prompt_estimation(story)
    elif input_value in ['q','Q']:
        exit()
    elif input_value in ['0','1','2','3','5','8']:
        value = int(input_value)
        story.assign_estimate(value)
    else:
        print "Invalid Input, Try again"
        prompt_estimation(story)


def _get_column_dimensions():
    rows, cols = os.popen('stty size', 'r').read().split()
    return int(rows), int(cols)



def main():
    clear()
    check_api_token()
    arguments = docopt(__doc__)
    if arguments['changelog']:
        project = prompt_project(arguments)
        generate_changelog(project)
    elif arguments['show_stories']:
        project = prompt_project(arguments)
        show_stories(project, arguments)
    elif arguments['show_story']:
        show_story(arguments['<story_id>'], arguments)
    elif arguments['browser_open']:
        browser_open(arguments['<story_id>'], arguments)
    elif arguments['scrum']:
        project = prompt_project(arguments)
        scrum(project)
    elif arguments['poker']:
        project = prompt_project(arguments)
        poker(project)
    else:
        print arguments


if __name__ == '__main__':
    main()
