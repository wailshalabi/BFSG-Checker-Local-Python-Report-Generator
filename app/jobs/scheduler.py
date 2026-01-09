from app.db.repo import ScanRepo

def enqueue_scan(url: str) -> int:
    return ScanRepo.create_scan(url)
