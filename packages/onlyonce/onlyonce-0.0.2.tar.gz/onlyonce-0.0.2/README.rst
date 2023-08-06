=========
Only Once
=========

A simple Lock Dir system. Creating Dirs is atomic, which is useful for
locking things to only let one version of a process start.

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

This system is NOT designed to replace large daemonising clever init/systemd whatever stuff.
It was written simply to let us run rsync & other processess around the campus without
it being possible for multiple versions of the script to be running at once.

Ideally, you should only be running ONE process with this at a time.

Have fun. :-)
