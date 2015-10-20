import rumps

# DEBUG purposes
rumps.rumps._NOTIFICATIONS = False


class DictConfig(object):

    def __init__(self):
        self._data = {
            'whale': {
                'show_notifications': True,
                'check_interval': 30,
            },
            'twitch': {
                'access_token': None
            }
        }

    def __getitem__(self, item):
        return self._data.get(item, None)

    def __setitem__(self, key, value):
        self._data[key] = value


class Worker(rumps.App):

    def __init__(self):
        super(Worker, self).__init__(name='Timer', title='T')
        self.timer = None
        self.timer_item = rumps.MenuItem(title='Start', callback=self.start, key='timer_item')
        self.menu.add(self.timer_item)

    def init_timer(self):
        self.timer = rumps.Timer(callback=self.callme, interval=5)
        self.timer.interval

    @rumps.clicked('Start')
    def start(self, sender):
        if not self.timer:
            self.init_timer()

        self.timer.start()
        print 'timer started'

        self.timer_item.title = 'Stop'
        self.timer_item.set_callback(self.stop)
        # self.menu.update([self.timer_item])

    def stop(self, sender):
        if self.timer and self.timer.is_alive():
            self.timer.stop()
            print 'timer stopped'

        self.timer_item.title = 'Start'
        self.timer_item.set_callback(self.start)

    def callme(self, sender):
        print 'Called by %s' % sender

if __name__ == '__main__':
    # worker = Worker()
    # worker.run()

    cfg = DictConfig()
    print cfg['whale']['check_interval']
    cfg['whale']['check_interval'] = 600
    print cfg['whale']['check_interval']
