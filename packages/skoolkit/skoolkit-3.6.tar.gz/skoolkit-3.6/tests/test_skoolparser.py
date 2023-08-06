# -*- coding: utf-8 -*-
import unittest

from skoolkittest import SkoolKitTestCase
from skoolkit import SkoolParsingError
from skoolkit.skoolparser import SkoolParser, set_bytes, BASE_10, BASE_16, CASE_LOWER

class SkoolParserTest(SkoolKitTestCase):
    def _get_parser(self, contents, *args, **kwargs):
        skoolfile = self.write_text_file(contents, suffix='.skool')
        return SkoolParser(skoolfile, *args, **kwargs)

    def assert_error(self, skool, error):
        with self.assertRaises(SkoolParsingError) as cm:
            self._get_parser('; @start\n' + skool, asm_mode=1)
        self.assertEqual(cm.exception.args[0], error)

    def test_html_escape(self):
        skool = 'c24576 NOP ; Return if X<=Y & Y>=Z'
        parser = self._get_parser(skool, html=True)
        inst = parser.instructions[24576][0]
        self.assertEqual(inst.comment.text, 'Return if X&lt;=Y &amp; Y&gt;=Z')

    def test_html_no_escape(self):
        skool = 'c49152 NOP ; Return if X<=Y & Y>=Z'
        parser = self._get_parser(skool, html=False)
        inst = parser.instructions[49152][0]
        self.assertEqual(inst.comment.text, 'Return if X<=Y & Y>=Z')

    def test_html_macro(self):
        skool = '\n'.join((
            'c24577 NOP ; #HTML(1. See <a href="url">this</a>)',
            '           ; #HTML[2. See <a href="url">this</a>]',
            '           ; #HTML{3. See <a href="url">this</a>}',
            '           ; #HTML@4. See <a href="url">this</a>@',
            '           ; #HTML!5. See <a href="url">this</a>!',
            '           ; #HTML%6. See <a href="url">this</a>%',
            '           ; #HTML*7. See <a href="url">this</a>*',
            '           ; #HTML_8. See <a href="url">this</a>_',
            '           ; #HTML-9. See <a href="url">this</a>-',
            '           ; #HTML+10. See <a href="url">this</a>+',
            '           ; #HTML??',
            '           ; #HTML|#CHR169|',
            '           ; #HTML:This macro is <em>unterminated</em>',
            '; Test the HTML macro with an empty parameter string',
            ' 24588 NOP ; #HTML'
        ))
        parser = self._get_parser(skool, html=True)

        delimiters = {
            '(': ')',
            '[': ']',
            '{': '}'
        }
        text = parser.instructions[24577][0].comment.text
        lines = []
        for i, delim1 in enumerate('([{@!%*_-+', 1):
            delim2 = delimiters.get(delim1, delim1)
            lines.append('#HTML{0}{1}. See <a href="url">this</a>{2}'.format(delim1, i, delim2))
        lines.append('#HTML??')
        lines.append('#HTML|#CHR169|')
        lines.append('#HTML:This macro is <em>unterminated</em>')
        self.assertEqual(text, ' '.join(lines))

        self.assertEqual(parser.instructions[24588][0].comment.text, '#HTML')

    def test_font_macro_text_parameter(self):
        macros = (
            '#FONT:(1. A < B)0',
            '#FONT:[2. A & B]8',
            '#FONT:{3. A > B}16',
            '#FONT:@4. A <> B@24',
            '#FONT:??',
            '#FONT:*This macro is <unterminated>'
        )
        skool = '\n'.join((
            ('; Test the FONT macro text parameter',
             'c24577 NOP ; {}') +
            ('           ; {}',) * (len(macros) - 1) +
            ('; Test the FONT macro with an empty parameter string',
             ' 24588 NOP ; #FONT:')
        )).format(*macros)
        parser = self._get_parser(skool, html=True)

        text = parser.instructions[24577][0].comment.text
        self.assertEqual(text, ' '.join(macros))

        self.assertEqual(parser.instructions[24588][0].comment.text, '#FONT:')

    def test_empty_description(self):
        skool = '\n'.join((
            '; Test an empty description',
            ';',
            '; .',
            ';',
            '; A 0',
            'c25600 RET'
        ))
        parser = self._get_parser(skool, html=False)
        entry = parser.entries[25600]
        self.assertEqual(entry.details, [])
        registers = entry.registers
        self.assertEqual(len(registers), 1)
        reg_a = registers[0]
        self.assertEqual(reg_a.name, 'A')

    def test_registers(self):
        skool = '\n'.join((
            '; Test register parsing (1)',
            ';',
            '; Traditional.',
            ';',
            '; A Some value',
            '; B Some other value',
            '; C',
            'c24589 RET',
            '',
            '; Test register parsing (2)',
            ';',
            '; With prefixes.',
            ';',
            '; Input:A Some value',
            ';       B Some other value',
            '; Output:HL The result',
            'c24590 RET'
        ))
        parser = self._get_parser(skool, html=False)

        # Traditional
        registers = parser.entries[24589].registers
        self.assertEqual(len(registers), 3)
        reg_a = registers[0]
        self.assertEqual(reg_a.prefix, '')
        self.assertEqual(reg_a.name, 'A')
        self.assertEqual(reg_a.contents, 'Some value')
        reg_b = registers[1]
        self.assertEqual(reg_b.prefix, '')
        self.assertEqual(reg_b.name, 'B')
        self.assertEqual(reg_b.contents, 'Some other value')
        reg_c = registers[2]
        self.assertEqual(reg_c.prefix, '')
        self.assertEqual(reg_c.name, 'C')
        self.assertEqual(reg_c.contents, '')

        # With prefixes
        registers = parser.entries[24590].registers
        self.assertEqual(len(registers), 3)
        reg_a = registers[0]
        self.assertEqual(reg_a.prefix, 'Input')
        self.assertEqual(reg_a.name, 'A')
        self.assertEqual(reg_a.contents, 'Some value')
        reg_b = registers[1]
        self.assertEqual(reg_b.prefix, '')
        self.assertEqual(reg_b.name, 'B')
        self.assertEqual(reg_b.contents, 'Some other value')
        reg_hl = registers[2]
        self.assertEqual(reg_hl.prefix, 'Output')
        self.assertEqual(reg_hl.name, 'HL')
        self.assertEqual(reg_hl.contents, 'The result')

    def test_snapshot(self):
        skool = '\n'.join((
            '; Test snapshot building',
            'b24591 DEFB 1',
            ' 24592 DEFW 300',
            ' 24594 DEFM "abc"',
            ' 24597 DEFS 3,7'
        ))
        parser = self._get_parser(skool)
        self.assertEqual(parser.snapshot[24591:24600], [1, 44, 1, 97, 98, 99, 7, 7, 7]) 

    def test_nested_braces(self):
        skool = '\n'.join((
            '; Test nested braces in a multi-line comment',
            'b32768 DEFB 0 ; {These bytes are {REALLY} {{IMPORTANT}}!',
            ' 32769 DEFB 0 ; }'
        ))
        parser = self._get_parser(skool)
        comment = parser.instructions[32768][0].comment.text
        self.assertEqual(comment, 'These bytes are {REALLY} {{IMPORTANT}}!')

    def test_braces_in_comments(self):
        skool = '\n'.join((
            '; Test comments that start or end with a brace',
            'b30000 DEFB 0 ; {{Unmatched closing',
            ' 30001 DEFB 0 ; brace} }',
            ' 30002 DEFB 0 ; { {Matched',
            ' 30003 DEFB 0 ; braces} }',
            ' 30004 DEFB 0 ; { {Unmatched opening',
            ' 30005 DEFB 0 ; brace }}',
            ' 30006 DEFB 0 ; {{{Unmatched closing braces}} }',
            ' 30007 DEFB 0 ; { {{Matched braces (2)}} }',
            ' 30008 DEFB 0 ; { {{Unmatched opening braces}}}'
        ))
        parser = self._get_parser(skool)
        exp_comments = (
            (30000, 'Unmatched closing brace}'),
            (30002, '{Matched braces}'),
            (30004, '{Unmatched opening brace'),
            (30006, 'Unmatched closing braces}}'),
            (30007, '{{Matched braces (2)}}'),
            (30008, '{{Unmatched opening braces')
        )
        for address, exp_text in exp_comments:
            text = parser.instructions[address][0].comment.text
            self.assertEqual(text, exp_text)

    def test_end_comments(self):
        skool = '\n'.join((
            '; First routine',
            'c45192 RET',
            '; The end of the first routine.',
            '; .',
            '; Really.',
            '',
            '; Second routine',
            'c45193 RET',
            '; The end of the second routine.'
        ))
        parser = self._get_parser(skool)
        memory_map = parser.memory_map
        self.assertEqual(len(memory_map), 2)
        self.assertEqual(memory_map[0].end_comment, ['The end of the first routine.', 'Really.'])
        self.assertEqual(memory_map[1].end_comment, ['The end of the second routine.'])

    def test_data_definition_entry(self):
        skool = '\n'.join((
            '; Data',
            'd30000 DEFB 1,2,3',
            ' 50000 DEFB 3,2,1'
        ))
        parser = self._get_parser(skool)
        self.assertEqual(len(parser.memory_map), 0)
        snapshot = parser.snapshot
        self.assertEqual(snapshot[30000:30003], [1, 2, 3])
        self.assertEqual(snapshot[50000:50003], [3, 2, 1])

    def test_remote_entry(self):
        skool = '\n'.join((
            'r16384 start',
            '',
            '; Routine',
            'c32768 JP $4000',
        ))
        parser = self._get_parser(skool)
        memory_map = parser.memory_map
        self.assertEqual(len(memory_map), 1)
        instructions = memory_map[0].instructions
        self.assertEqual(len(instructions), 1)
        reference = instructions[0].reference
        self.assertFalse(reference is None)
        self.assertEqual(reference.address, 16384)
        self.assertEqual(reference.addr_str, '$4000')
        entry = reference.entry
        self.assertTrue(entry.is_remote())
        self.assertEqual(entry.asm_id, 'start')
        self.assertEqual(entry.address, 16384)

    def test_set_directive(self):
        skool = '\n'.join((
            '; @start',
            '; @set-prop1=1',
            '; @set-prop2=abc',
            '; Routine',
            'c30000 RET'
        ))
        parser = self._get_parser(skool, asm_mode=1)
        for name, value in (('prop1', '1'), ('prop2', 'abc')):
            self.assertTrue(name in parser.properties)
            self.assertEqual(parser.properties[name], value)

    def test_set_bytes(self):
        # DEFB
        snapshot = [0] * 10
        set_bytes(snapshot, 0, 'DEFB 1,2,3')
        self.assertEqual(snapshot[:3], [1, 2, 3])
        set_bytes(snapshot, 2, 'DEFB 5, "AB"')
        self.assertEqual(snapshot[2:5], [5, 65, 66])

        # DEFM
        snapshot = [0] * 10
        set_bytes(snapshot, 7, 'DEFM "ABC"')
        self.assertEqual(snapshot[7:], [65, 66, 67])
        set_bytes(snapshot, 0, 'DEFM "\\"A\\""')
        self.assertEqual(snapshot[:3], [34, 65, 34])
        set_bytes(snapshot, 5, 'DEFM "C:\\\\",12')
        self.assertEqual(snapshot[5:9], [67, 58, 92, 12])

        # DEFW
        snapshot = [0] * 10
        set_bytes(snapshot, 3, 'DEFW 1,258')
        self.assertEqual(snapshot[3:7], [1, 0, 2, 1])

        # DEFS
        snapshot = [8] * 10
        set_bytes(snapshot, 0, 'DEFS 10')
        self.assertEqual(snapshot, [0] * 10)
        set_bytes(snapshot, 0, 'DEFS 10,3')
        self.assertEqual(snapshot, [3] * 10)

    def test_warn_ld_operand(self):
        skool = '\n'.join((
            '; @start',
            '; Routine',
            'c32768 LD HL,32771',
            '',
            '; Next routine',
            '; @label=DOSTUFF',
            'c32771 RET'
        ))
        self._get_parser(skool, asm_mode=1, warnings=True)
        warnings = self.err.getvalue().split('\n')[:-1]
        self.assertEqual(len(warnings), 2)
        self.assertEqual(warnings[0], 'WARNING: LD operand replaced with routine label in unsubbed operation:')
        self.assertEqual(warnings[1], '  32768 LD HL,32771 -> LD HL,DOSTUFF')

    def test_get_instruction_addr_str_no_base(self):
        skool = '\n'.join((
            'c24583 LD HL,$6003',
            '',
            'b$600A DEFB 123'
        ))
        parser = self._get_parser(skool)
        self.assertEqual(parser.get_instruction_addr_str(24583, ''), '24583')
        self.assertEqual(parser.get_instruction_addr_str(24586, ''), '600A')
        self.assertEqual(parser.get_instruction_addr_str(24586, 'start'), '24586')

    def test_get_instruction_addr_str_base_10(self):
        skool = '\n'.join((
            'c24583 LD HL,$6003',
            '',
            'b$600A DEFB 123'
        ))
        parser = self._get_parser(skool, base=BASE_10)
        self.assertEqual(parser.get_instruction_addr_str(24583, ''), '24583')
        self.assertEqual(parser.get_instruction_addr_str(24586, ''), '24586')
        self.assertEqual(parser.get_instruction_addr_str(24586, 'load'), '24586')

    def test_get_instruction_addr_str_base_16(self):
        skool = '\n'.join((
            'c24583 LD HL,$6003',
            '',
            'b$600A DEFB 123'
        ))
        parser = self._get_parser(skool, base=BASE_16)
        self.assertEqual(parser.get_instruction_addr_str(24583, ''), '6007')
        self.assertEqual(parser.get_instruction_addr_str(24586, ''), '600A')
        self.assertEqual(parser.get_instruction_addr_str(24586, 'save'), '600A')

    def test_get_instruction_addr_str_base_16_lower_case(self):
        skool = '\n'.join((
            'c24583 LD HL,$6003',
            '',
            'b$600A DEFB 123'
        ))
        parser = self._get_parser(skool, case=CASE_LOWER, base=BASE_16)
        self.assertEqual(parser.get_instruction_addr_str(24583, ''), '6007')
        self.assertEqual(parser.get_instruction_addr_str(24586, ''), '600a')
        self.assertEqual(parser.get_instruction_addr_str(24586, 'save'), '600a')

    def test_warn_unreplaced_operand(self):
        skool = '\n'.join((
            '; @start',
            '; Start',
            'c30000 JR 30002'
        ))
        self._get_parser(skool, asm_mode=2, warnings=True)
        warnings = self.err.getvalue().split('\n')[:-1]
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0], 'WARNING: Unreplaced operand: 30000 JR 30002')

    def test_error_duplicate_label(self):
        skool = '\n'.join(('; @start',
            '; Start',
            '; @label=START',
            'c40000 RET',
            '',
            '; False start',
            '; @label=START',
            'c40001 RET'
        ))
        with self.assertRaisesRegexp(SkoolParsingError, 'Duplicate label START at 40001'):
            self._get_parser(skool, asm_mode=1)

    def test_asm_mode(self):
        skool = '\n'.join((
            '; @start',
            '; Routine',
            '; @rsub-begin',
            '; @label=FOO',
            '; @rsub+else',
            '; @label=BAR',
            '; @rsub+end',
            'c32768 RET'
        ))
        for asm_mode, exp_label in ((0, 'FOO'), (1, 'FOO'), (2, 'FOO'), (3, 'BAR')):
            parser = self._get_parser(skool, asm_mode=asm_mode)
            self.assertEqual(parser.get_instruction(32768).asm_label, exp_label)

    def test_rsub_no_address(self):
        skool = '\n'.join((
            '; @start',
            '; Routine',
            'c30000 XOR A',
            '; @rsub-begin',
            ' 30001 LD L,0',
            '; @rsub+else',
            '       LD HL,16384',
            '; @rsub+end'
        ))
        parser = self._get_parser(skool, asm_mode=3)
        entry = parser.entries[30000]
        instruction = entry.instructions[1]
        self.assertEqual(instruction.operation, 'LD HL,16384')
        self.assertEqual(instruction.sub, instruction.operation)

    def test_start_and_end_directives(self):
        skool = '\n'.join((
            'c40000 LD A,B',
            '',
            '; @start',
            'c40001 LD A,C',
            '; @end',
            '',
            'c40002 LD A,D',
            '',
            '; @start',
            'c40003 LD A,E',
            '; @end',
            '',
            'c40004 LD A,H'
        ))
        entries = self._get_parser(skool, asm_mode=1).entries
        self.assertFalse(40000 in entries)
        self.assertTrue(40001 in entries)
        self.assertFalse(40002 in entries)
        self.assertTrue(40003 in entries)
        self.assertFalse(40004 in entries)

    def test_html_mode_label(self):
        label = 'START'
        skool = '\n'.join((
            '; Routine',
            '; @label={}'.format(label),
            'c49152 LD BC,0',
            ' 49155 RET'
        ))
        parser = self._get_parser(skool, html=True)
        entry = parser.get_entry(49152)
        self.assertEqual(entry.instructions[0].asm_label, label)
        self.assertIsNone(entry.instructions[1].asm_label)

    def test_html_mode_keep(self):
        skool = '\n'.join((
            '; Routine',
            'c40000 LD HL,40006',
            '; @keep',
            ' 40003 LD DE,40006',
            '',
            '; Another routine',
            'c40006 RET'
        ))
        parser = self._get_parser(skool, html=True)
        entry = parser.get_entry(40000)
        self.assertFalse(entry.instructions[0].keep)
        self.assertTrue(entry.instructions[1].keep)

    def test_html_mode_rem(self):
        skool = '\n'.join((
            '; Routine',
            ';',
            '; @rem=These comments',
            '; @rem=should be ignored.',
            '; Foo.',
            '; @rem=And these',
            '; @rem=ones too.',
            'c50000 RET'
        ))
        parser = self._get_parser(skool, html=True)
        entry = parser.get_entry(50000)
        self.assertEqual(entry.details, ['Foo.'])

    def test_asm_mode_rem(self):
        skool = '\n'.join((
            '; @start',
            '; Routine',
            ';',
            '; @rem=These comments',
            '; @rem=should be ignored.',
            '; Foo.',
            '; @rem=And these',
            '; @rem=ones too.',
            'c50000 RET'
        ))
        parser = self._get_parser(skool, asm_mode=1)
        entry = parser.get_entry(50000)
        self.assertEqual(entry.details, ['Foo.'])

    def test_rsub_minus_inside_rsub_minus(self):
        # @rsub-begin inside @rsub- block
        skool = '\n'.join((
            '; @rsub-begin',
            '; @rsub-begin',
            '; @rsub-end',
            '; @rsub-end',
        ))
        error = "rsub-begin inside rsub- block"
        self.assert_error(skool, error)

    def test_isub_plus_inside_bfix_plus(self):
        # @isub+else inside @bfix+ block
        skool = '\n'.join((
            '; @bfix+begin',
            '; @isub+else',
            '; @isub+end',
            '; @bfix+end',
        ))
        error = "isub+else inside bfix+ block"
        self.assert_error(skool, error)

    def test_dangling_ofix_else(self):
        # Dangling @ofix+else directive
        skool = '\n'.join((
            '; @ofix+else',
            '; @ofix+end',
        ))
        error = "ofix+else not inside block"
        self.assert_error(skool, error)

    def test_dangling_rfix_end(self):
        # Dangling @rfix+end directive
        skool = '; @rfix+end'
        error = "rfix+end has no matching start directive"
        self.assert_error(skool, error)

    def test_wrong_end_infix(self):
        # Mismatched begin/else/end (wrong infix)
        skool = '\n'.join((
            '; @rsub+begin',
            '; @rsub-else',
            '; @rsub+end',
        ))
        error = "rsub+end cannot end rsub- block"
        self.assert_error(skool, error)

    def test_mismatched_begin_end(self):
        # Mismatched begin/end (different directive)
        skool = '\n'.join((
            '; @ofix-begin',
            '; @bfix-end',
        ))
        error = "bfix-end cannot end ofix- block"
        self.assert_error(skool, error)

if __name__ == '__main__':
    unittest.main()
