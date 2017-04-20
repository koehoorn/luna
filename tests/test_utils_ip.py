from mock import patch
import unittest

from luna.utils import ip


class UtilsIPTestsV4(unittest.TestCase):

    def setUp(self):
        print

    def test_aton_with_valid_ip(self):
        self.assertEqual(ip.aton('10.0.0.1'), 167772161)

    def test_aton_with_invalid_ip(self):
        self.assertRaises(RuntimeError, ip.aton, '256.0.0.1')

    def test_ntoa_with_valid_absnum(self):
        self.assertEqual(ip.ntoa(167772161), '10.0.0.1')

    def test_ntoa_with_invalid_absnum(self):
        self.assertRaises(RuntimeError, ip.ntoa, 4294967296)

    def test_get_num_subnet_with_valid_input(self):
        num_subnet = ip.get_num_subnet('10.0.0.6', '24')
        self.assertEqual(num_subnet, 167772160)

    def test_get_num_subnet_with_invalid_prefix(self):
        self.assertRaises(RuntimeError, ip.get_num_subnet, '10.0.0.1', 33)

    def test_get_num_subnet_with_invalid_address(self):
        self.assertRaises(RuntimeError, ip.get_num_subnet, '256.0.0.1', 2)

    @patch('socket.gethostbyname')
    @patch('socket.gethostname')
    def test_guess_ns_hostname(self, gethostname, gethostbyname):
        # If no floating IP available with '-' in hostname

        gethostbyname.return_value = None
        gethostname.return_value = 'controller-1.cluster'

        self.assertEqual(ip.guess_ns_hostname(), 'controller-1')

        # If no floating IP available without '-' in hostname

        gethostname.return_value = 'controller1.cluster'

        self.assertEqual(ip.guess_ns_hostname(), 'controller1')

        # Floating IP available with '-' in hostname

        gethostbyname.return_value = '172.16.1.254'
        gethostname.return_value = 'controller-1.cluster'

        self.assertEqual(ip.guess_ns_hostname(), 'controller')

        # Floating IP available without '-' in hostname

        gethostname.return_value = 'controller1.cluster'

        self.assertEqual(ip.guess_ns_hostname(), 'controller')

        # Hostname does not end with digits

        gethostname.return_value = 'controller.cluster'

        self.assertEqual(ip.guess_ns_hostname(), 'controller')


class UtilsIPTestsV6(unittest.TestCase):

    def setUp(self):
        print

    def test_aton_with_valid_ip(self):
        self.assertEqual(
            ip.aton('fd12:3456:789a:1::1', 6),
            336389205813283084628800618700287770625
        )

    def test_aton_with_invalid_format(self):
        self.assertRaises(RuntimeError, ip.aton, 'fd12:3456:789a::1::1')

    def test_aton_with_invalid_ip(self):
        self.assertRaises(RuntimeError, ip.aton, 'gd12:3456:789a:1::1')

    def test_ntoa_with_valid_absnum(self):
        self.assertEqual(
            ip.ntoa(336389205813283084628800618700287770625, 6),
            'fd12:3456:789a:1::1'
        )

    def test_ntoa_with_invalid_absnum(self):
        self.assertRaises(
            RuntimeError,
            ip.ntoa,
            340282366920938463463374607431768211456,
            6
        )

    def test_get_num_subnet_with_valid_input(self):
        num_subnet = ip.get_num_subnet('fd12:3456:789a:1::1', 64, 6)
        self.assertEqual(
            num_subnet,
            336389205813283084628800618700287770624
        )

    def test_get_num_subnet_with_invalid_prefix(self):
        self.assertRaises(
            RuntimeError,
            ip.get_num_subnet,
            'fd12:3456:789a:1::1', 129, 6
        )

    def test_get_num_subnet_with_invalid_address(self):
        self.assertRaises(
            RuntimeError,
            ip.get_num_subnet,
            'gd12:3456:789a:1::1', 64, 6
        )

if __name__ == '__main__':
    unittest.main()
