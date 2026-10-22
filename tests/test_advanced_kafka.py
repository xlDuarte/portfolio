"""Optional *real broker* integration; skipped outside RUN_ADVANCED_KAFKA=1."""
import os
import tempfile
import unittest
from pathlib import Path
from advanced_batch.kafka_bus import publish,consume,TOPIC
from advanced_batch.engine import connect,read_events

@unittest.skipUnless(os.environ.get("RUN_ADVANCED_KAFKA")=="1","requires live Redpanda broker")
class TestKafkaBroker(unittest.TestCase):
    def test_ack_produce_and_durable_consume(self):
        with tempfile.TemporaryDirectory() as tmp:
            name="advanced-streams-ci-test-091"
            published=publish(91,count=24,bootstrap="localhost:19092",topic=name)
            self.assertEqual(published["published"],24)
            db=Path(tmp)/"stream.db"
            received=consume(str(db),bootstrap="localhost:19092",
                             topic=name,max_messages=24,group_id="advanced-ci-tests")
            self.assertEqual(received["messages_consumed"],24)
            self.assertEqual(received["inserted"],24)
            with connect(db) as conn:
                self.assertEqual(len(read_events(conn,91)),24)
if __name__=="__main__":unittest.main()
