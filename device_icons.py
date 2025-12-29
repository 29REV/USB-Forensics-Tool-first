"""Default device icons and images for USB Forensics Tool.

This module provides embedded base64 images for common USB device types
as fallback when online images are not available.
"""
import base64
from io import BytesIO
from typing import Dict, Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# Simple 64x64 USB storage icon (PNG, base64 encoded)
USB_STORAGE_ICON = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAE
m0lEQVR4nO2bS2wbVRSGv3HsOHbiOE7iV9I0TdO0pU1LaUuhQIGKR1ELUtkgIViwQKxYsEBIbBAS
C1asWLBBYoFYIAECCRBCQjwqHqUttKRtaNMmbZq0iePYjh/xY+bCjJPYsWc8r3Hs/NJoNJ6Ze/7/
nHPuPXNnBgYGBgb/Y+xAC9AKtAOtwEGgHqgDaoEqoBKoAMqBMiAX8AI+IAh4gRCQAKaBeWAOmAJm
gElgHJgAxoAx4KKWk9QDDwIPAvcDtwF7gCqtBkyDBPQDZ4CfgZ+Ac8BalHdZAW4GngWeB44Ae7Uc
nI64gF7gM+A74KIaEZMA9wAvAe8CRzUYUCZ4gXeBV4BbVYmwAQ8BnwAfow7dUskM8A7wFrBHaQlW
4CngQ+CBLQy+kJwFXgcOKynBCrwMfALUaD2gAjINfAi8pZSEcuBN4FmNB1NIxoD3gTdQEAtwCDgJ
3K7hQArJz8CbwG/pSqgAjgNfALs0GkQhmQD+AN5HOUrbUGbtN8BdWgyggPwNfA28gjKUthFgBzoI
tWk9+AIyA5wA3kdZSluBAO8BN2k9+AIyC3wFvEMmEixqprc6jQdfQFxoJKEceBa4X+uBFxAPGkoo
B+7SetAFxo8WEizkbpM/Kf6tsRVNJJRrPeAC40ITCQ1aDzbTMQH1WquYaY7WKmZa/J9iyLZyBegH
LqFMpT0og+4GZYA8gB+Io3yWiwFB1I/b80AEiAIxIAHMogRgU8AEMIyyw4wDo8AIMAz8i/IdMgrM
AAvAEhBCWTvMo2SZXFZlXE75hqgi82E72kr4nfRc+2ZpCZdQAq1NJGjBPMo+4lU7cKfWg9aYBeBP
rUeR7bihFELfTKUQWkshVKeViuUohY5CSnMpVKeVitUqhd5CKXQXUqG7u1AK1YVUqC6kQpdSqbCQ
CkWFlCgqpERRISWKCilRVEiJokJKFBVSoqiQEkWFlCgqpERRISU2UqI8R0oUFlKioJASBYWU2F1I
ic2FlNhYSIn1hZS4XkiJ1UJKrBRSYrmQEkuFlIgpKRFTUiKmpERMSYmYkhIxJSViSkrElJSIKSkR
U1IipqREVEmJqJISUSUlokpKRJSUiCgpEVFSIqykRFhJibCSEmElJYIKSwQVlggqLBFUWCKosERQ
YYmAwhIBhSUCCksEFJYIKCwRUFgioLBEo8ISjQpLNCos0aiwRKPCEg0KSzQoLNGgsESDwhINmZZo
yLREQ6YlGjIt0ZBpiYZ0SzSkW6Ih3RIN6ZZoSLdEQ7olGtIt0ZBuiYZ0SzSkW6Ih3RIN6ZZoSKdE
UzolmtIp0ZROiaZ0SjSlU6IpnRJN6ZRoSqdEUzolmtIp0ZROiaZUSzSnWqI51RLNqZZoTrVEc6ol
mlMt0ZxqieZUSzSnWqI51RLNqZZoTrVEcyolWlIp0ZJKiZZUSrSkUqIllRItqZRoSaVESyolWlIp
0ZJKiZZUSrSkUqIllRLbU7FbinZLEdstsVsKdkuxbinWLYW6pVC3FOqWQt1SqFsKdEuBbinQLQW6
JV+35OuWfN2Sr1vydEuebsnTLXm6ZYNu2aBbNugWl25x6RaXbnHpFqduce6gW3boFoducegWh+7Y
oTt26I7rNcf1muN6DeHSDg3h0g4N4dIOzeDUDk3h0g4vIjAwMDD4Hw52PvVQaGaBAAAAAElFTkSu
QmCC
"""

# Simple 64x64 HDD icon
HDD_ICON = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAE
HElEQVR4nO2aW2xURRjHfzuttNtttXIRkIsiKmKQGESDQRNj4gMPPmh8UAMGgxEf1BhN1AcMibwY
Y3zQB43RRA0QiQ8EiMFEoyIqoBIQxEsvFRHUS2upbWlpt+zOmG/LLu1uznbP2d1tO8k/2WTPzHzz
/3/nfPPNN7NADjnkkEMOOeSQQ16SA88Aa4FVwGJgPlAKFAHFQAFwDXAV4AV8QBDwA4eBI8Bh4DBw
ENhv2/2S2xC+0nYw9wIrgZuBCqAQqLTjHDsOpzbgF+BroA34FGgGvgZGbNsvjW0RfhLwJPAC0Apc
BxRbdXJFkDPlA5YBLUA70AJ8ADxm4xQ1twNPAa8B1wMzrdyv8RrgK+ARZJXSxgTgJuB54AXgDqtW
7ujNwJPAM8B0qzZpNQS8AzwPLEj2w7OAzcBXwE3OuJ1+vt3Ao8DSZACYBDwDfAIscrp1el0EXgbu
IQFzgDuBVuAWp1ujl5xzC1E1ImIcsBZ4C3gY0bo9up0HXkVXLCLmWmGbneZqRcq+F5gSq+NqYCdS
qJxuq2TeO5DCGZEQ3mCZ0+nUtevt+yQyxI3Wi3k6nRoR7gP0cxoOu4GVTqdDoVFgGyrHQ0NWf1r0
N0kSFl4AtkfqcBuwCThiNSKnw6HQBzpHw82AEvimUxwVKTMaZVHs5tBldAiwM7hPGVH4oaRQjOKI
CYDLke+K4G+uRZ4pEoWDkSr0qEUWV1dCkUneiH0lYU90G1E1OsCiCAo/kFSqUbxiWaZoxCqoGcUn
cZzCl1VRTStu8Uy0KqpRfBJXFdWoolrxyoRYVVSj+CSuKqoRVVHz9jqhKqqXWFVUIqqi5u11VFXV
/L2Oqqr6f04VtSCpiqrld1xVVfP6Oqqq6v95VVU1jw+rqpr/F1ZVVX/DVVXVe1xVVfO7rqqq+dtd
VVXztruqqvntV1VV73FVVfW2u6qq5m93VVX1tl9VVe/yqKpqRVJV1XK8qqoWhVdVtSirqloMXlXV
kqyqalFWVbUovKqqJVlVVYvCq6paklVVLQqvqmpRdlW1LLuqWhZcVS0Lr6qWhVdVy4Krqp4UV1XP
xFdVy4Krqp5UV1U94auqnoFX1TPgqnomuqrqaUBVPaOvqnoaXFXPaFfV0+qqejq6qp4GV9XT0VX1
tLqqqjf1qurN/ap6M75VVW/ur6p6c79VVe+lqqq35quq3qusqnqvsKrqvcyqqvdyq6re8lVVb3la
Vb3l6qp686NV1VseyareqpiqeitvVfVWuFTVW+5S1VvhUlXvH1bV+6dVVe+fV1X1/l2rqvcfV1W9
f7+q6r0iUFW9V/iq6r0qoqreq0JV9V7pq6r3qlBVvVd5quq9yldV71XeFFT1XhWoqveqQFW91w2p
qve6IVX1/oFVvf/Uqv/0Vv2nt/oftao/evX/FVj9f4Wx/A8BjEYfjf/WAQAAAABJRU5ErkJggg==
"""

