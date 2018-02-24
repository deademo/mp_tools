import logging
import time

from discovery import first
from upload import upload


logger = logging.getLogger('upload_test')
logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)


def make_test_file(size):
    return 'A' * int(size)


def do_test(ip, file_size_kb, test_count=5, port=80):
    file_size = file_size_kb*1024
    time_results = []

    for i in range(test_count):
        start_time = time.time()
        upload(ip, 'test_file', make_test_file(file_size), port=port, timeout=3600)
        delta_time = time.time() - start_time
        time_results.append(delta_time)

        log_tpl = 'Test {i}/{total_tests}: finished_for={delta_time:0.2f}s file_size={file_size:0.2f}kb'
        logger.debug(log_tpl.format(
            i=i+1,
            total_tests=test_count,
            delta_time=delta_time,
            file_size=file_size/1024
        ))

    average_time = sum(time_results)/len(time_results)
    logger.debug('Done: avg_time={:0.2f}s, file_size={:0.2f}kb, speed={:0.2f}kb/s'.format(average_time, file_size/1024, file_size/average_time/1024))

    return average_time


def main():
    ip = first()
    logger.debug('Found device ip: {}'.format(ip))

    start_time = time.time()

    test_cases = [
        (1/1024, 20),
        (1, 20),
        (5, 20),
        (10, 10),
        (25, 10),
        (50, 5),
    ]
    results = []
    for file_size_kb, test_count in test_cases:
        time_result = do_test(ip, file_size_kb, test_count)
        results.append((time_result, file_size_kb, test_count))

    end_time = time.time()
    delta_time = end_time - start_time
    logger.info('File size |   Time |      Speed | Test count')
    for time_result, size_kb, test_count in results:
        speed = size_kb/time_result
        logger.info('{:7.2f}kb | {:5.2f}s | {:6.2f}kb/s | {:<2}'.format(size_kb, time_result, speed, test_count))
    logger.info('Finished for {:0.2f}s'.format(delta_time))

if __name__ == '__main__':
    main()
