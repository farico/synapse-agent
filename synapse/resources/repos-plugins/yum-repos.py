import ConfigParser
import os

from synapse.synapse_exceptions import ResourceException


repo_path = "/etc/yum.repos.d"


def get_repos(name):

    repos = {}
    repo_file_list = os.listdir(repo_path)

    for repo_file in repo_file_list:
        repo_file_path = os.path.join(repo_path, repo_file)
        #Bleuargh, I don't like this
        config = ConfigParser.RawConfigParser()
        config.read(repo_file_path)
        for section in config.sections():
            repo = dict(config.items(section))
            repo["filename"] = repo_file_path
            repos[section] = repo

    if name:
        return repos.get(name)
    else:
        return repos


def create_repo(id, attributes):

    config_parser = ConfigParser.RawConfigParser()

    values = ("name",
              "baseurl",
              "metalink",
              "mirrorlist",
              "gpgcheck",
              "gpgkey",
              "exclude",
              "includepkgs",
              "enablegroups",
              "enabled",
              "failovermethod",
              "keepalive",
              "timeout",
              "enabled",
              "http_caching",
              "retries",
              "throttle",
              "bandwidth",
              "sslcacert",
              "sslverify",
              "sslclientcert",
              "metadata_expire",
              "mirrorlist_expire",
              "proxy",
              "proxy_username",
              "proxy_password",
              "cost",
              "skip_if_unavailable")

    # Check if repo already exists
    repo = get_repos(id)

    # If it exists, get the filename in which the repo is defined
    # If not, check if a filename is user provided
    # If no filename is provided, create one based on the repo name
    if repo:
        filename = repo.get("filename")
    elif attributes.get("filename"):
        filename = attributes["filename"]
    else:
        filename = "%s.repo" % id

    # Read the config file (empty or not) and load it in a ConfigParser
    # object
    repo_file_path = os.path.join(repo_path, filename)
    config_parser.read(repo_file_path)

    # Check if the repo is define in the ConfigParser context.
    # If not, add a section based on the repo name.
    if not config_parser.has_section(id):
        config_parser.add_section(id)
        config_parser.set(id, "name", id)

    # Update the section with not None fields provided by the user
    for key, value in attributes.items():
        if value is not None and key in values:
            config_parser.set(id, key, value)

    # Write changes to the repo file.
    with open(repo_file_path, 'wb') as repofile:
        config_parser.write(repofile)


def delete_repo(id):
    config_parser = ConfigParser.RawConfigParser()
    repo = get_repos(id)

    if repo:

        filename = repo.get("filename")
        repo_file_path = os.path.join(repo_path, filename)
        config_parser.read(repo_file_path)

        if config_parser.remove_section(id):
            # Write changes to the repo file.
            with open(repo_file_path, 'wb') as repofile:
                config_parser.write(repofile)

        # Delete the repo file if there are no section in them
        config_parser.read(repo_file_path)
        if not len(config_parser.sections()):
            os.remove(repo_file_path)

    else:
        raise ResourceException("Repo not found")
