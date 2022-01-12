"""
A bunch of stuff you can do with datetimes in python
"""
import datetime


def pathsafe_isoformat(dt):
    from datetime import timedelta
    def _format_offset(off):
        s = ''
        if off is not None:
            if off.days < 0:
                sign = "-"
                off = -off
            else:
                sign = "+"
            hh, mm = divmod(off, timedelta(hours=1))
            mm, ss = divmod(mm, timedelta(minutes=1))
            s += "%s%02d:%02d" % (sign, hh, mm)
            if ss or ss.microseconds:
                s += ":%02d" % ss.seconds

                if ss.microseconds:
                    s += '.%06d' % ss.microseconds
        return s

    text = dt.strftime('%Y%m%dT%H%M%S')
    if dt.tzinfo is not None:
        off = dt.utcoffset()
        suffix = _format_offset(off)
        if suffix == '+00:00':
            # TODO: use codes for offsets to remove the plus sign if possible
            suffix = 'Z'
            text += suffix
    return text


items = []
dt = datetime.datetime.now()
items.append(dt)
dt = datetime.datetime.utcnow()
items.append(dt)
dt = dt.replace(tzinfo=datetime.timezone.utc)
items.append(dt)


for dt in items:
    print('dt = {!r}'.format(dt))
    # ISO format is cool, but it doesnt give much control
    print(dt.isoformat())
    # Need a better version
    print(pathsafe_isoformat(dt))
