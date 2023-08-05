# Release Notes for pyrax

###2013.06.03 - Version 1.4.3
- Added support for having objects automatically deleted from Cloud Files after
    a period of time.

###2013.05.30 - Version 1.4.2
- Fixed several bugs related to the identity and config file changes.

###2013.05.30 - Version 1.4.1
- Added support for new Cloud Database user APIs.
- Fixed a bug in which an exception class was not defined (#77)

###2013.05.29 - Version 1.4.0
- Added support for **all** OpenStack clouds. Previous versions only supported
    Rackspace authentication methods.
- Configuration files now support multiple cloud environments in the same file.
    You can switch between environments by calling `pyrax.set_environment("env")`,
    where `env` is the name of the desired environment.
- Configuration settings can now be stored in environment variables. These all
    begin with `CLOUD_`; a full list can be found in the [main pyrax
    documentation](https://github.com/rackspace/pyrax/tree/master/docs/pyrax_doc.md).
- Available regions are now available in the `pyrax.regions` attribute after
    authentication.
- Services that are available for the current cloud provider are now available
    in the `pyrax.services` attribute.
- Fixed an issue in Cloud Databases in which the `volume` attribute was
    sometimes a dict and sometimes an instance of `CloudDatabaseVolume`. Now it
    will always be an instance.
- Added a smoke test script to the integrated tests. It currently covers the
    compute, networking, database, and object_store services.
- Removed unnecessary hack for compute URIs.
- Cleaned up some naming and formatting inconsistencies.


###2013.05.10 - Version 1.3.9
- This fixes two issues: #63 and #67. The first fixes an incorrect path in the
    cloudfiles get_temp_url() function; the second adds the ability to specify
    the content_encoding for an object in cloudfiles.

###2013.04.29 - Version 1.3.8
- Fixed a bug that prevented the Cloud Servers code from running properly
    in the UK.

###2013.04.26 - Version 1.3.7
- Removed a lot of the duplicated identity code from the main client
    class. This is in anticipation of a major re-working of identity
    that will work with non-Rackspace OpenStack deployments.
- Added methods to Cloud Load Balancer code to make it easier to get
    individual device usages and links.
- Added a customizable delay period for Cloud DNS.
- Changed the default behavior of utils.wait_until() to wait forever
    for the desired state to be reached. Previous default was 10 attempts,
    and it seemed that over 90% of use cases required waiting indefinitely,
    so the default was changed.
- Cleaned up some of the documentation style.

###2013.04.03 - Version 1.3.6
- Fixed the auth issues with python-novaclient introduced in the most
    recent release of that library. Thanks to Matt Martz for this fix.

###2013.03.27 - Version 1.3.5
- Updated the Cloud Databases code to work with recent API changes.
- Updated HACKING doc to include specific PEP8 exclusions.
- Cleaned up the code in the tests/ and samples/ directories for PEP8.
- Changed all uses of `file()` to `open()`.
- Added tox support.

###2013.03.26 - Version 1.3.4
- Fixed an ImportError in Cloud DNS. Thanks to Matt Martz for finding this.
- Minor improvements to the travis.ci integration.

###2013.03.21 - Version 1.3.3
- Added support for creating Temporary URLs for Cloud Files.
- Added set_account_metadata() for Cloud Files.
- Added shortcuts to the Cloud Servers client to make it more consistent
    with the rest of pyrax. E.g.:
      cs.images.list() -> cs.list_images()
- Added change_content_type() to the StorageObject class in Cloud Files.
- Cleaned up the __repr__ for some classes.
- Added more customization to the output for utils.wait_until()
- Cleaned up the markdown formatting in RELEASENOTES.md.
- Added travis-ci integration.

###2013.03.06 - Version 1.3.2
- Removed lazy loading of Database Volumes. GitHub #8.
- Fixed the inconsistent naming of the cloud databases module.
- Removed mixed line endings from the docs that my markdown
    editor inserted.
- Added the find_record() method to Cloud DNS to return a single
    domain record. GitHub #24.
- Added the test dependency for the 'mock' package to setup.py

###2013.03.04 - Version 1.3.1
- The merge for 1.3.0 did not grab the newly-created files for that
    version. They are included in this version.

###2013.03.04 - Version 1.3.0
- Added support for Rackspace Cloud Networks.
- Modified attach/detach of CBS volumes so that they both raise
exceptions on failure, and return None otherwise. GitHub #22
- Fixed bug in block storage that could connect to incorrect
datacenter. Github #19
- Added the option of running utils.wait_until() in a background thread.
- Added the HACKING file to help people contribute to pyrax.
- Merged pull request #21 from simonz05: fix name error: global
name `self` does not exist.

###2013.02.18 - Version 1.2.8
- Fixed a bug that created multiple debugging loggers.
- Refactored the utils script to use the match_pattern() method.

###2013.02.15 - Version 1.2.7
- Code formatting cleanup. No logical changes or additional
functionality included.
- Added httplib2 requirement, now that novaclient no longer installs
it. Taken from pull request #18 from Dustin Farris.
- Merge pull request #13 from adregner/container-ints: container
stats should be integers
- Modified the upload_file() process to not return an object
reference when not needed. GitHub issue #11.

###2013.02.05 - Version 1.2.6
- Added the `sync_folder_to_container()` method to cloudfiles to make it
easier to keep a copy of a local folder synced to the cloud.
- Removed the lazy load of volume info for cloud databases. Changed the
'volume' attribute to be an object to allow for dot notation access
to its values.
- Eliminated as many places as possible where use of non-ASCII characters
caused encoding issues. Added a configuration option to allow users to
specify their preferred encoding; default=utf-8.
- Fixed a bug in the `get_object_names()` method of the Cloud Files
container class.

###2013.01.26 - Version 1.2.5
- Fixed an issue preventing existing node objects being created if in
'DRAINING' condition (GitHub #6). Modified the rax_identity to accept
UTC dates returned from the LON datacenter (GitHub #5). Fixed an
issue that prevented HTTP debugging from turning off in swiftclient.
             

###2013.01.15 - Version 1.2.4
- Added support for keychain storage of credentials for authentication.


###2013.01.10 - Version 1.2.3
- Added the 'halfClosed' parameter to the create() method of load balancers.

###2013.01.03 - Version 1.2.2
- Fixed an issue that was causing calls to cloudservers to needlessly re-authenticate.

###2012.12.27 - Version 1.2.1
- Removed old class docs that were no longer needed in this release.

###2012.12.26 - Version 1.2.0
- Added support for Cloud DNS.
- Removed the 'beta' designation.

###2012.12.26 - Version 1.1.7b
- Updated setup.py to use setuptools.
- Fixed a problem with circular imports of the version info.
- Added a requirement for python-novaclient>=2.10.0.

###2012.12.18 - Version 1.1.6b
- Removed the code that controlled when pyrax connected to services. 
- Changed the User-agent format to match the other SDKs.

###2012.12.17 - Version 1.1.5b
- Enhanced the ability to debug HTTP traffic.
- Fixed a bug in object naming when uploading an entire folder in Cloud Files.

###2012.12.13 - Version 1.1.4b
- Added the ability to connect to the internal URL for Cloud Files.
- Added limit and marker to the base client/manager classes.
- Added the cloudfiles Container and StorageObject classes to the pyrax namespace.

###2012.12.10 - Version 1.1.2b
- Added a test that was missing in the previous release.

###2012.12.07 - Version 1.1.1b
- Added the ability for developers to customize the User-agent string for their applications.

###2012.11.26 - Version 1.1.1b
- Added Cloud Block Storage support.
- Added the refactored code for Cloud Load Balancers that removes the dependency on the python-cloudlb library.

###2012.11.24 - Version 1.0.4b
- Maintenance fix release.

###2012.11.20
- Improved the handling of CDN calls so they don't fail as often, and are more resilient when they do.

###2012.11.06
- Release of the initial beta for pyrax. Supports Cloud Servers, Cloud Files, and Cloud Load Balancers.
