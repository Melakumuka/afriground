import logging
from local_db import CachedJob, CachedProfile
from cloud_client import CloudClient
from .iso_observer import IsolatedObserver

logger = logging.getLogger(__name__)

class ReadinessService:
    """Enforces Safran Pro 730 SX readiness checks before allowing cloud execution."""

    def __init__(self):
        self.iso_observer = IsolatedObserver()
        self.cloud_client = CloudClient()

    async def evaluate_and_push_readiness(
        self, 
        job: CachedJob, 
        profile: CachedProfile, 
        checklist_results: dict
    ) -> tuple[bool, str]:
        """
        Validates the 12 Safran safety checks + LCB + CRT SPOF.
        Returns (is_ready, reason_if_not).
        """
        
        # 1. Base 12 checks from the HTML form
        required_keys = [
            "mcs_ta_xml_synced",
            "rm_port_4000_stream",
            "lcb_not_engaged",
            "hpa_radiation_mask_armed",
            "stow_pins_free",
            "acu_tle_in_window",
            "rise_angle_ok",
            "interpass_gap_ok",
            "wind_weather_safe",
            "time_sync_ok",
            "rf_path_unmodified",
            "profile_certified"
        ]
        
        for key in required_keys:
            if not checklist_results.get(key):
                return False, f"Missing required checklist item: {key}"

        # 2. Check LCB status via observer
        lcb_status = await self.iso_observer.get_lcb_status()
        if lcb_status.get("lcb_engaged"):
            return False, "LCB is engaged, antenna is in Local Mode."

        # 3. Check Profile status
        if profile.status != "CERTIFIED" and profile.certification_state != "CERTIFIED":
            return False, f"Profile is not CERTIFIED (status: {profile.status})"

        # 4. Check TX SPOF rule
        if job.tx_requested:
            if not checklist_results.get("tx_redundancy_ack"):
                return False, "TX redundancy and radiation mask acknowledgement missing."
                
            crt = await self.iso_observer.get_crt_redundancy()
            if crt.get("state") == "spof":
                # Wait, the prompt says push NOT_READY with reason "crt_redundancy_loss"
                checklist_results["crt_redundancy_loss"] = True
                
                try:
                    await self.cloud_client.submit_readiness(
                        job.id, 
                        status="NOT_READY", 
                        checklist_results={"reason": "crt_redundancy_loss"}
                    )
                except Exception as e:
                    logger.error(f"Failed to push SPOF NOT_READY to cloud: {e}")
                
                return False, "S-Band TX SPOF active. Cannot execute TX job."
            
            # Decorate checklist results with redundancy for the cloud to evaluate
            checklist_results["crt_redundancy"] = crt.get("state")

        # All checks passed, push READY
        try:
            await self.cloud_client.submit_readiness(
                job.id, 
                status="READY", 
                checklist_results=checklist_results
            )
        except Exception as e:
            logger.error(f"Failed to submit READY to cloud: {e}")
            # we might want to return False if we can't talk to cloud, but per existing design
            # we fall back to local update
            pass

        return True, "Ready"
