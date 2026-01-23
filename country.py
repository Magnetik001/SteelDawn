class Country:
    def __init__(self, name, color, resources, wheat, metal, wood, coal, oil):
        self.country = name
        self.color = color
        self.resources = resources
        self.provinces = []
        self.wheat = wheat
        self.metal = metal
        self.wood = wood
        self.coal = coal
        self.oil = oil