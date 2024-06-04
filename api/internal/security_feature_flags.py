# security_feature_flags.py
import time

class FeatureFlags:
    def __init__(self):
        self.flags = {
            "resourceQuotas": False,
            "timeouts": False,
            "inputValidation": False,
            "efficiency": False
        }
        # Initialize usage counters with the last reset time
        self.usage_counters = {
            "addressValidationCount": 0,
            "lastResetTime": time.time()
        }

    def set_flag(self, feature, enabled):
        if feature in self.flags:
            self.flags[feature] = enabled
            if enabled and feature == "resourceQuotas":
                self.reset_usage_counters()
            return True
        return False

    def is_enabled(self, feature):
        return self.flags.get(feature, False)

    def reset_usage_counters(self):
        self.usage_counters['addressValidationCount'] = 0
        self.usage_counters['lastResetTime'] = time.time()

    def check_and_increment_quota(self):
        if self.flags['resourceQuotas']:
            # Check if 5 seconds have passed since the last reset
            if time.time() - self.usage_counters['lastResetTime'] > 8:
                self.reset_usage_counters()

            # Allow up to 5 requests per 5 seconds
            if self.usage_counters['addressValidationCount'] < 5:
                self.usage_counters['addressValidationCount'] += 1
                return True
            return False
        return True

feature_flags = FeatureFlags()
