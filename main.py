import sys
import math
import select
import queue
import re
import curses
import threading
import time
import termios, tty
#TODO: sudo prompt is always on the tty not terminal.

def reader(q):
    for line in sys.stdin:
        q.put(line)
    q.put(None)
def windows(stdscr):

    stdscr.nodelay(True)
    curses.curs_set(0)
    stdscr.clear()
    curses.cbreak()
    h, w = stdscr.getmaxyx()
    q = queue.Queue()
    t = threading.Thread(target=reader, args=(q,), daemon=True)
    t.start()

    mainwin = curses.newwin(h - 2, w, 0,     0)   # rows 1..h-2
    emerging_win = curses.newwin(1, w, h - 2, 0)  # row h-2
    installing_win = curses.newwin(1, w, h - 1, 0)  # row h-1
    mainwin.scrollok(True)
    mainwin.idlok(True)
    emerging_cur = emerging_total = installing_cur = installing_total = 0
    try:
        tty_fd = open("/dev/tty", 'r')
        fd = tty_fd.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)
    except:
        #TODO: improved error message
        tty_fd = None
    def draw_bars():
        emerging_win.erase()
        emerge_label = f"Emerging: {emerging_cur} / {emerging_total} "[:w - 1]
        els = len(emerge_label)
        emerging_win.addstr(0, 0, emerge_label)

        if emerging_total > 0 and w > els + 2:
            e_bar_width = w - els - 3  # -3 for brackets and space
            emerging_ratio = emerging_cur / emerging_total
            emerging_progress = min(math.floor(emerging_ratio * e_bar_width), e_bar_width)
            emerging_bar = "[" + ("#" * emerging_progress) + (" " * (e_bar_width - emerging_progress)) + "]"
            emerging_win.addstr(0, els, emerging_bar)

        emerging_win.refresh()
        
        installing_win.erase()
        install_label = f"Installing: {installing_cur} / {installing_total} "[:w - 1]
        ils = len(install_label)
        installing_win.addstr(0, 0, install_label)

        if installing_total > 0 and w > ils + 2:
            i_bar_width = w - ils - 3  # -3 for brackets and space
            installing_ratio = installing_cur / installing_total
            installing_progress = min(math.floor(installing_ratio * i_bar_width), i_bar_width)
            installing_bar = "[" + ("#" * installing_progress) + (" " * (i_bar_width - installing_progress)) + "]"
            installing_win.addstr(0, ils, installing_bar)

        installing_win.refresh()

    while True:
        if tty_fd:
            ready, _, _ = select.select([tty_fd], [], [], 0.02)
            if ready:
                ch = tty_fd.read(1)
                if ch and (ch == 'q' or ch == 'Q'):
                    termios.tcsetattr(tty_fd, termios.TCSADRAIN, old_settings)
                    tty_fd.close()
                    return

        try:
            line = q.get_nowait()
        except queue.Empty:
            time.sleep(0.02)
            continue
        if line is None:
            break
        mainwin.addstr(line[:w-1])
        mainwin.refresh()

        total_match = re.search(r"Total:\s*(\d+)\s+package", line)
        if total_match:
            emerging_total = installing_total = int(total_match.group(1))
        emerging_match = re.search(r"\(\s*(\d+)\s+of\s+(\d+)\s*\)", line)
        if emerging_match:
            emerging_cur = int(emerging_match.group(1))

        installing_match = re.search(r"Installing\s+\(\s*(\d+)\s+of\s+(\d+)\s*\)", line, re.IGNORECASE)
        if installing_match:
            installing_cur = int(installing_match.group(1))

        draw_bars()
    installing_win.clear()
    emerging_win.clear()
    emerging_win.refresh()
    installing_win.addstr(0, 0, "emerge finished press 'q' to quit")
    installing_win.refresh()
    stdscr.nodelay(False)
    while True:
        ch = tty_fd.read(1)
        if ch and (ch == 'q' or ch == 'Q'):
            termios.tcsetattr(tty_fd, termios.TCSADRAIN, old_settings)
            tty_fd.close()
            return



if __name__ == "__main__":
    curses.wrapper(windows)