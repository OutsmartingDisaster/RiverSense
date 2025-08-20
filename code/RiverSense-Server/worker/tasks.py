import os
import datetime
from celery import Celery
from database.models import GNSSData
from database.session import get_db_session

app = Celery('tasks', broker='redis://redis:6379/0')

@app.task
def process_raw_data(raw_data):
    """
    Celery task to process raw GNSS data.
    """
    db_session = get_db_session()
    try:
        new_data = GNSSData(
            raw_data=raw_data,
            processing_status="pending"
        )
        db_session.add(new_data)
        db_session.commit()
        convert_to_rinex.delay(new_data.id)
    except Exception as e:
        print(f"Error in process_raw_data task: {e}")
        db_session.rollback()
    finally:
        db_session.close()

@app.task
def convert_to_rinex(data_id):
    """
    Celery task to convert raw GNSS data to RINEX format.
    """
    db_session = get_db_session()
    gnss_data = db_session.query(GNSSData).filter_by(id=data_id).first()

    if not gnss_data:
        print(f"Error: GNSSData with id {data_id} not found.")
        return

    try:
        gnss_data.processing_status = "processing"
        db_session.commit()

        # RINEX Conversion
        now = datetime.datetime.now()
        rinex_filename = now.strftime("%Y%m%d_%H%M%S") + ".rnx"
        rinex_file_path = os.path.join("/data/rinex_files/", rinex_filename)

        # Placeholder for actual conversion logic
        with open(rinex_file_path, "w") as f:
            f.write(gnss_data.raw_data)

        gnss_data.rinex_file_path = rinex_file_path
        gnss_data.processing_status = "completed"
        db_session.commit()

    except Exception as e:
        gnss_data.processing_status = "failed"
        db_session.commit()
        print(f"Error in convert_to_rinex task: {e}")
    finally:
        db_session.close()