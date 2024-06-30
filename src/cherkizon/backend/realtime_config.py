from src.mybootstrap_core_itskovichanton.realtime_config import RealTimeConfigEntry, IntRealTimeConfigEntry
from src.mybootstrap_ioc_itskovichanton.ioc import bean


@bean
class AlertIfDiskUsagePercentBiggerThanRealTimeConfigEntry(IntRealTimeConfigEntry):
    key = "alert_if_disk_usage_percent_greater_than"
    description = "высылать алерт если использование диска больше чем (%)"
    category = "Алерты"
    value = 80
    watched = True


@bean
class AlertIfRAMUsagePercentBiggerThanRealTimeConfigEntry(IntRealTimeConfigEntry):
    key = "alert_if_ram_usage_percent_greater_than"
    description = "высылать алерт если использование RAM больше чем (%)"
    category = "Алерты"
    value = 90
    watched = True