"""RVS native blending parameters; independent of LAS2 depth estimation."""
from dataclasses import asdict,dataclass
import math,struct

@dataclass(frozen=True)
class BlendingOptions:
    method:str='Multispectral'
    low_factor:float=1.
    high_factor:float=4.
    simple_factor:float=5.

    def validate(self):
        if self.method not in ('Multispectral','Simple'):
            raise ValueError('Unbekannte Bildverschmelzung / Unknown blending method')
        values=(self.low_factor,self.high_factor) if self.method=='Multispectral' else (self.simple_factor,)
        for value in values:
            try:
                number=struct.unpack('f',struct.pack('f',value))[0]
                valid=math.isfinite(number) and number>0 and math.isfinite(1/number) and 1/number<=3.4028234663852886e38
            except (OverflowError,TypeError,ZeroDivisionError):valid=False
            if not valid:raise ValueError('Faktoren müssen positive, endliche Float32-Zahlen sein. / Factors must be positive, finite float32 numbers.')

    def to_settings(self):return asdict(self)

    @classmethod
    def from_settings(cls,data):
        if not isinstance(data,dict):return cls()
        defaults=cls();values={}
        for key in ('low_factor','high_factor','simple_factor'):
            try:
                value=float(data.get(key,getattr(defaults,key)))
                trial=cls(method='Simple',simple_factor=value);trial.validate();values[key]=value
            except (ValueError,TypeError,OverflowError):values[key]=getattr(defaults,key)
        return cls(method=data.get('method') if data.get('method') in ('Multispectral','Simple') else defaults.method,**values)

    def rvs_config(self):
        self.validate()
        if self.method=='Simple':return dict(BlendingMethod=self.method,BlendingFactor=self.simple_factor)
        return dict(BlendingMethod=self.method,BlendingLowFreqFactor=self.low_factor,BlendingHighFreqFactor=self.high_factor)

    @property
    def description(self):
        factors=f'{self.low_factor:g}/{self.high_factor:g}' if self.method=='Multispectral' else f'{self.simple_factor:g}'
        return f'RVS CPU Precision 1 {self.method} {factors}'