# Simple 64x64 USB icon (generic)
USB_ICON = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAD
lklEQVR4nO2bW2gcVRjHf5vdJJtNm6RJ06RpbKJGq4iIWkVBEEEQH0R8EF9EfRAf9EXxQdQHRVAQ
xBcVwRcRfFHBC4qgIIIXFEWt1lqttTVNm2bT3WST3c3szMjMJpvdmZ2dM7szm/nDYWF3zvnO9//m
O+d8ZwYKFChQIEccAt4FTgJngQlgGpgFIsAKsAxEgSVgHpgBJoGzwHvAQ8AewM6XABuBt4GrWMcy
cAJ4HNiRawE2AO8DC1hPBDgO7MuFABXAcWAB6wkDR7D+8O4Cvk4hsBccB2rSFaAS+DQD4l0HrgNL
msc8UIe5bAJ+TkEAxWmgAW/sB77VLP66c/kA8/kKeESj7wBwJYXgSj8CG8mOKuCMhs9fAm/iT/YD
Z5IIrVQPHCY7Hkjid1wOZTsJWxL0Ow5Ukz2bk/j+dZ4E2A+MJug3BNSS3fs+mMD/KNadCx4Ahhz6
/QXszJH/exz8zwD35UqAu4BfHfr9DVTl0P8qh7FPAM/nWoAXHPqMAhU59l+p/DsQ4LlcC7AXmI7T
bxDYkie+tjr48GRu5gv3OvSZyCP/txr8VGXbWQO8H6ffPFCWR/6XaZ6FBuBNnX5BIJQnARQhzRog
CExl25kNPO3Q501tLSwzUI6/ijjYVbYCbAa+j9PnFM6WmMn8GafPC0AtBvIi8Eecfk8YzP+ROP2U
E3RQIC2+i9NnJ8aTP4/8o+AjDk/3VoxnHfCvg49ejOcBh/JX2fdeAqqxgK3xVWhM5+usgF2ABexM
0GcTFrAHuJagTy+WsB9jSdxthd6aHN+Az/sdxgxgCfd5mLCsxRJetgqHBxzGNGMJNT4SOzOwBC8b
3p+BF1d7nMF2k/9WnLx/NZbRh/e7P7Ul9mCQ/1acvFdhGaPAXZ76KhepzSuMZTTeqy1jvIywG+gF
TuFtFzmKxTyDt/LX6UXPA+twwB/Ak8BPHvq+i4FbjJexQsArgB+AF3F3y1OOhXyAt0vT74BHcckY
1x1ihY58PUm9a8Bx4BESU49FbAXexFtV6GfgY+AlXByoNlmEG37G/YXpEnABuIiz2lYtzjZhIU/h
vtS1jPZdoRuyrfa0gGd13gSPkN49YAZ4CovZg7vaX7q0Yz5HsZwdwG84X4E7cQXoICD04nybfBxT
q0UBYRP+q0NjwBMESABFL8GoBf4M+I+A0oBx9YGzwJMEmAM4qx29DxxKYF+ORdThcyv8fyQI3IF1
fIGPzdDVUIb/4ognxghID/g/Uwf8TjBPwmpUYF116AbwF/AV8AzBEqBAgQIFKFb+A0OlncZo/b3Y
AAAAAElFTkSuQmCC
"""

# Mouse icon
MOUSE_ICON = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAD
VElEQVR4nO2aS2gTURSGv6Zt0qRJm7RJY2NVxAeKCxVBcOFCd7oQF+JCFyK4cOFCEBcuXIiCGxcu
xIULQVy4EEFBRfCBC19YWxVFqbW1Vms1aZOm0Sa5MtNptJlkJjOTzMTOgcMsbmbO/d+555w7MwOW
ZVmWZVmWZVlbEQfwAHAHqAFWgQQQB1aAJJAB0kAKSAJxYBm4C5wHDgH1bnBfHrgBLAIpIAtks3+m
gUXgBnA2+8bfbKkAPgXmgCRQAPLAIvAcuAkcA3qAVqAOqM9+twJdwCHgOvAEuA+MAZNAK9AK9AKX
gKdZn6vAHDAD+N33s8A8AYwBr7M/sgBc07xHfzE/An6u0WcauJkN8r96bwafZV+gkD0OfFnn72Y4
AYQNBh8DIgZ99gCPDQQfBXYa9HkAeCsYfBVwNWiM7QXGVwuwX+P36ewRUKodKOOd7Qb6Nc5+W4FT
xcFXafyp/d4C3Ad6y/SdBX4Ak8ABjf9/CDhetfP/rgVc1vh9HGipwF4FfNT4/gLoKA7+JPua0vj+
woBvX/a0qkfS4jdhgb0K2Kfxm9AKfK0sADggdgV8az2mz6RPv8AvGHOgjnpd5Q4u2W6qnwu/Yuwt
cxCqkF9Vs8d+KwGtqnbPv4q1Ue3eqs3QRnVT1e6p+gxtVMOqdi/lALShvlPtnqr+0QbcU7V7qPpH
E/C9qt13NQDbUB+p2j1VA7ANNaxq91D1jybge1W7+2oAtqF+VLX7QQ3ANtQPqnbfqwHYhnqjaveN
GoBtqFeqdi/lAbSh3qjaOVQDsA31tardd2oAtqH+ULV7qgZgG+oHVbsfagC2oT5StXuqBmAb6jtV
u+9qALah/lC1+64GYBvqW1W7b9QAbEO9ULV7Lg+gDfVM1e6pGoBtqCeqdk/kAbShHqraOVQDsA31
SNXuuzwANtSwqt1DNQDbUPdV7e7LA2BDvVO1e6wGYBvqtqrdLTUA21BfqtrdkgfAhvpM1e6mPAA2
1CdVuxvyANhQH1Xt3ssDbPIdPqjaXZMHwIa6omr3XR4AG+q9qt17eQBsqMuqdhflAbChLqnaPZYH
wIa6oGp3Xh4AG+q8qt0ZeQBsqLOqdqflAbChzqjaHZcHwIY6qWp3XB4AG+qYqt2RUu1OGPBZUu3+
AuoqNOAI2FDH/wUfBzwG/Ra0fv8CFY7ssLuIBEwAAAAASUVORK5CYII=
"""

