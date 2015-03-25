#!/usr/bin/env python

__author__ = "Rostyslav Fridman"
__copyright__ = "Copyright 2015"
__license__ = "Apache License 2.0"
__version__ = "1.0"
__maintainer__ = "Rostyslav Fridman"
__email__ = "rostyslav.fridman@gmail.com"
__status__ = "Development"

import urllib2
import json
import re


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def deleteArtifacts(url, credentials, repo, group, artifact, num_versions):
    versions = []
    paths = []
    point = re.compile("\.")
    uri = url + "/api/search/gavc?g=" + group + "&a=" \
        + artifact + "&repos=" + repo

    try:
        request = urllib2.Request(uri)
        request.add_header("Authorization", "Basic %s" % credentials)
        output = urllib2.urlopen(request)
    except Exception as e:
        return "The connection wasn't successful. Error: %s" % e

    result = output.read()

    if not result:
        return "There are no %s/%s artifacts" % \
               (re.sub(point, "/", group), artifact)

    result_json = json.loads(result)

    for path in result_json["results"]:
        artifact_path = path["uri"].split("/")
        versions.append(artifact_path[-2])

    versions = unique(versions)
    versions.sort(key=lambda s: map(int, s.split('.')))

    print("Going to leave these %s/%s artifacts untouched: %s" %
          (re.sub(point, "/", group), artifact, versions[-num_versions:]))
    # Leave the latest n versions
    del versions[-num_versions:]

    for version in versions:
        paths.append(url + "/" + repo + "/" + re.sub(point, "/", group) +
                     "/" + artifact + "/" + version)

    for path in paths:
        try:
            request = urllib2.Request(path)
            request.add_header("Authorization", "Basic %s" % credentials)
            request.get_method = lambda: 'DELETE'
            result = urllib2.urlopen(request)
            print "Artifact %s was deleted" % path
        except Exception as e:
            print("Couldn't delete artifact %s. Error: %s" % (path, e))

# Artifactory url
url = "http://artifactory.example.com/artifactory"
# Artifactory repository
repo = "Some-Repo"
# Artifactory credentials encoded in base64
credentials = "Base64GoesHere=="
# Number of versions that should not be deleted
num_versions = 30

# Artifacts tuples in the format:
# [("some.group", "artifact_name")]
artifacts = [
    ("some.group", "some-artifact")
]

for group, artifact in artifacts:
    deleteArtifacts(url, credentials, repo, group, artifact, num_versions)
