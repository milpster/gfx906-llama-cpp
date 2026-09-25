import gdb
import threading

BT_PATH = '/home/srcds/dev/uf3_rocm6.1_llama.cpp/bench/logs/q38speed/tenancy-selective-mlock-gdb/bt.log'

def on_stop(event):
    try:
        with open(BT_PATH, 'w') as f:
            f.write(gdb.execute('thread apply all bt 20', to_string=True))
    finally:
        gdb.execute('set confirm off')
        gdb.execute('kill')
        gdb.execute('quit')

gdb.events.stop.connect(on_stop)

def poke():
    gdb.post_event(lambda: gdb.execute('interrupt'))

threading.Timer(160, poke).start()
