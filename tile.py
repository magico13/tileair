class Tile(object):
    gas_constant = 8.206e-5 #m^3*atm/K*mol

    def __init__(self, tileid=0, temp=20, solid=False, nmol=0) -> None:
        super().__init__()
        self.tile_id = tileid
        self.temperature = temp
        self.num_moles = nmol
        self.solid = solid

    def temp_K(self) -> float:
        '''Returns the temperature in Kelvin'''
        return self.temperature + 273.15

    def get_pressure(self) -> float:
        '''Returns pressure in the tile in atmospheres'''
        #P=nRT/V
        #volume = 1 m^3
        if self.solid: return 0
        return self.num_moles * self.temp_K() * self.gas_constant
    
    def set_pressure(self, pressure) -> float:
        '''Sets the pressure by updating the number of moles'''
        #n=PV/RT
        if self.solid: return 0
        if pressure <= 0:
            self.num_moles = 0
        else:
            self.num_moles = pressure / (self.gas_constant * self.temp_K())
        return self.num_moles

