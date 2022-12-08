from datetime import datetime

class ButtonEventTracker:
    """
    Class for tracking button up/down events as multi or long presses.
    """

    def __init__(self, resource_id, name, value):
        
        self.multiClickMaxMs = 1000
        self.longClickMinMs = 1000
    
        self.resource_id = resource_id
        self.name = name

        self.multiCount = 0
        isDownEvent = value
        now = datetime.now()
        if isDownEvent:
            self.lastDownEvent = now
        else:
            self.lastUpEvent = now

    def DeltaMs(self, timeA, timeB):
        """
            Returns time from timeA to timeB in integer milliseconds.
        """
        return (int)(1000 * (timeB - timeA).total_seconds())

    def RegisterEvent(self, value):
        """
        Register button event. 
        :param Bool value: True, button was pressed. False, button was released.
        """
        isDownEvent = value
        now = datetime.now()

        if isDownEvent:
                print(f"{now} - Down event received for {self.resource_id}")
                # Reset multi count if down was pressed too long after last up
                deltaUp = self.DeltaMs(self.lastUpEvent, now)                
                if deltaUp > self.multiClickMaxMs:
                    self.multiCount = 0
        else: # Key up
            print(f"{now} - Up event received for {self.resource_id}")
            deltaDown = self.DeltaMs(self.lastDownEvent, now)

            if  deltaDown >= self.longClickMinMs: # Long press if long time since last down
                    print(f"{now} - Long press event received for {self.name} [{deltaDown} ms]")
                    self.multiCount = 0
            else:               
                if self.multiCount == 0:
                    print(f"{now} - Key press event received for {self.name} [{deltaDown} ms]")
                    self.multiCount = 1
                else:
                    deltaUp = self.DeltaMs(self.lastUpEvent, now)

                    if deltaUp <= self.multiClickMaxMs: # Multi press if short time since last up
                        self.multiCount += 1
                        print(f"{now} - Multi event received for {self.name} with count {self.multiCount} [{deltaUp} ms]")
                    else:
                        self.multiCount = 0

        if isDownEvent:
            self.lastDownEvent = now
        else:
            self.lastUpEvent = now
