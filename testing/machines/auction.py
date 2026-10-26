import re

CORE = re.compile(r'\bCore i[3579]-(\d{2})\d{3}([A-Z]*)\b', re.IGNORECASE)
ULTRA = re.compile(r'\bCore Ultra [3579] \d{3}([A-Z]*)\b', re.IGNORECASE)


def xe_igpu(cpu):
    if 'intel' not in cpu.lower():
        return False
    ultra = ULTRA.search(cpu)
    if ultra:
        return 'F' not in ultra.group(1).upper()
    core = CORE.search(cpu)
    return bool(core) and int(core.group(1)) >= 12 and 'F' not in core.group(2).upper()


def choose(listings):
    xe = [p for p in listings if xe_igpu(p.get('cpu') or '')]
    fee = [p for p in xe if float(p.get('price_setup') or 0) > 0]
    no_hourly = [p for p in xe if p.get('price_hourly') is None]
    fit = [p for p in xe if p not in fee and p not in no_hourly]
    if fit:
        return min(fit, key=lambda p: (float(p['price_hourly']), p['id'])), ''
    return None, ('of %d auction listings, %d have an Intel Core 12th gen or later with graphics: '
                  '%d with a setup fee, %d with no hourly price' % (len(listings), len(xe), len(fee), len(no_hourly)))