# Keyboard icon
KEYBOARD_ICON = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAC
wklEQVR4nO2bv2sUQRTHP5vbnTvvsvdDTSEWIv4FgkVsFAsLwcJCsLGwECwsLAQLC0GwsBAEC0Gw
EAQLQbAQBAtBsBAEC0GwEAQLwUKwEAwWgoVgIVgIFsK+YYOXy+7N7N7uztzNDXxhmb2d9773vZl5
b3YW/Hw8IAfMAY+AFWALqACOv3rA72ADWAHuAHNALu0g5YBzwCqwTeexDlwE8mkFYQxYBGQIrAHz
QCaNIEwD78i+N8C0b0GYBj5HDMAW8BhYBh4BS8BjYB1Y829MkrfAKV+CMAnsx3i3DSwAE8AoUPDX
KFDE/6L0A+ZvE3gBnABGkkQiBxSBK0BLw7YO5JMEYpx/PnSY2k0nXLdFYM2j/w5wpLcAGJxCqc3L
rUXgnXZPLfp12RDwUmP/IzCslwUcBb5o7D+DM65bwbDVLgu4rtG/Azzsr3/0qGn0zwGzGv1NQ3/7
WcC0Rv8NcKQf/tFzRqO/hWFhxLSACxr9l2BW29gqQLuYQmaBo+jXdX31j56SRn+xI2Beo38VfzpA
G13XBoBtgRw2DPRfAH7C0AB0BRAYMuz/kVr0bU+HG+i/wNAAdAUQLQBcByQInPJ0eAr+dIApg/43
QCaDnmbPAb+0Bb1P6EKXvwn6vgL3MRcV64YOfQE+A3PAcQz43ivAtKHvHrAIvAS+4UzSWzgV5Qbw
BDgYv6LsZdZQNKUBfPfpB3nz5FgyZH8B9hL4Pws4Z9D/OMJsUZb9I+Ci9v+bjpgZdM8Y9K9FmC2u
sn8UQd+0+28F/4+A+xo7d4O2dO48n2P/yIm+X8UWzqqj6C5p7CwadB61bIi6ABwM/p816L6nsXHJ
oHPWoKMc8f+QQe+Cxs4Ng87/FgAdMwa9SxobilE9xbhXzXs+FEDboHtVY+dyxP9DBr2PNHYqGARg
U/ggpBVxAfjLohFXdV/TGdS+m+xfTMnOMF2XYN7I/L+z9wdK94AJxYWr9QAAAABJRU5ErkJggg==
"""

# Bluetooth/Wireless icon
BLUETOOTH_ICON = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAD
WklEQVR4nO2aS2gTURSGv0maNE2aNGmTNtZWRREVF4ILFwqCILhw4U4XunDhQhAXLlyIggsXLsSF
CxcuBHHhQgQFFVFEBReuVMSH1Vpb26S1SZs0aZLcyLSNNpnMvTOTSXPnQCBkcu//n3PvOXPuTCCQ
Qw455OAOIuA0cBWoAMvAEhAHloAkkAYSQBJIAEvAMnANOA8cBurcqL4OuA4sAilAAvlsP0kgBlwH
ztnV5KYGuAwsAGkgC+Syfz4D48CNbPKvpqsBfgemgQyQB+aBp8At4DiwF2gCGrJ/7gWOATeB+8Az
4Akw5QXyLuAb8A1YANLA5+y9fHYe+AJ8BIaBBuAg8DvwDZhxY8D3wCdghuz3BrgGtFjc4y3wyk2C
Mvkxl5LfBrwHXri18CXfAvpdjH8/MGoh/kHgAe4mfxv4bDH+XcB4WZNvLHPyI8Aui+sccDP5EvnP
gF0O1t8FfHYh+RHgo8PkfwD3uZH8deBfC/FUZr+g0n/QhYJoI/A0+9+TZpMfAp5bTL4EPHFrL1AG
3gMd2QxdLUPA+2wGy+Yt8BS4APRjHe3AReAR8NZC8iXgkRfFj0p+Ajhq8nVwxIvkR4CvGvkJ4LjF
+Nvd6AJNGI9/RCO/AAx4EH8vcE8j/wU46kX8h0ySnwAOVSD+/RrZ60CPF/H3aqq+T8ABF+IvaoqP
UV6N8k2a+N8D+92IX02+D/hVIn5VvF/xq+L3lYlfFe9X/Ct7gVZN/E/98QMHNNX/Sw/8wAHgk0b+
sQd+4IDVpvBvvfCDf83+fq3OVlztuWi2vjaCBNsEVCXYhgq2CahKsA0VbBNQlWAbKtgmoCrBNlSw
TUBVgm2oYJuAqgTbUME2AVUJtqGCbQKqEmxDBdsEVCXYhgq2CahKsA0VbBNQlWAbKtgmoCrBNlSw
TUBVgm2oYJuAqgTbUME2AVUJtqGCbQKqEmxDBdsEVCXYhgq2CahKsA0VbBNQlWAbKtgmoCrBNlSw
TUBVgm2oYJuAqgTbUME2AVUJtqGCbQKqEmxDBdsEVCXYhgq2CahKsA0VbBNQlWAbKtgmoCrBNlSw
TUBVgm2oYJuAqgTbUME2AVUJtqGCbQKqEmxDBdsEVCXYhgq2CahKsA0VbBPQSL5V43/TAz9wwIhG
/o4HfuCAYY18yQM/cMCQRn7IAz9wwG2NfNEDP3DASvJfyR0BOeSQQ6Dq+Qs/VbBQn/vxugAAAABJ
RU5ErkJggg==
"""

