from event_bus import EventBus

EVENT_DEPLOY_HEALTHCHECK_FAILED = "EVENT_DEPLOY_HEALTHCHECK_FAILED"
EVENT_DEPLOY_HEALTHCHECK_FIXED = "EVENT_DEPLOY_HEALTHCHECK_FIXED"
EVENT_DEPLOY_RESTARTED = "EVENT_DEPLOY_RESTARTED"
EVENT_DEPLOY_STOPPED = "EVENT_DEPLOY_STOPPED"
EVENT_MACHINE_HEALTHCHECK_BAD = "EVENT_MACHINE_HEALTHCHECK_BAD"
EVENT_MACHINE_HEALTHCHECK_FIXED = "EVENT_MACHINE_HEALTHCHECK_BAD"

EVENT_MACHINE_DISK_OVER_USED = "EVENT_MACHINE_DISK_OVER_USED"
EVENT_MACHINE_RAM_OVER_USED = "EVENT_MACHINE_RAM_OVER_USED"

event_bus = EventBus()
