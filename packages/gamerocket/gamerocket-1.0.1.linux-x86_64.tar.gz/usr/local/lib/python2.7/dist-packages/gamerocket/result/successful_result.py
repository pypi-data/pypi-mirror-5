from gamerocket.attribute_getter import AttributeGetter

class SuccessfulResult(AttributeGetter):
    
    @property
    def is_success(self):
        
        return True