# Network/Hub icon
NETWORK_ICON = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAD
LklEQVR4nO2aS2gTURSGv0mTNE2aNGnSpI1VRUXEhQsVQRBcuHCnC3EhLlwI4sKFC0FcuHAhCi5c
uBAXLly4EMSFCxEUVEQRFVy4UhEf1dbWNmmTNmmSpsmV20bbaJKZuZNk7swcCITM5N7//eece+69
EwiRQgoppFBBwgFaAC9wEggDcSAGJIAkkAFmgSSQAGLACHAK8AAtbhRfB5wFYkAayAK57J/LwAhw
Lpv8O2lqAC4C00AKyAP5bDsFJIEbwKVs8jVSVw18AqaBNJAHZoCnwG2gFWgEGrJ/NgJtwD3gBfAM
eALE3SBvA74D34AUkAa+AIPAHmAVsAyoyv65DNiY/XkQeAE8BqKljn8t8AmIAimyJwj0A+ssjvEe
iJZT8m3Ae2BchW+NdXj++Cce4wnwGpiy+Bzq8uRdjH8j8Bp45dTCl3wz0Otg/GuBd+WSvEp+wOH4
NwDvHEx+K/DE7eRvAP86GP/nwDO3k78F/Otg/J+BO24nfwf428H4PwV87iZ/G/jHwfg/Avbc6AGq
wPOq/19pJv43wFMLyX8Cnrq1Eigj74CObIauKvkh4G0R8ivGI7fWAsvIe2BlNkOnEu8Fhov4fwE8
dmvhY+R9wIoSxf8q2wVimqjOAA9c3AuY+R8BttsYf51bXWCV3/h/YxH/Vjfi3+MveQXY4WD824r0
/xovkm8D/hYR/1avkm8F/ioQfwqoKVH8NcAfReJPAFu8SH6HWfylir+myK6wCHxzO/kdReJ/41bs
hWTtArb/mCBRSwUpwsYEiVqsSBs2Jkh0ykWbNmxMkKjEirRhY4JEJVakDRsTJCqxIm3YmCBRiRVp
w8YEiUqsSBs2JkhUYkXasDFBohIr0oaNCRKVWJE2bEyQqMSKtGFjgkQlVqQNGxMkKrEibdiYIFGJ
FWnDxgSJSqxIGzYmSFRiRdqwMUGiEivSho0JEpVYkTZsTJCoxIq0YWOCRCVWpA0bEyQqsSJt2Jgg
UYkVacPGBIlKrEgbNiZIVGJF2rAxQaISK9KGjQkSlViRNmxMkKjEirRhY4JEJVakDRsTJCqxIm0U
iu0qEH+vC/GHAN2q/4sR+hTEjvC/iP8Cc3/gNPtVBs8AAAAASUVORK5CYII=
"""

# Default/Unknown device icon
UNKNOWN_DEVICE_ICON = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAD
uElEQVR4nO2aXUhTYRjHn3NObunmtpmVFhSVFyVdhBB2UVdBQXQRdFEXQRdBF0EXQRdBF0EXQRdB
F0GQRUEWYRdBF0EXQRdBF0EXQRdBF0EXQRdBUDBn58TzH/bO1uZ2zub2zDMP/GGc8z7v8/s/7/u+
7zkKBYfD4XA4HM5fTxrQCJQAdUANUA6UABuBjUA+kAvkADnZfwsABQgDU8AUMAm8A94AL4FRYATw
An3Z35s1agGfAU+AGBAnQRKBISAfJEk48A5ISUI/0I72hFsEBpIk/CnQwgbEDgzPEf5ncAC4DVQC
m5ZJLgXMAF+z//8YuAAUKS7hAtD8B/HngAPOBMDh3wdKlJRxEfghif8ZOO90AOT/bqtjfw/UOx0A
mfxGbPC/BfKcDoCM+c8siv8z0Oh0AOTrT1kU/wjQ5HQA5PI3bUH8I8Bhn87FNVvkBzoA6zb5gX3A
c4viX5Dxb1Jxu6TyHe7cPwDcskH8A0CT5YC8B+pb3PEZ2K+kmNOSOz7lkgOE2x5JfJOW+48BR5QU
s18S36TlfhKoVlJMlSS+ScttA+4qKeau5I6bsl++sNxpx3w/V0/W/W8dCkA3cNOB8W9SuA/4LI39
N4p9VmvjVJ9YfXz+WGEMD0hi/xjb/y97mObUAXRZaP9PsgdcjgfgqoX2X8p+0nM0ANXAp0WK/yPQ
oNgI+ewuTr5VE/5WxYaoA8YWIf6/QK1iQ9Sy8EwvaT2WZ39aXMBRzXNV28cJiy2vXrEpDkvu+LRN
nXBGsSnOSOKbtNwBxcY4IIlv0nI7FBujQxLfpOXucfAJ8D1JfJOW2+rYvbiD8lk/I5H/t8VOiFss
iv8VuOZkh3jdovjDwBUlhVyRxDdpuX0Wn3tXKPYB9z3SuJe06mf/Pk5CvSS8ScsdBE4pacA8UGgC
Hp6z/tDyQnEo5M6x2wQcmOfpb4OSJrRZfOV1XPG49L+dWgA8F8Vfg/u02g+ApxZu69FicCwpOOQg
QUIU2gkSIVCnzEMO5Pr/lEOEJxWPorDuv0oHCU8qBk8dJDytODxWOfivTY6ZQPaBeWAJeFZxuDg3
51KBXL7K+uVmBTipOMxT7YDiUC99A+ocCoBcntZJ7nskDziipJRGi/c81iop5ogkvin35HQH6LG4
40+VlNNtYfxfKCmnWxLfpOU+UFLOAzm3S1ruXSXl3JXcacpy7yop567cU0+We0dJOXfknl6S3A7F
5mgvMr7JSW5bAuTuL3L8+7S8FXRQbjflZHlMccHkKO/8/XQsB1hvg/CrjuUX8CkuK7VkXgN+Zkf2
MLBY/gPHOTiuDgMoRAAAAABJRU5ErkJggg==
"""


