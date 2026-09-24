# Validates the fixed inherited TLS aliases alongside the original static checks.
# Keeps confirmed firmware metadata separate from arbitrary TLS or runtime support.
# Tested by independent D147 synthetic artifacts; the D142 validator stays intact.
import hashlib


BASE_SHA256 = 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'
TLS_SHA256 = '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'
LOADER_SHA256 = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
TLS_VALUES = {'_TLS_MODULE_BASE_': 8, '_rand_next': 8, 'z_tls_current': 16,
              'errno': 20, '_strtok_last': 24, '_localtime_buf': 28}


def checked_source(source, limit, digest):
    if type(source) is not bytes or not 0 < len(source) <= limit:
        raise ValueError('Source byte type or size invalid')
    if hashlib.sha256(source).hexdigest() != digest:
        raise ValueError('Source hash mismatch')


def load_frozen(native_tls_source, frozen_validator_source):
    # Check both inputs before even the known validator is executed.
    checked_source(native_tls_source, 65536, TLS_SHA256)
    checked_source(frozen_validator_source, 32768, BASE_SHA256)
    namespace = {'__name__': '_sumox_frozen_static_artifacts'}
    exec(compile(frozen_validator_source, '<frozen-static-artifacts>', 'exec'), namespace)
    return namespace


def image_type(base):
    class NativeElf(base['Elf']):
        def check_symbol(self, symbol, index, split, name):
            if name in TLS_VALUES or symbol['type'] == 6:
                base['require'](name in TLS_VALUES, 'Unrecognized TLS symbol')
                expected = dict(value=TLS_VALUES[name], size=0, bind=1, type=6,
                                other=0, section=65521)
                base['require'](symbol == expected and index >= split,
                                'Inherited TLS tuple or local partition mismatch')
                return
            super().check_symbol(symbol, index, split, name)

        def check_symbols(self):
            bounds = super().check_symbols()
            self.native_tls = []
            for name in sorted(TLS_VALUES):
                entries = self.symbols.get(name, [])
                base['require'](len(entries) == 1, 'Inherited TLS name missing or duplicated')
                self.native_tls.append(dict(name=name, **entries[0]))
            return bounds

    return NativeElf


def validate_artifacts(artifacts, native_tls_source, frozen_validator_source):
    base = load_frozen(native_tls_source, frozen_validator_source)
    require = base['require']
    require(type(artifacts) is dict, 'artifacts must be a dict')
    require(all(type(name) is str for name in artifacts) and
            set(artifacts) == set(base['LIMITS']), 'fixed seven artifacts required')
    for name, data in artifacts.items():
        require(type(data) is bytes and 0 < len(data) <= base['LIMITS'][name],
                'artifact type/size invalid')
    image = image_type(base)
    images = [image(artifacts[name]) for name in base['ELF_NAMES']]
    final = images[0]
    for other in images[1:]:
        require(other.normalized() == final.normalized() and other.bounds == final.bounds and
                other.entry_identity == final.entry_identity and other.native_tls == final.native_tls,
                'allocated image, initialization or TLS tuples differ across ELF forms')
    base['validate_packages'](artifacts, final)
    result = base['report'](artifacts, images)
    result['status'] = 'STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS'
    result['native_tls'] = dict(source_sha256=TLS_SHA256, loader_sha256=LOADER_SHA256,
                                symbols=final.native_tls)
    return result
