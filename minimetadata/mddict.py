#!/usr/bin/python

class MDDict (dict):
    """Implementation of perl's autovivification feature.
    (via
    http://stackoverflow.com/questions/2600790/multiple-levels-of-collection-defaultdict-in-python)"""

    def __init__(self, toplevel=None):
        super(MDDict, self).__init__()

        self.toplevel = toplevel if toplevel else self
        self.closed = False

    def close(self):
        self.closed = True

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            if self.closed or (
                    self.toplevel is not None and self.toplevel.closed):
                raise
            
            value = self[item] = type(self)(toplevel=self.toplevel)
            return value

    def parse(self, data):
        for k,v in data.items():
            target = self
            for kk in k.split('/')[:-1]:
                target = target[kk]
            target[k.split('/')[-1]] = v

    def lookup(self, path):
        target = self

        if len(path) > 0:
            for kk in path.split('/'):
                target = target[kk]

        return target

if __name__ == '__main__':
    global cfg
    cfg = { 'metadata': {
        'public-keys/0/openssh-key': 'ssh-rsa ...stuff...',
        'public-keys/1/openssh-key': 'ssh-rsa ...more...',
        'instance-id': 'i-01234',
        }
    }
    
    metadata = MDDict()
    metadata.parse(cfg['metadata'])



