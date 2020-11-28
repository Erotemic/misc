import ubelt as ub


class Coarse(object):
    @classmethod
    def coerce(cls, data):
        # print('Coarse.coerce: cls = {!r}, data={!r}'.format(cls, data))
        if isinstance(data, cls):
            return data
        else:
            return None


class Fine_V1(Coarse):
    @classmethod
    def coerce(cls, data):
        # print('Fine.coerce: cls = {!r}, data={!r}'.format(cls, data))
        return super().coerce(data)


class Fine_V2(Coarse):
    pass


def main():
    coarse = Coarse()
    fine1 = Fine_V1()
    fine2 = Fine_V2()
    print('coarse = {!r}'.format(coarse))
    print('fine1 = {!r}'.format(fine1))
    print('fine2 = {!r}'.format(fine2))

    cls_list = [Coarse, Fine_V1, Fine_V2]

    for data_cls in cls_list:
        data = data_cls()
        print('data_cls = {!r}'.format(data_cls))

        for coerce_cls in cls_list:
            res = coerce_cls.coerce(data)
            print('    child_cls = {}, {}'.format(ub.repr2(coerce_cls, nl=1), res))

    Coarse.coerce(fine1)
    Coarse.coerce(fine2)


if __name__ == '__main__':
    main()
