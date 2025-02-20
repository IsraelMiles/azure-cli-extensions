# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from azure.cli.core.util import CLIError
import azext_aks_preview._validators as validators
from azext_aks_preview._consts import ADDONS


class TestValidateIPRanges(unittest.TestCase):
    def test_simultaneous_allow_and_disallow_with_spaces(self):
        api_server_authorized_ip_ranges = " 0.0.0.0/32 , 129.1.1.1.1 "
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = ("Setting --api-server-authorized-ip-ranges to 0.0.0.0/32 is not allowed with other IP ranges."
               "Refer to https://aka.ms/aks/whitelist for more details")

        with self.assertRaises(CLIError) as cm:
            validators.validate_ip_ranges(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_simultaneous_enable_and_disable_with_spaces(self):
        # an entry of "", 129.1.1.1.1 from command line is translated into " , 129.1.1.1.1"
        api_server_authorized_ip_ranges = " , 129.1.1.1.1"
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = "--api-server-authorized-ip-ranges cannot be disabled and simultaneously enabled"

        with self.assertRaises(CLIError) as cm:
            validators.validate_ip_ranges(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_disable_authorized_ip_ranges(self):
        api_server_authorized_ip_ranges = ''
        namespace = Namespace(api_server_authorized_ip_ranges)
        validators.validate_ip_ranges(namespace)

    def test_local_ip_address(self):
        api_server_authorized_ip_ranges = "192.168.0.0,192.168.0.0/16"
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = "--api-server-authorized-ip-ranges must be global non-reserved addresses or CIDRs"

        with self.assertRaises(CLIError) as cm:
            validators.validate_ip_ranges(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_invalid_ip(self):
        api_server_authorized_ip_ranges = "193.168.0"
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = "--api-server-authorized-ip-ranges should be a list of IPv4 addresses or CIDRs"

        with self.assertRaises(CLIError) as cm:
            validators.validate_ip_ranges(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_IPv6(self):
        api_server_authorized_ip_ranges = "3ffe:1900:4545:3:200:f8ff:fe21:67cf"
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = "--api-server-authorized-ip-ranges cannot be IPv6 addresses"

        with self.assertRaises(CLIError) as cm:
            validators.validate_ip_ranges(namespace)
        self.assertEqual(str(cm.exception), err)


class TestClusterAutoscalerParamsValidators(unittest.TestCase):
    def test_empty_key_empty_value(self):
        cluster_autoscaler_profile = ["="]
        namespace = Namespace(cluster_autoscaler_profile=cluster_autoscaler_profile)
        err = "Empty key specified for cluster-autoscaler-profile"

        with self.assertRaises(CLIError) as cm:
            validators.validate_cluster_autoscaler_profile(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_non_empty_key_empty_value(self):
        cluster_autoscaler_profile = ["scan-interval="]
        namespace = Namespace(cluster_autoscaler_profile=cluster_autoscaler_profile)

        validators.validate_cluster_autoscaler_profile(namespace)

    def test_two_empty_keys_empty_value(self):
        cluster_autoscaler_profile = ["=", "="]
        namespace = Namespace(cluster_autoscaler_profile=cluster_autoscaler_profile)
        err = "Empty key specified for cluster-autoscaler-profile"

        with self.assertRaises(CLIError) as cm:
            validators.validate_cluster_autoscaler_profile(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_one_empty_key_in_pair_one_non_empty(self):
        cluster_autoscaler_profile = ["scan-interval=20s", "="]
        namespace = Namespace(cluster_autoscaler_profile=cluster_autoscaler_profile)
        err = "Empty key specified for cluster-autoscaler-profile"

        with self.assertRaises(CLIError) as cm:
            validators.validate_cluster_autoscaler_profile(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_invalid_key(self):
        cluster_autoscaler_profile = ["bad-key=val"]
        namespace = Namespace(cluster_autoscaler_profile=cluster_autoscaler_profile)
        err = "Invalid key specified for cluster-autoscaler-profile: bad-key"

        with self.assertRaises(CLIError) as cm:
            validators.validate_cluster_autoscaler_profile(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_parameters(self):
        cluster_autoscaler_profile = ["scan-interval=20s", "scale-down-delay-after-add=15m"]
        namespace = Namespace(cluster_autoscaler_profile=cluster_autoscaler_profile)

        validators.validate_cluster_autoscaler_profile(namespace)


class Namespace:
    def __init__(self, api_server_authorized_ip_ranges=None, cluster_autoscaler_profile=None, kubernetes_version=None):
        self.api_server_authorized_ip_ranges = api_server_authorized_ip_ranges
        self.cluster_autoscaler_profile = cluster_autoscaler_profile
        self.kubernetes_version = kubernetes_version


class TestSubnetId(unittest.TestCase):
    def test_invalid_subnet_id(self):
        invalid_vnet_subnet_id = "dummy subnet id"
        err = ("--vnet-subnet-id is not a valid Azure resource ID.")

        with self.assertRaises(CLIError) as cm:
            validators._validate_subnet_id(invalid_vnet_subnet_id, "--vnet-subnet-id")
        self.assertEqual(str(cm.exception), err)

    def test_valid_vnet_subnet_id(self):
        valid_subnet_id = "/subscriptions/testid/resourceGroups/MockedResourceGroup/providers/Microsoft.Network/virtualNetworks/MockedNetworkId/subnets/MockedSubNetId"
        validators._validate_subnet_id(valid_subnet_id, "something")

    def test_none_vnet_subnet_id(self):
        validators._validate_subnet_id(None, "something")

    def test_empty_vnet_subnet_id(self):
        validators._validate_subnet_id("", "something")


class MaxSurgeNamespace:
    def __init__(self, max_surge):
        self.max_surge = max_surge


class SpotMaxPriceNamespace:
    def __init__(self, spot_max_price):
        self.priority = "Spot"
        self.spot_max_price = spot_max_price


class TestMaxSurge(unittest.TestCase):
    def test_valid_cases(self):
        valid = ["5", "33%", "1", "100%"]
        for v in valid:
            validators.validate_max_surge(MaxSurgeNamespace(v))

    def test_throws_on_string(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_max_surge(MaxSurgeNamespace("foobar"))
        self.assertTrue('int or percentage' in str(cm.exception), msg=str(cm.exception))

    def test_throws_on_negative(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_max_surge(MaxSurgeNamespace("-3"))
        self.assertTrue('positive' in str(cm.exception), msg=str(cm.exception))


class TestSpotMaxPrice(unittest.TestCase):
    def test_valid_cases(self):
        valid = [5, 5.12345, -1.0, 0.068, 0.071, 5.00000000]
        for v in valid:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(v))

    def test_throws_if_more_than_5(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(5.123456))
        self.assertTrue('--spot_max_price can only include up to 5 decimal places' in str(cm.exception), msg=str(cm.exception))

    def test_throws_if_non_valid_negative(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(-2))
        self.assertTrue('--spot_max_price can only be any decimal value greater than zero, or -1 which indicates' in str(cm.exception), msg=str(cm.exception))
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(0))
        self.assertTrue('--spot_max_price can only be any decimal value greater than zero, or -1 which indicates' in str(cm.exception), msg=str(cm.exception))

    def test_throws_if_input_max_price_for_regular(self):
        ns = SpotMaxPriceNamespace(2)
        ns.priority = "Regular"
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(ns)
        self.assertTrue('--spot_max_price can only be set when --priority is Spot' in str(cm.exception), msg=str(cm.exception))


class ValidateAddonsNamespace:
    def __init__(self, addons):
        self.addons = addons


class TestValidateAddons(unittest.TestCase):
    def test_correct_addon(self):
        addons = list(ADDONS)
        if len(addons) > 0:
            first_addon = addons[0]
            namespace1 = ValidateAddonsNamespace(first_addon)

            try:
                validators.validate_addons(namespace1)
            except CLIError:
                self.fail("validate_addons failed unexpectedly with CLIError")

    def test_validate_addons(self):
        addons = list(ADDONS)
        if len(addons) > 0:
            first_addon = addons[0]
            midlen = int(len(first_addon) / 2)

            namespace = ValidateAddonsNamespace(
                first_addon[:midlen] + first_addon[midlen + 1:])
            self.assertRaises(CLIError, validators.validate_addons, namespace)

    def test_no_addon_match(self):
        namespace = ValidateAddonsNamespace("qfrnmjk")

        self.assertRaises(CLIError, validators.validate_addons, namespace)


class AssignIdentityNamespace:
    def __init__(self, assign_identity):
        self.assign_identity = assign_identity


class TestAssignIdentity(unittest.TestCase):
    def test_invalid_identity_id(self):
        invalid_identity_id = "dummy identity id"
        namespace = AssignIdentityNamespace(invalid_identity_id)
        err = ("--assign-identity is not a valid Azure resource ID.")

        with self.assertRaises(CLIError) as cm:
            validators.validate_assign_identity(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_identity_id(self):
        valid_identity_id = "/subscriptions/testid/resourceGroups/MockedResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/mockIdentityID"
        namespace = AssignIdentityNamespace(valid_identity_id)
        validators.validate_assign_identity(namespace)

    def test_none_identity_id(self):
        none_identity_id = None
        namespace = AssignIdentityNamespace(none_identity_id)
        validators.validate_assign_identity(namespace)

    def test_empty_identity_id(self):
        empty_identity_id = ""
        namespace = AssignIdentityNamespace(empty_identity_id)
        validators.validate_assign_identity(namespace)


class PodIdentityNamespace:

    def __init__(self, identity_name):
        self.identity_name = identity_name


class TestValidatePodIdentityResourceName(unittest.TestCase):

    def test_valid_required_resource_name(self):
        validator = validators.validate_pod_identity_resource_name('identity_name', required=True)
        namespace = PodIdentityNamespace('test-name')
        validator(namespace)

    def test_missing_required_resource_name(self):
        validator = validators.validate_pod_identity_resource_name('identity_name', required=True)
        namespace = PodIdentityNamespace(None)

        with self.assertRaises(CLIError) as cm:
            validator(namespace)
        self.assertEqual(str(cm.exception), '--name is required')


class PodIdentityResourceNamespace:

    def __init__(self, namespace):
        self.namespace = namespace


class TestValidatePodIdentityResourceNamespace(unittest.TestCase):

    def test_valid_required_resource_name(self):
        namespace = PodIdentityResourceNamespace('test-name')
        validators.validate_pod_identity_resource_namespace(namespace)

    def test_missing_required_resource_name(self):
        namespace = PodIdentityResourceNamespace(None)

        with self.assertRaises(CLIError) as cm:
            validators.validate_pod_identity_resource_namespace(namespace)
        self.assertEqual(str(cm.exception), '--namespace is required')

class TestValidateKubernetesVersion(unittest.TestCase):

    def test_valid_full_kubernetes_version(self):
        kubernetes_version = "1.11.8"
        namespace = Namespace(kubernetes_version=kubernetes_version)

        validators.validate_k8s_version(namespace)

    def test_valid_alias_minor_version(self):
        kubernetes_version = "1.11"
        namespace = Namespace(kubernetes_version=kubernetes_version)

        validators.validate_k8s_version(namespace)

    def test_valid_empty_kubernetes_version(self):
        kubernetes_version = ""
        namespace = Namespace(kubernetes_version=kubernetes_version)

        validators.validate_k8s_version(namespace)

    def test_invalid_kubernetes_version(self):
        kubernetes_version = "1.2.3.4"

        namespace = Namespace(kubernetes_version=kubernetes_version)
        err = ("--kubernetes-version should be the full version number or alias minor version, "
               "such as \"1.7.12\" or \"1.7\"")

        with self.assertRaises(CLIError) as cm:
            validators.validate_k8s_version(namespace)
        self.assertEqual(str(cm.exception), err)

        kubernetes_version = "1."

        namespace = Namespace(kubernetes_version=kubernetes_version)

        with self.assertRaises(CLIError) as cm:
            validators.validate_k8s_version(namespace)
        self.assertEqual(str(cm.exception), err)


if __name__ == "__main__":
    unittest.main()
