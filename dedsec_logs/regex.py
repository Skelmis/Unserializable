import re

patterns = ['https://discord.gg', 'discord.gg']
text = 'https://discord.gg/XmT7aE'
for pattern in patterns:
    print('Looking for "%s" in "%s" ->' % (pattern, text), end=' ')
    if re.search(pattern, text):
        print('found a match!')
else:
    print('no match')
