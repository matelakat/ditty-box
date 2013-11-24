import unittest

from dittybox import vm_param_generator


class TestNameGenerator(unittest.TestCase):
    def test_accepting_hypervisor(self):
        name_generator = vm_param_generator.NameGenerator(
            'prefix', 0, 1)
        self.assertEquals('prefix', name_generator.prefix)

    def test_generate_new(self):
        name_generator = vm_param_generator.NameGenerator('vm-', 0, 1)

        self.assertEquals('vm-0', name_generator.new_name([]))

    def test_generate_name_first_exists(self):
        name_generator = vm_param_generator.NameGenerator('vm-', 0, 1)

        self.assertEquals('vm-1', name_generator.new_name(['vm-0']))

    def test_generate_name_no_name_available(self):
        name_generator = vm_param_generator.NameGenerator('vm-', 0, 1)

        with self.assertRaises(vm_param_generator.NoMoreResources) as ctx:
            name_generator.new_name(['vm-0', 'vm-1'])

        self.assertEquals(
            'No more names are available for new VM',
            ctx.exception.message)
