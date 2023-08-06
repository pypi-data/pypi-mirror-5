
import sys
import time
import traceback
import threading

timer = time.perf_counter if hasattr(time, "perf_counter") else time.clock

class Wrapper:
    def __init__(self, workload):
        self.workload = workload

    def __repr__(self):
        return repr(self.workload)

class ExceptionWrapper(Wrapper):
    def __call__(self):
        try:
            self.workload()
        except:
            sys.stderr.write("Exception in {thread} at {time}\n".format(
                thread=threading.current_thread().name,
                time=time.strftime("%c")
            ))
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()

class WorkloadWrapper(Wrapper):
    time = 0.0

    def __call__(self):
        tp1 = timer()
        self.workload()
        self.time = timer() - tp1
