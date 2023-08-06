#!/usr/bin/python

#    Copyright 2012 Urban Airship
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Inspect an iOS or Android project for configuration errors"""

import sys
import argparse
import logging
import os
import support
import iossupport
import androidsupport
import package_info

from iossupport import VerificationInformation


def display_version():
    """Display the version number and usage if desired"""

    print("Version:%s" % package_info.current_version())


NO_CONFIG_PLIST_ERROR = """
No AirshipConfig.plist in app bundle. Without the configuration plist the
verification API call cannot be made. Parsing the app key and secret from
code is slated for a future release.
"""


class IosVerify(object):
    """ Verify the build with Urban Airship """

    def execute_xcode_verify(self):
        """Execute all build verification tasks"""

        # Setup logger
        log = logging.getLogger(support.UA_LOGGER)

        if self.version:
            display_version()
            return support.EXIT_SUCCESS

        iossupport.clean()

        if self.diagnostic:
            log.info("Setting up diagnostic logging")
            support.setup_diagnostic_logging()

        # Extract entitlement info from app
        log.info("Executing codesign system call")

        if self.application_path is None:
            log.error("Path to application is required. application_path must"
                      " be set in command line options")
            return False

        success = iossupport.execute_codesign_system_call(
            self.application_path)
        if not success:
            log.error("Error in codesign system call")
            return False

        # Parse entitlement plist output
        entitlements_plist_path = \
            support.get_value_from_config(support.ENTITLEMENTS_PLIST_PATH)

        entitlement_plist = iossupport.read_entitlement_plist_from_path(
            entitlements_plist_path)
        if entitlement_plist is None:
            log.error("Entitlement plist could not be read")
            return False

        # Read the AirshipConfig from the app
        if self.plist is None:
            airship_config_plist = iossupport.extract_airship_config_from_app(
                self.application_path)
        else:
            airship_config_plist = \
                iossupport.extract_airship_config_from_app(
                    self.application_path, self.plist)

        # Store entitlement and config info
        self.verification_info = VerificationInformation(
            entitlement_plist, airship_config_plist)
        iossupport.log.debug("Verification:%s", self.verification_info)

        # Check local entitlement settings and app configuration
        if not self.verification_info.check_aps_environment():
            return False

        # If there is no plist, there is no reason to verify anything
        # else. This is done after extracting the entitlements, but
        # before the matching API call. Extracting the information from code
        # is slated for a future release.
        if not airship_config_plist:
            if self.diagnostic:
                self.verification_info.log_diagnostic_information()
            log.error(NO_CONFIG_PLIST_ERROR)
            return False

        # Make API verification request
        request = iossupport.get_verification_request(self.verification_info)
        response = iossupport.make_request_against_api(request)
        if response.error is not None:
            log.error("API verification request failed")
            return False
        iossupport.log.debug("Response %s", response)

        # API response dependent tests
        apns_server = self.verification_info.check_apns_server(response.json)
        if not apns_server:
            log.error("APNS server is not configured properly")
            return False

        bundle_id = self.verification_info.check_bundle_id(response.json)
        if not bundle_id:
            log.error("Bundle id mismatch")
            return False

        if self.diagnostic:
            # Print diagnostic info, this has the side effect of printing
            # to a file
            self.verification_info.log_diagnostic_information()

        return True


class AndroidVerify(object):
    """Verify an Android Project"""

    def execute_android_verify(self):
        """Verify the android build"""

        # Setup logger
        log = logging.getLogger(support.UA_LOGGER)

        if self.version:
            display_version()
            return support.EXIT_SUCCESS

        if self.diagnostic:
            log.info("Setting up diagnostic logging")
            support.setup_diagnostic_logging()

        if not os.path.isdir(self.application_path):
            log.error("Path %s is not a directory." % self.application_path)
            return support.EXIT_FAILURE

        if self.manifest_path:
            manifest_element_tree = \
                androidsupport.parse_android_manifest(self.manifest_path)
        else:
            manifest_element_tree = \
                androidsupport.parse_manifest_in_directory(
                    self.application_path)

        # TODO change this so that it doesn't stop until all tests are run
        if manifest_element_tree is None:
            log.error("There is a problem with the AndroidManifest")
            return support.EXIT_FAILURE

        package_name = \
            androidsupport.package_name_from_manifest(manifest_element_tree)
        log.info("Package Name %s" % package_name)

        test_has_failed = list()

        isMissing = androidsupport.is_missing_uses_permissions(
            manifest_element_tree)
        if isMissing:
            test_has_failed.append(True)

        isMissing = androidsupport.is_missing_package_dependent_permissions(
            manifest_element_tree, package_name)
        if isMissing:
            test_has_failed.append(True)

        isMissing = androidsupport.is_missing_receiver_attributes(
            manifest_element_tree)
        if isMissing:
            test_has_failed.append(True)

        isMissing = androidsupport.is_missing_action_attributes(
            manifest_element_tree)
        if isMissing:
            test_has_failed.append(True)

        isMissing = androidsupport.is_missing_android_provider_attribute(
            manifest_element_tree, package_name)
        if isMissing:
            test_has_failed.append(True)

        # TODO possibly check proguard for annotations
        if not androidsupport.is_analytics_implemented(self.application_path):
            test_has_failed.append(True)

        if not androidsupport.is_takeoff_called(self.application_path):
            test_has_failed.append(True)

        airship_config_properties = androidsupport.read_properties_file(
            self.application_path)

        if airship_config_properties is None:
            test_has_failed.append(True)
            # If there are no config properties, a request cannot be made
            response = None
        else:
            request = androidsupport.get_verification_request(
                airship_config_properties)
            response = support.make_request_against_api(request)

        if response is None:
            test_has_failed.append(True)
        elif response.error is not None:
            test_has_failed.append(True)
        elif not androidsupport.is_airship_configured_properly(
            response.json,
            airship_config_properties,
            package_name):

            test_has_failed.append(True)

    # If something is missing in the test results, there was a problem
        if True in test_has_failed:
            log.error("Problems found in the Android Project")
            return support.EXIT_FAILURE
        else:
            log.info("Android project verified successfully")
            return support.EXIT_SUCCESS

APPLICATION_PATH_MESSAGE = """
Path to Project.app directory for iOS or root project directory for Android
"""

IOS_EPILOG = """
Extract the entitlements from a .app directory, parse them, and
check for errors. An API call is made to Urban Airship using the
configured key/secret pair to return API app settings for
comparison
"""


def ios_main():
    """Parses arguments and runs the uav-ios tool against an app"""

    log = logging.getLogger(support.UA_LOGGER)

    parser =\
        argparse.ArgumentParser(description="Verify a build with Urban Airship",
                                epilog=IOS_EPILOG)

    parser.add_argument('application_path', type=str, nargs="?",
                        help=APPLICATION_PATH_MESSAGE)

    parser.add_argument('-d', '--diagnostic', action="store_true",
                        help="Write out diagnostic information to a file")

    parser.add_argument('--plist', type=str,
                        help="Name of the configuration plist, "
                             "defaults to \"AirshipConfig.plist\" ")

    parser.add_argument('-v', '--version', action="store_true",
                        help="Display version number and exit")

    # Short circuit if there are no command line args
    if len(sys.argv) <= 1:
        display_version()
        parser.print_usage()
        return support.EXIT_SUCCESS

    # This appends the args to the object as instance variables
    verify = IosVerify()
    parser.parse_args(namespace=verify)

    success = verify.execute_xcode_verify()
    # There is the possibility of a file logger
    logging.shutdown()
    if success:
        log.debug("Successful verification")
        return support.EXIT_SUCCESS
    else:
        log.error("Failed verification")
        return support.EXIT_FAILURE

ANDROID_EPILOG = """
Parse the AndroidManifest.xml and look for required settings. Search
code files for proper implementation of analytics and references to takeOff. An
API call is made to Urban Airship using the key/secret pair to return API
app settings for comparison.
"""

ANDROID_MANIFEST_HELP = """
If your application has more than one AndroidManifest.xml file, use this flag
to pass the path of the manifest file to use for verification.
"""


def android_arg_parser():
    """Setup the arg parser for the Android tool"""

    parser = \
        argparse.ArgumentParser(description="Verify a build with Urban Airship",
                                epilog=ANDROID_EPILOG)

    parser.add_argument('application_path', type=str, nargs="?",
                        help=APPLICATION_PATH_MESSAGE)

    parser.add_argument('-d', '--diagnostic', action="store_true",
                        help="Write out diagnostic information to a file")

    parser.add_argument('-m', '--manifest_path', action="store",
                        help=ANDROID_MANIFEST_HELP)

    parser.add_argument('-v', '--version', action="store_true",
                        help="Display version number and exit")
    return parser


def android_main():
    """Parses arguments and runs the uav-android tool against an app"""

    log = logging.getLogger(support.UA_LOGGER)

    parser = android_arg_parser()

    # Short circuit if there are no command line args
    if len(sys.argv) <= 1:
        display_version()
        parser.print_usage()
        return support.EXIT_SUCCESS

    verify = AndroidVerify()
    parser.parse_args(namespace=verify)

    success = verify.execute_android_verify()
    # There is the possibility of a file logger
    logging.shutdown()
    if success == support.EXIT_SUCCESS:
        log.debug("Successful verification")
        return support.EXIT_SUCCESS
    else:
        log.error("Verification failed")
        return support.EXIT_FAILURE
