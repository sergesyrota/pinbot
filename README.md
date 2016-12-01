```bash
brew install --HEAD opencv3 --with-contrib
brew install webp

pip install --upgrade pip
pip install virtualenv

echo /usr/local/opt/opencv3/lib/python2.7/site-packages >> /usr/local/lib/python2.7/site-packages/opencv3.pth

# Reload terminal

cd path/to/pinbot

virtualenv -p `which python` .virtualenv
source .virtualenv/bin/activate

pip install -r requirements.txt

```

### Debugging

For debugging place following in the code:

```python
import ipdb; ipdb.set_trace()
```

For debugging serial communication:

```
$ socat -d -d pty,raw,echo=0 pty,raw,echo=0
2016/11/29 08:41:25 socat[43296] N PTY is /dev/ttys003
2016/11/29 08:41:25 socat[43296] N PTY is /dev/ttys004
```
This will create forwarding between 2 serial interfaces. Then you can write into one, and read from another.

Flipper detect frame numbers:

When we want to train flipper on recorded video, we need to know frame numbers that can be considered as "pressing
the button." Both arguments need to be passed (otherwise it doesn't make much sense).

--debug-right 243,271,314,346,378,410,442,472,518
--debug-left 590,621,653,686,718,749,781
