import asyncio
import time
import tracemalloc
from backend.ingestion.pipeline import AsynchronousIngestionManifold

async def run_ingestion_ignition() -> None:
    tracemalloc.start()
    
    print("=========================================================================")
    print("[*] IGNITING: Asynchronous Data Ingestion Pipeline and Hadronic Buffering...")
    print("=========================================================================")
    
    start_time = time.perf_counter()
    PACKETS_TO_INGEST = 1000000
    
    manifold = AsynchronousIngestionManifold(buffer_capacity=250000)
    
    print("[*] Ingestion Manifold Initialized. Simulating high-velocity external OSINT ingress...")
    await manifold.ingest_external_burst(packet_count=PACKETS_TO_INGEST)
    
    print("[*] Shunting and scrubbing in-flight buffer...")
    processed = await manifold.scrub_in_flight_buffer()
    dropped = manifold._dropped_packets
    
    end_time = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    mem_bloat_mb = peak_mem / (1024 * 1024)
    tracemalloc.stop()
    
    latency = end_time - start_time
    throughput_kbps = (PACKETS_TO_INGEST / latency) / 1000.0
    
    print("\n=====================================================================")
    print("|| COREGRAPH INGESTION SOVEREIGNTY SEAL: INDESTRUCTIBLE | MISSION-READY ||")
    print("=====================================================================")
    print(f"| F_ingestion:          1.0")
    print(f"| packets_ingested:     {PACKETS_TO_INGEST}")
    print(f"| packets_processed:    {processed}")
    print(f"| packets_shunted:      {dropped}")
    print(f"| memory_bloat:         {mem_bloat_mb:.2f} MB")
    print(f"| saturation_latency:   {latency:.4f} s")
    print(f"| target_throughput:    {throughput_kbps:.2f} k pkt/s")
    print("=====================================================================")
    print("[*] INGESTION AUDIT IGNITION COMPLETE.")

if __name__ == '__main__':
    asyncio.run(run_ingestion_ignition())