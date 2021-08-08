import os


class Config(object):
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "{JCsu0@oCQl_ԛCX}o,I-WF>~i?ߤW]?6Fߍ^im`#yʽMF"
    )
