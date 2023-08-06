from getpass import getuser


class Property():
    def __init__(self, home, post, activity, name):
        self.home = home
        self.post = post
        self.activity = activity
        self.name = name

        self.value = ''
        self.y = ''

        if self.name == 'Title':
            self.value = ''

        if self.name == 'Location':
            self.units = {}

            for number in range(0, len(post.elements)):
                term = post.elements[number][0]
                if number <= 7:
                    self.units[term] = (
                        self.activity.content.locate(
                            term, tag=True
                        )
                    )
                else:
                    self.units[term] = (
                        self.activity.content.locate(term)
                    )
                    self.value = self.units[term]

            if self.post.province:
                self.units['province'] = self.post.province
                self.y += 'Province determined by post. '

            if self.units['province'].lower() == 'damascus':
                self.units['province'] = 'Dimashq'

            if not self.units['city']:
                if self.units['province'] in ['Aleppo', 'Hama', 'Homs']:
                    self.units['city'] = self.post.province
                    self.y += 'City determined by province. '
                if self.units['city'] == 'Raqqah':
                    self.units['city'] = 'al-Raqqah'
                    self.y += 'City determined by province. '
                if self.units['province'] == 'Dimashq':
                    self.units['city'] = 'Damascus'
                    self.y += 'City determined by province. '

            self.units['province'] = 'Rif ' + self.units['province']

            for element in post.elements:
                term = element[0]
                if self.units[term].lower() == 'the':
                    if self.home.activities:
                        self.units[term] = (
                            self.post.activities[self.activity.number - 1]
                            .properties[1].units[term]
                        )
                    else:
                        self.units[term] = ''

                if self.units[term]:
                    self.value += self.units[term] + ', '

            if self.value:
                if self.value[-2:] == ', ':
                    self.value = self.value[:-2]

            self.value = self.check(self.value)
            self.activity.location = self.value

        if self.name == 'Lat-Long':
            self.value = ''
            my_location = self.activity.properties['Location'].value

            for location in self.home.locations:
                if my_location in location['names']:
                    self.value = location['Lat-Long']

        if self.name == 'Grid Prec':
            self.value = ''
            my_location = self.activity.properties['Location'].value

            for location in self.home.locations:
                if my_location in location['names']:
                    self.value = location['Grid Prec']

        if self.name == 'Description':
            self.value = self.activity.content.text
            self.value = self.check(self.value)

        if self.name == 'Orientation':
            self.value = 'Anti-regime'

            if self.activity.content.contains('regime forces'):
                self.value = 'Pro-regime'
                self.y = 'Contains "regime force." '
            else:
                self.y = 'Does not contain "regime forces." '

            if(
                self.activity.content.contains('air') or
                self.activity.content.contains('helicopter')
            ):
                self.value = 'Pro-regime'

            self.value = self.check(self.value)

        if self.name == 'Ground':
            if self.activity.content.contains('clashes'):
                self.value = 'Complex'
                self.y = 'Contains "clashes." '

                if self.activity.content.contains('died', 'killed', 'dead'):
                    self.value = 'DF'
                    self.y += 'Contains "died," "killed," or "dead." '

            self.value = self.check(self.value)

        if self.name == 'Air':
            if self.activity.content.contains('air'):
                self.value = 'UNK Strike'
            if self.activity.content.contains('helicopter'):
                self.value = 'Rotary Wing Strike'
            if self.activity.content.contains('targeted a fighter-jet'):
                self.value = 'Ground-to-Air'

            self.value = self.check(self.value)

            if self.value:
                self.activity.properties['Orientation'].value = 'Pro-Regime'
            if self.value == 'Ground-to-Air':
                self.activity.properties['Orientation'].value = 'Anti-Regime'

        if self.name == 'Blast':
            if self.activity.content.contains('bomb ', 'IED', 'bomber'):
                self.value = 'IED'
            if self.activity.content.contains(
                'car bomb ', 'VBIED', 'car-bomb'
            ):
                self.value = 'VBIED'
            if self.activity.content.contains('suicide'):
                self.value = 'SVEST'

            self.value = self.check(self.value)

            if self.value:
                self.activity.properties['Orientation'] = 'Anti-Regime'

        if self.name == 'Targeted':
            if self.activity.content.contains('execut'):
                self.value = 'Execution'

            self.value = self.check(self.value)

        if self.name == 'Tactical':
            if self.activity.content.contains('ambush'):
                self.value = 'Ambush'
            if self.activity.content.contains('seize', 'taken'):
                self.value = 'Seize'
            if self.activity.content.contains('raid'):
                if not self.activity.content.contains('air raid'):
                    self.value = 'Raid'

            self.value = self.check(self.value)

        if self.name == 'Pro-regime KIA':
            self.value = self.number_check(self.value)

        if self.name == 'Pro-regime WIA':
            self.value = self.number_check(self.value)

        if self.name == 'Anti-regime KIA':
            self.value = self.number_check(self.value)

        if self.name == 'Anti-regime WIA':
            self.value = self.number_check(self.value)

        if self.name == 'Total KIA':
            self.value = self.total(
                self.activity.properties['Pro-regime KIA'].value,
                self.activity.properties['Anti-regime KIA'].value
            )

            self.value = self.number_check(self.value)

        if self.name == 'Total WIA':
            self.value = self.total(
                self.activity.properties['Pro-regime WIA'].value,
                self.activity.properties['Anti-regime WIA'].value
            )

            self.value = self.number_check(self.value)

        if self.name == 'Outcome':
            if self.activity.properties['Blast'].value:
                self.value = 'Effective'
            else:
                self.value = ''

            self.value = self.check(self.value)

        if self.name == 'Full Text':
            self.value = self.post.content.text

        if self.name == 'URL':
            self.value = self.post.link

        if self.name == 'Source Text':
            self.value = (
                'Syrian Observatory for Human Rights Facebook Page ' +
                self.post.date.strftime('%B %d %Y')
            )

        if self.name == 'Country Team':
            self.value = 'MESP-Syria'

        if self.name == 'Date Begin':
            self.value = self.post.short_date

        if self.name == 'Date End':
            self.value = self.post.short_date

        if self.name == 'Posted Date':
            self.value = self.post.time

        if self.name == 'Author':
            self.value = (
                getuser() + ' via SIGACTor ' + self.home.version + ' at ' +
                self.post.now.strftime('%Y-%m-%d-%H%M')
            )

    def check(self, value):
        while True:
            answer = input(
                '\nContent:\n' + self.activity.content.text + '\n' +
                '\nIs "' + self.value + '" the correct ' + self.name +
                ' ? (If correct, press enter. ' +
                'Otherwise, enter the correct value or "n" for none. '
                'To see why this value was determined, enter "y." '
                'To restart processing this activity, enter "r") '
            )
            if answer == '':
                return value
            elif answer == 'n':
                return ''
            elif answer == 'y':
                print('\n' + self.y)
            elif answer == 'r':
                self.activity.restart = True
                return ''
            else:
                return answer

    def number_check(self, value):
        while True:
            answer = self.check(value)
            if answer:
                try:
                    self.value_number = int(answer)
                    return answer
                except ValueError:
                    print('\nInvalid answer. Please enter a number. ')
                    continue
            else:
                return answer

    def total(self, pro, anti):
        number = 0

        for value in [pro, anti]:
            if value:
                number += int(value)
        return str(number)
