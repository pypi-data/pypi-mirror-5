=========
Only Once
=========

A simple Lock Dir system. Creating Dirs is atomic, which is useful for
locking things to only let one version of a process start.

A directory is created, say called 'lock'.
Inside this directory will be a PID file, which keeps the PID of the running process.
If the process dies, or is killed, then the whole directory will be deleted, allowing
the task to be run again later, and not leaving clutter around the place.

------
Usage:
------

Basic usage should be as simple as ::

    try:
        with onlyonce.SingleProcessLock('/tmp/lock') as lock:
            lock.run(['rsync', '-avz', '/here', 'there'])
    except onlyonce.StillRunning as err:
        print str(err)

if you want to do something special with running the task (redirecting output, etc)
then you can use lock.run with the same arguments as subprocess.Popen (they'll all get
passed through). So: ::

    lock.run(['rsync','...'], stderr=...)

Should work fine.

If you *dont* want to block and wait for the process to finish, then you'll need to
go a bit more low level: ::


    try:
        with onlyonce.SingleProcessLock('/tmp/lock') as lock:
        process = Popen(['rsync', '-avz', '/here', 'there'], stderr=whatever ...)
        lock.write_pid(process.pid)
    except ...

Which doesn't block.

------
Notes:
------

You can 'kill' the task, and onlyonce will clean up the lock dir for you.  If you 'kill -9' the
script, however, python freaks out and quits before the script can do anything. Sorry!

This system is NOT designed to replace large daemonising clever init/systemd whatever stuff.
It was written simply to let us run rsync & other processess around the campus without
it being possible for multiple versions of the script to be running at once.

Ideally, you should only be running ONE process with this at a time.

Have fun. :-)
