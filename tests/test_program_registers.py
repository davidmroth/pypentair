from pypentair.pump import Program


class DummyPump:
    def __init__(self, values=None):
        self.values = dict(values or {})
        self.writes = []

    def get(self, address):
        key = tuple(address)
        if key not in self.values:
            raise KeyError(f"Missing register value for {key}")
        return self.values[key]

    def set(self, address, value):
        key = tuple(address)
        self.values[key] = value
        self.writes.append((key, value))
        return value


def test_program_rpm_prefers_alt_register_for_programs_1_to_4():
    pump = DummyPump({
        (0x03, 0x8D): 140,
        (0x03, 0xBB): 1093,
    })

    program = Program(pump, 1)

    assert program.rpm == 1093
    assert program.speed == 1093
    assert program.speed_type == "RPM"


def test_program_speed_write_mirrors_alt_register_for_programs_1_to_4():
    pump = DummyPump({
        (0x03, 0x8D): 140,
        (0x03, 0xBB): 1093,
    })

    program = Program(pump, 1)
    program.speed = 30

    assert pump.values[(0x03, 0x8D)] == 30
    assert pump.values[(0x03, 0xBB)] == 1093
    assert program.speed == 30
    assert program.speed_type == "GPM"


def test_program_rpm_write_mirrors_alt_register_for_programs_1_to_4():
    pump = DummyPump({
        (0x03, 0x8D): 30,
        (0x03, 0xBB): 30,
    })

    program = Program(pump, 1)
    program.rpm = 1093

    assert pump.values[(0x03, 0x8D)] == 1093
    assert pump.values[(0x03, 0xBB)] == 1093
    assert program.rpm == 1093
    assert program.speed_type == "RPM"


def test_program_5_to_8_do_not_use_alt_registers():
    pump = DummyPump({
        (0x03, 0x91): 1100,
    })

    program = Program(pump, 5)
    program.rpm = 1500

    assert pump.values[(0x03, 0x91)] == 1500
    assert ((0x03, 0xBF), 1500) not in pump.writes
    assert program.rpm == 1500
