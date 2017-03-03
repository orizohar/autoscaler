from custom_auto_scaler import CustomAutoScaler
import config
import time

def main():
    scaler = CustomAutoScaler(config.AZURE_CLIENT_ID,
        config.AZURE_CLIENT_SECRET,
        config.AZURE_TENANT_ID,
        config.SUBSCRIPTION_ID)    
    scaler.run(config.VMSS_LOW_THRESHOLD, 
        config.VMSS_HIGH_THRESHOLD,
        config.VMSS_SCALE_DOWN_BY,
        config.VMSS_SCALE_UP_BY,
        config.VMSS_MIN_CAPACITY,
        config.VMSS_MAX_CAPACITY)
    if config.RUN_ONCE:
        return
    while True:
        time.sleep(config.INTERVAL_IN_SEC)
        scaler.run(config.VMSS_LOW_THRESHOLD, 
            config.VMSS_HIGH_THRESHOLD,
            config.VMSS_SCALE_DOWN_BY,
            config.VMSS_SCALE_UP_BY,
            config.VMSS_MIN_CAPACITY,
            config.VMSS_MAX_CAPACITY)

if __name__ == "__main__":
    main()
