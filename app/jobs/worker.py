import time
import traceback

from app.db.session import init_db
from app.db.repo import ScanRepo
from app.core.scan_service import run_scan_job

POLL_SECONDS = 1.5

def main():
    init_db()
    print("Worker started. Polling for queued scans...")

    while True:
        scan_id = ScanRepo.claim_next_queued_scan()
        if scan_id is None:
            time.sleep(POLL_SECONDS)
            continue

        try:
            run_scan_job(scan_id)
        except Exception as e:
            traceback.print_exc()
            ScanRepo.set_scan_failed(scan_id, error_message=str(e))

if __name__ == "__main__":
    main()
