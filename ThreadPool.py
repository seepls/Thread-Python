import threading


class ThreadPool():
   
   
    max_threads = 32 
    def __init__(self, num_threads, pool_size=0):
        """Spawn num_threads threads in the thread pool,
        and initialize three queues.
        """
        # pool_size = 0 indicates buffer is unlimited.
        num_threads = ThreadPool.max_threads \
            if num_threads > ThreadPool.max_threads \
            else num_threads
        self.in_queue = Queue.Queue(pool_size)
        self.out_queue = Queue.Queue(pool_size)
        self.err_queue = Queue.Queue(pool_size)
        self.workers = {}
        for i in range(num_threads):
            worker = Worker(self.in_queue, self.out_queue, self.err_queue)
            self.workers[i] = worker
            
    def add_task(self, callback, *args, **kwds):
        command = 'process' 
        self.in_queue.put((command, callback, args, kwds))

    def _get_results(self, queue):
        '''Generator to yield one after the others all items currently
           in the queue, without any waiting
        '''
        try:
            while True:
                yield queue.get_nowait()
        except Queue.Empty:
            raise StopIteration
    
    def get_task(self):
        return self.out_queue.get()    

    def show_results(self):
        for result in self._get_results(self.out_queue):
            print 'Result:', result
        
    def show_errors(self):
        for etyp, err in self._get_results(self.err_queue):
            print 'Error:', etyp, err

    def destroy(self):
        # order is important: first, request all threads to stop...:
        for i in self.workers:
            self.workers[i].dismiss()
        # ...then, wait for each of them to terminate:
        for i in self.workers:
            self.workers[i].join()
        # clean up the workers from now-unused thread objects
        del self.workers
