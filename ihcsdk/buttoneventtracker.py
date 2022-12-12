from datetime import datetime


class ButtonEventTracker:
    """
    Class for tracking button up/down events as multi or long presses.
    """

    def __init__(self, resource_id, name, value):

        self.MULTI_CLICK_MAX_MS = 1000
        self.LONG_CLICK_MIN_MS = 1000

        self.resource_id = resource_id
        self.name = name

        self.multiCount = 0
        is_down_event = value
        now = datetime.now()
        if is_down_event:
            self.lastDownEvent = now
        else:
            self.lastUpEvent = now

    @staticmethod
    def time_delta(time_a, time_b):
        """
            Returns time from timeA to timeB in integer milliseconds.
        """
        return int(1000 * (time_b - time_a).total_seconds())

    def register_event(self, value):
        """
        Register button event. 
        :param Bool value: True, button was pressed. False, button was released.
        """
        is_down_event = value
        now = datetime.now()

        if is_down_event:
            print(f"{now} - Down event received for {self.resource_id}")
            # Reset multi count if down was pressed too long after last up
            delta_up = self.time_delta(self.lastUpEvent, now)
            if delta_up > self.MULTI_CLICK_MAX_MS:
                self.multiCount = 0
        else:  # Key up
            print(f"{now} - Up event received for {self.resource_id}")
            delta_down = self.time_delta(self.lastDownEvent, now)

            if delta_down >= self.LONG_CLICK_MIN_MS:  # Long press if long time since last down
                print(f"{now} - Long press event received for {self.name} [{delta_down} ms]")
                self.multiCount = 0
            else:
                if self.multiCount == 0:
                    print(f"{now} - Key press event received for {self.name} [{delta_down} ms]")
                    self.multiCount = 1
                else:
                    delta_up = self.time_delta(self.lastUpEvent, now)

                    if delta_up <= self.MULTI_CLICK_MAX_MS:  # Multi press if short time since last up
                        self.multiCount += 1
                        print(
                            f"{now} - Multi event received for {self.name} with count {self.multiCount} [{delta_up} ms]")
                    else:
                        self.multiCount = 0

        if is_down_event:
            self.lastDownEvent = now
        else:
            self.lastUpEvent = now
