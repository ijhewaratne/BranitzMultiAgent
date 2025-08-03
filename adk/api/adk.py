# adk/api/adk.py
class ADK:
    """
    A minimal stub of your Agent Development Kit.
    Flesh this out with the real methods and attributes you need.
    """
    def __init__(self, **kwargs):
        # e.g. store configuration, set up clients, etc.
        self.config = kwargs

   
    
    def run(self, agent_instance, user_input):
        # agent_instance is already an Agent instance, not a class
        result = agent_instance.act(user_input)
        return result
    