def get_icon_for_device_type(device_type: str) -> Optional[bytes]:
    """Get icon bytes for device type."""
    if not PIL_AVAILABLE:
        return None
    
    icon_map = {
        'storage': USB_STORAGE_ICON,
        'input': MOUSE_ICON,
        'mouse': MOUSE_ICON,
        'keyboard': KEYBOARD_ICON,
        'network': BLUETOOTH_ICON,
        'bluetooth': BLUETOOTH_ICON,
        'hub': NETWORK_ICON,
        'unknown': UNKNOWN_DEVICE_ICON,
    }
    
    icon_base64 = icon_map.get(device_type.lower(), USB_ICON)
    
    try:
        icon_data = base64.b64decode(icon_base64)
        return icon_data
    except Exception:
        return None


def get_pil_image_for_device_type(device_type: str) -> Optional['Image.Image']:
    """Get PIL Image for device type."""
    if not PIL_AVAILABLE:
        return None
    
    icon_data = get_icon_for_device_type(device_type)
    if not icon_data:
        return None
    
    try:
        image = Image.open(BytesIO(icon_data))
        return image
    except Exception:
        return None


def get_icon_names() -> Dict[str, str]:
    """Get mapping of device types to icon descriptions."""
    return {
        'storage': 'USB Storage Device',
        'input': 'Input Device (Mouse/Keyboard)',
        'mouse': 'Mouse',
        'keyboard': 'Keyboard',
        'network': 'Network/Bluetooth Device',
        'bluetooth': 'Bluetooth Device',
        'hub': 'USB Hub',
        'unknown': 'Unknown USB Device'
    }


if __name__ == '__main__':
    print("Available device icons:")
    for device_type, desc in get_icon_names().items():
        print(f"  {device_type}: {desc}")
    
    if PIL_AVAILABLE:
        print("\nGenerating test image...")
        img = get_pil_image_for_device_type('storage')
        if img:
            img.save('test_icon.png')
            print("Test icon saved to test_icon.png")
