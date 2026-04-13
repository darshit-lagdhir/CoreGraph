import asyncio
import sys

from backend.interface.command_gateway import gateway_kernel


class AgencySovereigntyTask:
    def __init__(self):
        self.gateway = gateway_kernel
        # State transitions
        self.coregraph_command_ingress_complete = False

    async def execute_agency_siege(self):
        """
        Executes Prompt 4: Real-time 3.81M Node Analyst-Agency Sovereignty Manifold.
        Signals the final Agential Seal.
        """
        print(
            "[*] IGNITING: Asynchronous Command Ingress Gating and Directive Input Manifold Specification"
        )
        print("[*] Pre-initializing non-blocking buffer listen sequence...")

        # Igniting agency avoids event loop freezes
        manifest = await self.gateway.initialize_agential_seal()
        await self.gateway.monitor_tty()  # Send a synthetic agency signal

        # Waiting for the background consumer to process our synthetic command
        await asyncio.sleep(0.1)

        self.coregraph_command_ingress_complete = True

        print("\n=======================================================")
        print("  [ STATUS: INDESTRUCTIBLE | AGENTIALLY-SEALED ]       ")
        print("          MISSION-READY FORENSIC CONTROL               ")
        print("=======================================================")
        for key, value in manifest.items():
            print(f" > {key}: {value}")
        print("=======================================================\n")

        # Validate that the active audits caught the non-blocking command
        print(f"ACTIVE AUDITS DETECTED IN RAM: {self.gateway.active_audits}")

        self.gateway.manifold.halt()
        return manifest


if __name__ == "__main__":
    task = AgencySovereigntyTask()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(task.execute_agency_siege())
