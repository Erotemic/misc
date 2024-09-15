#!/usr/bin/env python3
"""
WIP to fixup monitor positions using dbus

References:
    https://gitlab.com/goshansp/infrastructure/-/blob/main/files/screen_toggle.py
    https://dbus.freedesktop.org/doc/dbus-python/tutorial.html
    https://github.com/GNOME/mutter/blob/b5f99bd12ebc483e682e39c8126a1b51772bc67d/data/dbus-interfaces/org.gnome.Mutter.DisplayConfig.xml
    https://discussion.fedoraproject.org/t/change-scaling-resolution-of-primary-monitor-from-bash-terminal/19892
Requirements:
    pip install dbus-python
"""

import platform
import dbus
import enum


class DBusMethod(enum.Enum):
    # 2 means show a prompt before applying settings; 1 means instantly apply settings without prompt
    PROMPT = 2
    NO_PROMPT = 1


class DBusTransform(enum.Enum):
    """
    References:
        https://github.com/GNOME/mutter/blob/b5f99bd12ebc483e682e39c8126a1b51772bc67d/data/dbus-interfaces/org.gnome.Mutter.DisplayConfig.xml#L372
    """
    LANDSCAPE = 0       # normal
    PORTRAIT_RIGHT = 1   # 90°
    ROTATE_180 = 2      # 180°
    PORTRAIT_LEFT = 3  # 270°
    LANDSCAPE_FLIP = 4  # flipped
    FLIP_90 = 5         # 90° flipped
    FLIP_180 = 6        # 180° flipped
    FLIP_270 = 7        # 270° flipped


class LogicalMonitor(dict):
    def __init__(self, x, y, scale, transform, primary, linked_monitors_info, props):
        _locs = locals()
        _locs.pop('self')
        self.update(_locs)

    def to_struct(self):
        linked_monitor_info_structs = [linked.to_struct() for linked  in linked_monitors_info]
        struct = dbus.Struct(
            (
                dbus.Int32(self['x']),
                dbus.Int32(self['y']),
                dbus.Double(self['scale']),
                dbus.UInt32(self['transform']),
                dbus.Boolean(self['primary']),
                linked_monitor_info_structs,
            ),
            signature=None,
        )
        return struct


class MonitorInfo(dict):
    def __init__(self, connector, vendor, product, serial):
        _locs = locals()
        _locs.pop('self')
        self.update(_locs)

    def to_struct(self):
        struct = dbus.Struct(
            (
                dbus.String("HDMI-2"),
                dbus.String("1920x1080@60.000"),
                {}
            ),
            signature=None,
        )
        return struct


class PhysicalMonitor(dict):
    def __init__(self, monitor_info, monitor_modes, monitor_properties):
        _locs = locals()
        _locs.pop('self')
        self.update(_locs)


class MonitorMode(dict):
    def __init__(self, mode_id, mode_width, mode_height, mode_refresh, mode_preferred_scale, mode_supported_scales, mode_properties):
        _locs = locals()
        _locs.pop('self')
        self.update(_locs)


bus = dbus.SessionBus()

display_config_well_known_name = "org.gnome.Mutter.DisplayConfig"
display_config_object_path = "/org/gnome/Mutter/DisplayConfig"

display_config_proxy = bus.get_object(
    display_config_well_known_name, display_config_object_path
)
display_config_interface = dbus.Interface(
    display_config_proxy, dbus_interface=display_config_well_known_name
)

serial, physical_monitors, logical_monitors, properties = (
    display_config_interface.GetCurrentState()
)

if 1:
    import ubelt as ub
    for logical_values in logical_monitors:
        logical = LogicalMonitor(*logical_values)
        linked_monitors_info = []
        for linked_monitor_info_values in logical['linked_monitors_info']:
            monitor_info = MonitorInfo(*linked_monitor_info_values)
            linked_monitors_info.append(monitor_info)
        logical['linked_monitors_info'] = linked_monitors_info
        print(f'logical = {ub.urepr(logical, nl=3)}')

    for physical_values in physical_monitors:
        physical = PhysicalMonitor(*physical_values)
        monitor_info = physical['monitor_info']
        monitor_info = MonitorInfo(*monitor_info)
        physical['monitor_info'] = monitor_info
        modes = []
        for monitor_mode in physical['monitor_modes']:
            mode = MonitorMode(*monitor_mode)
            modes.append(mode)
        physical['monitor_modes'] = modes
        print(f'physical = {ub.urepr(physical, nl=3)}')

