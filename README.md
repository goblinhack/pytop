pytop
=====
This is a Python based "top" like tool for linux with historical graphing for processes.

- Python 2 version: pytop2
- Python 3 version: pytop3

Allows you to select individual processes (j/k) and receive a histogram of the CPU usage for that process.

```bash
usage: pytop2 [-h] [-p PID] [-one] [-i IGNORE] [-d DELAY] [-a] [-c] [-H]

optional arguments:
  -h, --help            show this help message and exit
  -p PID, --pid PID     filter to a given pid
  -one, --one           one shot and then exit, like top -b
  -i IGNORE, --ignore IGNORE
                        filter idle processes after x seconds of inaction
  -d DELAY, --delay DELAY
                        delay between system samples
  -a, --all             include all processes, including idle ones
  -c, --no-color        disable color output
  -H, --no-histogram    disable histogram
```

![Alt text](screenshot.png?raw=true "")
