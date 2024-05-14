class FeatureFlags:
    def __init__(self):
        self.flags = {
            "resourceQuotas": False,
            "timeouts": False,
            "concurrency": False,
            "inputValidation": False,
            "efficiency": False
        }

    def set_flag(self, feature, enabled):
        if feature in self.flags:
            self.flags[feature] = enabled
            return True
        return False

    def is_enabled(self, feature):
        return self.flags.get(feature, False)

feature_flags = FeatureFlags()