# updated_logical_monitors=[]
# for x, y, scale, transform, primary, linked_monitors_info, props in logical_monitors:
#     physical_monitors_config = []
#     for linked_monitor_connector, linked_monitor_vendor, linked_monitor_product, linked_monitor_serial in linked_monitors_info:
#         for monitor_info, monitor_modes, monitor_properties in physical_monitors:
#             monitor_connector, monitor_vendor, monitor_product, monitor_serial = monitor_info
#             if linked_monitor_connector == monitor_connector:
#                 for mode_id, mode_width, mode_height, mode_refresh, mode_preferred_scale, mode_supported_scales, mode_properties in monitor_modes:
#                     if mode_properties.get("is-current", False): # ( mode_properties provides is-current, is-preferred, is-interlaced, and more)
#                         physical_monitors_config.append(dbus.Struct([monitor_connector, mode_id, {}]))
#                         print(linked_monitor_connector)
#         # reset x for single monitor
#         # if linked_monitor_connector == 'HDMI-2':
#         #   x = 0
#     updated_logical_monitor_struct = dbus.Struct([dbus.Int32(x), dbus.Int32(y), dbus.Double(scale), dbus.UInt32(transform), dbus.Boolean(primary), physical_monitors_config])
#     updated_logical_monitors.append(updated_logical_monitor_struct)

# for updated_logical_monitor in updated_logical_monitors:
#     print(updated_logical_monitor)


if platform.node() == 'toothbrush':
    updated_logical_monitors = [
        # (top left)
        dbus.Struct(
            (
                dbus.Int32(0),
                dbus.Int32(0),
                dbus.Double(1.0),
                dbus.UInt32(DBusTransform.LANDSCAPE.value),
                dbus.Boolean(False),
                [
                    dbus.Struct(
                        (dbus.String("DP-0"), dbus.String("2560x1440@143.97325134277344"), {}),
                        signature=None,
                    )
                ],
            ),
            signature=None,
        ),
        # (right portrait)
        dbus.Struct(
            (
                dbus.Int32(2560),
                dbus.Int32((1440 + 1440) - 2560),
                dbus.Double(1.0),
                dbus.UInt32(DBusTransform.PORTRAIT_LEFT.value),
                dbus.Boolean(False),
                [
                    dbus.Struct(
                        (dbus.String("DP-2"), dbus.String("2560x1440@143.97325134277344"), {}),
                        signature=None,
                    )
                ],
            ),
            signature=None,
        ),
        # (bottom left)
        dbus.Struct(
            (
                dbus.Int32(0),
                dbus.Int32(1440),
                dbus.Double(1.0),
                dbus.UInt32(DBusTransform.LANDSCAPE.value),
                dbus.Boolean(True),
                [
                    dbus.Struct(
                        (dbus.String("DP-4"), dbus.String("2560x1440@143.97325134277344"), {}),
                        signature=None,
                    )
                ],
            ),
            signature=None,
        ),
    ]

# if len(logical_monitors) == 3:
#     updated_logical_monitors = [
#         dbus.Struct(
#             (
#                 dbus.Int32(0),
#                 dbus.Int32(0),
#                 dbus.Double(1.0),
#                 dbus.UInt32(0),
#                 dbus.Boolean(True),
#                 [
#                     dbus.Struct(
#                         (dbus.String("HDMI-2"), dbus.String("1920x1080@60.000"), {}),
#                         signature=None,
#                     )
#                 ],
#             ),
#             signature=None,
#         )
#     ]

properties_to_apply = {"layout_mode": properties.get("layout-mode")}


display_config_interface.ApplyMonitorsConfig(
    dbus.UInt32(serial),
    dbus.UInt32(DBusMethod.PROMPT.value),
    updated_logical_monitors,
    properties_to_apply,
)
