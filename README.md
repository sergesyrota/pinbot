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
