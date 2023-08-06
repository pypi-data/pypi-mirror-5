from mock import call, MagicMock as Mock, patch
from nose.tools import raises

import spreads
import spreads.plugin as plugin
from spreads.util import DeviceException


class TestPlugin(object):
    def setUp(self):
        spreads.config.clear()
        spreads.config.read(user=False)
        spreads.config['plugins'] = []
        reload(plugin)

    def test_pluginmanager(self):
        plugin.SpreadsNamedExtensionManager = Mock()
        pm = plugin.get_pluginmanager()
        assert plugin.SpreadsNamedExtensionManager.call_count == 1
        assert plugin.SpreadsNamedExtensionManager.call_args_list == ([call(
            invoke_on_load=True, namespace=u'spreadsplug.hooks', names=[],
            name_order=True, invoke_args=[spreads.config])])
        pm_new = plugin.get_pluginmanager()
        assert plugin.SpreadsNamedExtensionManager.call_count == 1
        assert pm is pm_new

    def test_get_devices(self):
        device_a = Mock()
        device_a.plugin.match = Mock(return_value=True)
        device_a.plugin.__name__ = "Mock"
        device_b = Mock()
        device_b.plugin.match = Mock(return_value=False)
        device_b.plugin.__name__ = "Mock"
        usb_mock = Mock()
        plugin.usb.core.find = Mock(return_value=[usb_mock])
        dm = Mock()
        dm.map = lambda x, y: [x(z, y) for z in [device_a, device_b]]
        plugin.get_devicemanager = Mock(return_value=dm)
        ret = plugin.get_devices()
        assert ret == [device_a.plugin()]
        assert call(spreads.config, usb_mock) in device_a.plugin.call_args_list
        assert device_a.plugin.match.call_args_list == [call(usb_mock)]
        assert device_b.plugin.match.call_args_list == [call(usb_mock)]

    @raises(DeviceException)
    def test_no_devices(self):
        device_a = Mock()
        device_a.plugin.match = Mock(return_value=True)
        device_b = Mock()
        device_b.plugin.match = Mock(return_value=False)
        plugin.usb.core.find = Mock(return_value=[])
        dm = Mock()
        dm.map = lambda x, y: [x(z, y) for z in [device_a, device_b]]
        plugin.get_devicemanager = Mock(return_value=dm)
        plugin.get_devices()
