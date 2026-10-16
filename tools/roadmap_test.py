import unittest

import roadmap


def item(number, status, *body, name='A title'):
    text = '\n'.join(['# %d. %s' % (number, name), '', '**%s**' % status, ''] + list(body)) + '\n'
    return roadmap.Item('roadmap/%03d-a-title.md' % number, text)


VISION_STUB = item(
    85, 'Open. Filed 2026-10-16 (r412), a vision item: its details are private. Nobody\'s call.',
    'Depends on: 82 (slice 1)', '',
    'Details: `vision/items/085-city-look-part-1.md`, in the private vision repository.',
    name='City look, part 1')

TABLE = '\n'.join([
    '| item | what it wants | depends on | whose call |',
    '| --- | --- | --- | --- |',
    '| [69](roadmap/069-x.md) | a bar | — | Aria |',
    '| [83](roadmap/083-x.md) | a pane | 82 (slice 1) | nobody, after item 82\'s first slice |',
    '| [phase 20 item 3](roadmap/phase-20-explain-itself.md) | the reading | — | Aria, from a frame |',
])


class WhenParsingDependsOn(unittest.TestCase):
    def test_and_it_is_well_formed_it_should_name_each_item_and_slice(self):
        for raw, want in [
            (None, []),
            ('nothing', []),
            ('82', [(82, None)]),
            ('82 (slice 1)', [(82, 1)]),
            ('82 (slice 1), 85', [(82, 1), (85, None)]),
        ]:
            with self.subTest(raw=raw):
                self.assertEqual(roadmap.parse_depends(raw), want)

    def test_and_it_is_malformed_it_should_refuse_it(self):
        for raw in ['', 'item 82', '82,85', '82 (slices 1 and 2)', '82 (slice one)', 'none']:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    roadmap.parse_depends(raw)


class WhenReadingAnItem(unittest.TestCase):
    def test_and_its_status_is_open_it_should_be_open(self):
        self.assertTrue(item(70, 'Open. Filed 2026-10-01 (r380).').is_open)

    def test_and_its_status_is_done_it_should_not_be_open(self):
        self.assertFalse(item(70, 'Done 2026-10-02 (`abc1234`, r381). Filed 2026-10-01 (r380).').is_open)

    def test_and_it_is_claimed_it_should_name_the_date_and_session(self):
        claimed = item(70, 'Open, in progress since 2026-10-16 in the session "item 70". Filed 2026-10-01 (r380).')
        self.assertEqual(claimed.claim, ('2026-10-16', 'item 70'))

    def test_and_it_is_not_claimed_it_should_have_no_claim(self):
        self.assertIsNone(item(70, 'Open. Filed 2026-10-01 (r380).').claim)

    def test_and_it_records_landed_slices_it_should_know_which(self):
        landed = item(82, 'Open. Filed.', 'Landed: slice 1 (`abc1234`, r413).', 'Landed: slice 3 (`def5678`, r420).')
        self.assertEqual(landed.landed, {1, 3})

    def test_and_it_has_a_details_line_it_should_be_a_vision_item(self):
        self.assertTrue(VISION_STUB.vision)

    def test_and_it_has_a_details_line_it_should_know_the_details_path(self):
        self.assertEqual(VISION_STUB.details, 'vision/items/085-city-look-part-1.md')

    def test_and_it_has_a_title_it_should_know_its_public_name(self):
        self.assertEqual(VISION_STUB.name, 'City look, part 1')

    def test_and_it_says_what_it_depends_on_it_should_keep_the_text(self):
        self.assertEqual(VISION_STUB.depends_raw, '82 (slice 1)')

    def test_and_it_has_no_details_line_it_should_be_a_normal_item(self):
        self.assertFalse(item(70, 'Open. Filed.').vision)


class WhenReadingTheOpenTable(unittest.TestCase):
    rows = roadmap.open_table(TABLE)

    def test_it_should_list_the_numbered_rows(self):
        self.assertEqual(sorted(self.rows), [69, 83])

    def test_it_should_keep_each_rows_depends_on_cell(self):
        self.assertEqual(self.rows[83].depends, '82 (slice 1)')

    def test_it_should_keep_each_rows_whose_call_cell(self):
        self.assertEqual(self.rows[69].whose, 'Aria')


class WhenJudgingWhereAnOpenItemStands(unittest.TestCase):
    def standing(self, subject, *others, whose='nobody, a defect'):
        items = {i.number: i for i in (subject,) + others}
        row = roadmap.Row('what', subject.depends_raw or '—', whose)
        return roadmap.standing(subject, items, row)

    def test_and_it_is_claimed_it_should_be_in_progress(self):
        claimed = item(70, 'Open, in progress since 2026-10-16 in the session "item 70". Filed.')
        self.assertEqual(self.standing(claimed, whose='Aria'), 'in progress')

    def test_and_it_is_aria_s_call_it_should_wait_on_aria(self):
        self.assertEqual(self.standing(item(69, 'Open. Filed.'), whose='Aria'), 'aria')

    def test_and_it_waits_until_something_costs_it_should_be_parked(self):
        self.assertEqual(self.standing(item(66, 'Open. Filed.'), whose='nobody, until it costs something'), 'parked')

    def test_and_a_slice_it_depends_on_has_not_landed_it_should_be_blocked(self):
        subject = item(83, 'Open. Filed.', 'Depends on: 82 (slice 1)')
        self.assertEqual(self.standing(subject, item(82, 'Open. Filed.')), 'blocked')

    def test_and_the_slice_it_depends_on_has_landed_it_should_be_ready(self):
        subject = item(83, 'Open. Filed.', 'Depends on: 82 (slice 1)')
        dep = item(82, 'Open. Filed.', 'Landed: slice 1 (`abc1234`, r413).')
        self.assertEqual(self.standing(subject, dep), 'ready')

    def test_and_a_whole_item_it_depends_on_is_still_open_it_should_be_blocked(self):
        subject = item(84, 'Open. Filed.', 'Depends on: 82')
        dep = item(82, 'Open. Filed.', 'Landed: slice 1 (`abc1234`, r413).')
        self.assertEqual(self.standing(subject, dep), 'blocked')

    def test_and_everything_it_depends_on_is_closed_it_should_be_ready(self):
        subject = item(84, 'Open. Filed.', 'Depends on: 82')
        self.assertEqual(self.standing(subject, item(82, 'Done 2026-10-20 (`abc1234`, r430). Filed.')), 'ready')


if __name__ == '__main__':
    unittest.main()
