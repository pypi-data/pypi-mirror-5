import Queue
import sys
import threading

import abstract
import rawapi

__all__ = [
    'Scanner',
    'ScannerOption',
    'get_devices',
]

class SaneAction(object):
    def __init__(self, func, **kwargs):
        self.func = func
        self.args = kwargs
        self.result = None
        self.exception = None
        self.__sem = threading.Semaphore(0)

    def start(self):
        global sane_thread
        global sane_action_queue

        if sane_thread == None or not sane_thread.is_alive():
            raise rawapi.SaneException("Sane thread died unexpectidly !")
        sane_action_queue.put(self)

    def wait(self):
        self.start()
        self.__sem.acquire()
        if self.exception != None:
            raise self.exception
        return self.result

    def do(self):
        try:
            sys.stdout.flush()
            self.result = self.func(**self.args)
        except Exception, exc:
            self.exception = exc
        self.__sem.release()


class SaneWorker(threading.Thread):
    def run(self):
        global sane_action_queue
        while True:
            try:
                action = sane_action_queue.get(block=True, timeout=1)
                action.do()
            except Queue.Empty:
                if not parent_thread.is_alive():
                    return


parent_thread = threading.current_thread()
sane_action_queue = Queue.Queue()
# TODO(Jflesch): Lock for sane_thread*
sane_thread = SaneWorker()
sane_thread.start()


def sane_init():
    return SaneAction(abstract.sane_init).wait()


def sane_exit():
    return SaneAction(abstract.sane_exit).wait()


class ScannerOption(object):
    _abstract_opt = None

    idx = 0
    name = ""
    title = ""
    desc = ""
    val_type = rawapi.SaneValueType(rawapi.SaneValueType.INT)
    unit = rawapi.SaneUnit(rawapi.SaneUnit.NONE)
    size = 4
    capabilities = rawapi.SaneCapabilities(rawapi.SaneCapabilities.NONE)

    constraint_type = rawapi.SaneConstraintType(rawapi.SaneConstraintType.NONE)
    constraint = None

    def __init__(self, scanner, idx):
        self.idx = idx
        self._abstract_opt = abstract.ScannerOption(scanner._abstract_dev, idx)

    @staticmethod
    def build_from_abstract(scanner, abstract_opt):
        opt = ScannerOption(scanner, abstract_opt.idx)
        opt._abstract_opt = abstract_opt
        opt.name = abstract_opt.name
        opt.title = abstract_opt.title
        opt.desc = abstract_opt.desc
        opt.val_type = abstract_opt.val_type
        opt.unit = abstract_opt.unit
        opt.size = abstract_opt.size
        opt.capabilities = abstract_opt.capabilities
        opt.constraint_type = abstract_opt.constraint_type
        opt.constraint = abstract_opt.constraint
        return opt

    def _get_value(self):
        return SaneAction(self._abstract_opt._get_value).wait()

    def _set_value(self, new_value):
        SaneAction(self._abstract_opt._set_value, new_value=new_value).wait()

    value = property(_get_value, _set_value)


class ScanSession(object):
    def __init__(self, scanner, multiple):
        self._session = SaneAction(scanner._abstract_dev.scan, multiple=multiple).wait()

    def read(self):
        SaneAction(self._session.read).wait()

    def get_nb_img(self):
        return SaneAction(self._session.get_nb_img).wait()

    def get_img(self, idx=0):
        return SaneAction(self._session.get_img, idx=idx).wait()

    def __del___(self):
        SaneAction(self._session._del).start()


class Scanner(object):
    def __init__(self, name=None,
                 vendor="Unknown", model="Unknown", dev_type="Unknown",
                 abstract_dev=None):
        if abstract_dev == None:
            abstract_dev = abstract.Scanner(name)
        else:
            vendor = abstract_dev.vendor
            model = abstract_dev.model
            dev_type = abstract_dev.dev_type
        self._abstract_dev = abstract_dev
        self.name = name
        self.vendor = vendor
        self.model = model
        self.dev_type = dev_type
        self.__options = None # { "name" : ScannerOption }

    @staticmethod
    def build_from_abstract(abstract_dev):
        return Scanner(abstract_dev.name, abstract_dev=abstract_dev)

    def _get_options(self):
        if self.__options != None:
            return self.__options
        options = SaneAction(self._abstract_dev._get_options).wait()
        ar_options = [ScannerOption.build_from_abstract(self, opt)
                      for opt in options.values()]
        options = {}
        for opt in ar_options:
            options[opt.name] = opt
        self.__options = options
        return self.__options

    options = property(_get_options)

    def scan(self, multiple=False):
        return ScanSession(self, multiple)

    def __del__(self):
        SaneAction(self._abstract_dev._del)

    def __str__(self):
        return ("Scanner '%s' (%s, %s, %s)"
                % (self.name, self.vendor, self.model, self.dev_type))


def get_devices(local_only=False):
    abs_devs = SaneAction(abstract.get_devices, local_only=local_only).wait()
    abs_th_devs = [Scanner.build_from_abstract(abs_dev) for abs_dev in abs_devs]
    return abs_th_devs
