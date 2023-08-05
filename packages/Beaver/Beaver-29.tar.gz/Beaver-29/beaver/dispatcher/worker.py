# -*- coding: utf-8 -*-
import multiprocessing
import Queue
import signal
import sys

from beaver.config import BeaverConfig
from beaver.queue import run_queue
from beaver.ssh_tunnel import create_ssh_tunnel
from beaver.utils import setup_custom_logger, REOPEN_FILES
from beaver.worker.worker import Worker


def run(args):
    logger = setup_custom_logger('beaver', args)

    beaver_config = BeaverConfig(args, logger=logger)
    queue = multiprocessing.Queue(beaver_config.get('max_queue_size'))

    worker = None
    ssh_tunnel = create_ssh_tunnel(beaver_config, logger=logger)

    def cleanup(signalnum, frame):
        sig_name = tuple((v) for v, k in signal.__dict__.iteritems() if k == signalnum)[0]

        logger.info('{0} detected'.format(sig_name))
        logger.info('Shutting down. Please wait...')

        if worker is not None:
            logger.info('Closing worker...')
            try:
                worker.close()
            except RuntimeError:
                pass

        try:
            queue.put_nowait(('exit', ()))
        except Queue.Full:
            pass

        if ssh_tunnel is not None:
            logger.info('Closing ssh tunnel...')
            ssh_tunnel.close()

        logger.info('Shutdown complete.')
        return sys.exit(signalnum)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGQUIT, cleanup)

    def create_queue_consumer():
        process_args = (queue, beaver_config, logger)
        proc = multiprocessing.Process(target=run_queue, args=process_args)

        logger.info('Starting queue consumer')
        proc.start()
        return proc

    while 1:
        try:
            if REOPEN_FILES:
                logger.debug('Detected non-linux platform. Files will be reopened for tailing')

            logger.info('Starting worker...')
            worker = Worker(beaver_config, queue_consumer_function=create_queue_consumer, callback=queue.put, logger=logger)

            logger.info('Working...')
            worker.loop()

        except KeyboardInterrupt:
            pass
