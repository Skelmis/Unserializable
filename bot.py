from __future__ import print_function
import psutil
import discord
from discord.ext import commands
from aiohttp import ClientSession
import aiohttp
import asyncio
import async_timeout
import os
import json
import math
import datetime
import sys, traceback
import platform
import random, string
import pathlib
from pathlib import Path
from datetime import datetime

print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
cwd = Path(__file__).parents[0]
print(cwd)


OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            return
        except OSError:
            pass

        raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))

def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or("-")(bot, message)
    data = read_json('discordConfig')
    did = '{}'.format(message.guild.id)
    if did not in data:
        return commands.when_mentioned_or("-")(bot, message)
    prefix = data[did]['prefix']
    return commands.when_mentioned_or(prefix)(bot, message)

config_file = json.load(open(str(cwd)+'/bot_config/config.json'))
secret_file = json.load(open(str(cwd)+'/bot_config/secrets.json'))
bot = commands.Bot(command_prefix=get_prefix, owner_id=271612318947868673, case_insensitive=True)
#bot.remove_command('help')
bot.config_token = secret_file['token']
bot.config_stars = json.load(open(str(cwd)+'/bot_config/stars.json'))
bot.next_bug_report_id = None
extensions = []

botVersion = "0.7.3"

@bot.event
async def on_ready():
    """When the bot has connected to discord and is ready to go, is different to on connect"""
    print('------')
    global before_invites
    before_invites = []
    did = 599164187385659402
    guild = bot.get_guild(did)
    data = read_json('inviteLog')
    for invite in await guild.invites():
        if not invite.id in data:
            data[invite.id] = {}
        if not 'invitedUsers' in data[invite.id]:
            data[invite.id]['invitedUsers'] = {}
        data[invite.id]['invitedUsers'] = data[invite.id]['invitedUsers']
        data[invite.id]['creator'] = invite.inviter.id
        data[invite.id]['uses'] = invite.uses
        data[invite.id]['revoked'] = invite.revoked
        x = [invite.id, invite.code, invite.url, invite.uses, invite.inviter.id]
        before_invites.append(x)
    write_json(data, 'inviteLog')
    print(before_invites)
    print('------')
    print('Logged in as')
    print(bot.user.name)
    bot.embed_footer = f"Carpe Noctem | {bot.user.name} | "
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Game(name="Beware of keeping cash, but can you trust the banks?"))

@bot.event
async def on_message(message):
    """On discord message, this events called"""
    '''
    if bot.user.mentioned_in(message) and message.mention_everyone is False and:
        did = '{}'.format(message.guild.id)
        configData = read_json('config')
        prefix = configData[did]['prefix']
        prefixMsg = await message.channel.send(f"My prefix here is `{prefix}`")
        await prefixMsg.add_reaction('👀')
'''
    #commands = []
    #for command in bot.commands:
    #    commands.append(command)
    #    print(command)
    #await message.channel.send(commands)
    if message.author.id != 600246325900214295:
        if message.guild.id == 599164187385659402:
            data = read_json('whitelistedChannels')
            channel = '{0.id}'.format(message.channel)
            if channel in data:
                if data[channel]['state'] == "true":
                    await bot.process_commands(message)
                else:
                    print(f"{message.channel.name} is not a whitelisted channel")
            else:
                print(f"{message.channel.name} is not in the data")
        else:
            await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    """When the bot joins a new guild this runs"""
    guildId = '{}'.format(guild.id)
    guildName = '{}'.format(guild.name)
    failure = False
    modifier = 0.25
    whitelisted = False
    userCount = 0
    prefix = '-'
    randomOne = random.randint(1,25)
    randomTwo = random.randint(1,25)
    if randomOne == randomTwo:
        criminalDiscord = True
    else:
        criminalDiscord = False
    data = read_json('discordConfig')
    if guildId in data:
        failure = None
    else:
        data[guildId] = {}
        data[guildId]['guildName'] = guildName
        data[guildId]['modifier'] = modifier
        data[guildId]['whitelisted'] = whitelisted
        data[guildId]['criminalDiscord'] = criminalDiscord
        data[guildId]['prefix'] = prefix
        write_json(data, 'discordConfig')

    for member in guild.members:
        userCount += 1

    for channel in guild.channels:
        try:
            defaultChannel = bot.get_channel(channel.id)
            await defaultChannel.send("Thanks for adding me to your discord yall. @Me to get your prefix here and lets get grinding.\n*Please note you do need to run the income command atleast once to setup this discords eco*")
            break
        except:
            failure = True

    time = getTime()
    logChannel = bot.get_channel(600666300460695592)
    em = discord.Embed(title="Guild Joined", description=f"{guild.name}", colour=0x0000CC)
    em.add_field(name="Guild Info",value=f"Owner: <@{guild.owner_id}> `({guild.owner_id})`\nMembers: {userCount}\nModifier: {modifier}\nCriminal Discord: {criminalDiscord}", inline=False)
    em.set_footer(text=bot.embed_footer + time)
    await logChannel.send(embed=em)

@bot.event
async def on_message_delete(message):
    """When a message is deleted this is called"""
    author = message.author
    deleteChannel = message.channel
    content = message.content
    discord = message.guild.name
    channel = bot.get_channel(600265717400600586)
    await channel.send('#{} -> user {} deleted: `{}`'.format(deleteChannel, author, content))

@bot.event
async def on_command_completion(ctx):
    """Everytime a command is completed successfully this is called"""
    data = read_json('secrets')
    count = data['cc']
    count += 1
    data['cc'] = count
    write_json(data, 'secrets')

@bot.event
async def on_command_error(ctx, error):
    """Everytime a command errors this is called"""
    ignored = (commands.CommandNotFound)
    if isinstance(error, ignored):
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('This command is on a `%.2fs` cooldown' % error.retry_after)
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("This commands failed a check :/\n||*commands.CheckFailure tripped*||")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I am missing permissions to do this...\n||*commands.BotMissingPermissions tripped*||")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(f'{ctx.command} has been disabled.\n||*commands.DisabledCommand tripped*||')
    elif ctx.author.id == 271612318947868673:
        await ctx.send(f"Hey Skel, I encountered an error in command: `{ctx.command}`.\n`{error}`")
    raise error  # re-raise the error so all the errors will still show up in console
    print('------')

@bot.command()
@commands.is_owner()
async def prupdate(ctx, *, args):
    """Progress update logger"""
    data = read_json('config')
    number = data['progressReportCounter']
    number += 1
    data['progressReportCounter'] = number
    time = getTime()
    em = discord.Embed(title="Progress update", description=f"Progress report: {number}", colour=0x0000CC)
    em.add_field(name="Update Explanation",value=f"{args}", inline=False)
    em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
    em.set_footer(text=bot.embed_footer + time)
    channel = bot.get_channel(600686157604585492)
    await channel.send(embed=em)
    await ctx.message.delete()
    write_json(data, 'config')

@bot.command()
@commands.is_owner()
async def cwhitelist(ctx, channel=None):
    """Whitelist channels for the bot"""
    if not channel:
        channel = '{0.id}'.format(ctx.message.channel)
    data = read_json('whitelistedChannels')
    if channel in data:
        if data[channel]['state'] == "true":
            await ctx.send(f"Removing {channel} from the channel whitelist")
            data[channel]['state'] = "false"
        elif data[channel]['state'] == "false":
            await ctx.send(f"Adding {channel} to the channel whitelist")
            data[channel]['state'] = "true"
    else:
        await ctx.send(f"Adding {channel} to the channel whitelist")
        data[channel] = {}
        data[channel]['state'] = "true"
    write_json(data, 'whitelistedChannels')


@bot.command()
@commands.is_owner()
async def prefix(ctx, *, pre):
    '''Set a custom prefix for the guild.'''
    #try find prefix for this server in existing data using result = data[etc etc]
    uid = '{0.id}'.format(ctx.message.author)
    did = '{}'.format(ctx.message.guild.id)
    data = read_json('discordConfig')
    if not did in data:
        #create new area for that discord then store guild prefix
        data[did] = {}
        data[did]['prefix'] = str(pre)
        write_json(data, 'discordConfig')
        return await ctx.send(f'The guild prefix has been set to `{pre}` Use `{pre}prefix <prefix>` to change it again.')
    data[did]['prefix'] = str(pre)
    #update json file for that discord
    write_json(data, 'discordConfig')
    await ctx.send(f'The guild prefix has been set to `{pre}` Use `{pre}prefix <prefix>` to change it again.')

@bot.command(enabled=True)
@commands.guild_only()
async def verify(ctx):
    '''Used to verify your not a bot'''
    await ctx.message.delete()
    time = getTime()
    uid = '{0.id}'.format(ctx.message.author)
    did = '{}'.format(ctx.message.guild.id)
    check = read_json('discordConfig')
    if not did in check:
        check[did] = {}
    if 'verifyState' in check[did]:
        verifyState = check[did]['verifyState']
    else:
        check[did]['verifyState'] = "false"
        verifyState = "false"
    if 'verifySetup' in check[did]:
        verifySetup = check[did]['verifySetup']
    else:
        check[did]['verifySetup'] = "false"
        verifySetup = "false"
    write_json(check, 'discordConfig')
    guild = ctx.guild
    if verifySetup.lower() == "true":
        if verifyState.lower() == "true":
            data = read_json('userConfig')
            if not uid in data:
                data[uid] = {}
            if 'verify' in data[uid]:
                verified = data[uid]['verify']
            else:
                data[uid]['verify'] = False
                verified = False
            write_json(data, 'userConfig')
            user = ctx.author
            if verified == False:
                randNum = random.randint(000000, 999999)
                time = getTime()
                embed = discord.Embed(title=f"{ctx.message.author}", description="Please repeat the below code to be verified.", colour=0xffffff)
                embed.add_field(name="You have 15 seconds to verify with the below code.",value=f"{randNum}")
                embed.set_footer(text=bot.embed_footer + time)
                message = await user.send(embed=embed)
                try:
                    msg = await bot.wait_for('message', timeout=15, check=lambda message: message.author == ctx.author)
                    if msg:
                        if msg.content == str(randNum):
                            em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nPass", colour=0x228B22)
                            em.add_field(name="Thank you for completing verification.",value=f"Your input: *{msg.content}*")
                            roleGiven = await verifyFunction(ctx)
                            data = read_json('userConfig')
                            data[uid]['verify'] = True
                            write_json(data, 'userConfig')
                            userData = read_json('secrets')
                            endUsers = userData['commandUsers']
                            endUsers += 1
                            userData['commandUsers'] = endUsers
                            write_json(userData, 'secrets')
                        else:
                            em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nFail-Wrong Input", colour=0xff0000)
                            em.add_field(name="Im sorry but you failed verification.",value=f"Your input: *{msg.content}*")
                        time = getTime()
                        em.set_footer(text=bot.embed_footer + time)
                        messageTwo = await user.send(embed=em)
                #if msg is None:
                except asyncio.TimeoutError:
                    time = getTime()
                    em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nFail-No Input", colour=0x808080)
                    em.add_field(name="Im sorry but you failed verification.",value=f"Your input: *null*")
                    em.set_footer(text=bot.embed_footer + time)
                    messageTwo = await user.send(embed=em)
            else:
                await user.send(f"You are already verfied in this discord. (*{did}*)")
        else:
            await ctx.send("**This discord does not have verification enabled.\nPlease contact a staff member in your discord to enable this.**")
    else:
        await ctx.send("**This discord has not setup verification yet.\nPlease contact a staff member in your discord in order to do this.**")


@bot.command()
@commands.is_owner()
async def echo(ctx,*,msg='e'):
    """Echo input"""
    if msg == 'e':
        await ctx.send("Please enter text to echo after the command")
    else:
        await ctx.message.delete()
        await ctx.send(msg)

@bot.event
async def on_member_join(user):
    """When a member joins a guild the bot is in this is called"""
    if user.guild.id == 599164187385659402:
        uid = str(user.id)
        did = str(user.guild.id)
        data = read_json('userConfig')
        if uid in data:
            if data[uid]['verify'] == True:
                role = discord.utils.get(user.guild.roles, name="$Verified$")
                await user.add_roles(role)
        userData = read_json('userConfig')
        if not uid in userData:
            data[uid] = {}
        userData[uid]['inviteLogged'] = None
        write_json(userData, 'userConfig')

        did = 599164187385659402
        guild = bot.get_guild(did)
        inviteData = read_json('inviteLog')
        for invite in await guild.invites():
            if not invite.id in inviteData:
                inviteData[invite.id] = {}
            if not 'invitedUsers' in inviteData[invite.id]:
                inviteData[invite.id]['invitedUsers'] = {}
            inviteData[invite.id]['invitedUsers'] = inviteData[invite.id]['invitedUsers']
            inviteData[invite.id]['creator'] = invite.inviter.id
            inviteData[invite.id]['uses'] = invite.uses
            inviteData[invite.id]['revoked'] = invite.revoked

            if invite.uses != inviteData[invite.id]['uses']:
                print(invite.id, invite.uses)
                print(inviteData[invite.id], inviteData[invite.id]['uses'])


        """
        if userData[uid]['inviteLogged'] != True:
            inviteData = read_json('inviteLog')
            for i in range(inviteData[invite.id]['invitedUsers']):
                i += 1
            inviteData[invite.id]['invitedUsers'][i] = uid
            write_json(inviteData, 'inviteLog')

        """


@bot.command()
async def invites(ctx):
    """Show invites"""
    did = 599164187385659402
    if ctx.guild.id == did:
        data = read_json('inviteLog')
        did = 599164187385659402
        guild = bot.get_guild(did)
        invites = 0
        inviteCodes = []
        inviteIds = "None"
        for invite in await guild.invites():
            if invite.inviter.id == ctx.author.id:
                invites = invites + invite.uses
                inviteCodes.append(invite.id)
        dictLen = len(inviteCodes)
        for i in range(dictLen):
            if inviteIds == "None":
                inviteIds = inviteCodes[i]
            else:
                inviteIds = inviteIds + ', ' + inviteCodes[i]
        time = getTime()
        embed = discord.Embed(title="Invites", description="Come hither children.", colour=0xF1C40F)
        embed.add_field(name="Users invited (Joined)",value=f"{invites}",inline=False)
        embed.add_field(name="Invite codes",value=f"{inviteIds}",inline=False)
        embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
        embed.set_footer(text=bot.embed_footer + time)
        await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await ctx.message.delete()

spamcount = 0
@bot.command()
@commands.is_owner()
async def spam(ctx, *, message):
    """Spam input"""
    global spamcount
    while spamcount < 5:
        await ctx.send("{}".format(message))
        spamcount += 1
    else:
        await ctx.send("Reset")
        spamcount = 0

@bot.command()
@commands.has_role('Cool Kid')
async def purge(ctx, amount:int):
    """Purge some channels"""
    amount += 1
    await ctx.channel.purge(limit=amount)

@bot.command(name='perms', aliases=['perms_for', 'permissions', 'userperms'])
@commands.guild_only()
async def check_permissions(ctx, member: discord.Member=None):
    """A simple command which checks a members Guild Permissions.
    If member is not provided, the author will be checked."""
    if not member:
        member = ctx.author
    # Here we check if the value of each permission is True.
    perms = '\n'.join(perm for perm, value in member.guild_permissions if value)
    # And to make it look nice, we wrap it in an Embed.
    embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
    embed.set_author(icon_url=member.avatar_url, name=str(member))
    # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
    embed.add_field(name='\uFEFF', value=perms)
    await ctx.send(content=None, embed=embed)


@bot.command()
@commands.is_owner()
async def embed(ctx, *, content:str):
    """Embed a message"""
    # Usage: (prefix)embed <your message>

    embed = discord.Embed(
        description = content,
        color = discord.Color.orange()
    );

    embed.set_footer(text = 'ID: ' + str(ctx.author.id));
    embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url));

    await ctx.send(embed = embed);



@bot.command()
@commands.is_owner()
async def itest(ctx):
    """Income averages command"""
    for i in range(25):
        incomes = []
        for i in range(10):
            income = random.randint(25, 75)
            income = income * 1
            incomes.append(income)
        await ctx.send(incomes)
        total = 0
        for i in range(10):
            total = total + incomes[i]
        average = total / 10
        await ctx.send(average)
        await asyncio.sleep(2)

@bot.group()
async def bug(ctx):
    """Bug report section"""
    if ctx.invoked_subcommand is None:
        time = getTime()
        em = discord.Embed(title="Commands", description="Avaliable commands.", colour=0x0000CC)
        em.add_field(name="report",value="Report bot bugs", inline=False)
        em.add_field(name="status",value="Check the status of a bug report", inline=False)
        em.add_field(name="accept",value="Accept and close active bug reports - `Management Only`", inline=False)
        em.add_field(name="deny",value="Deny and close active bug reports - `Management Only`", inline=False)
        em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
        em.set_footer(text=bot.embed_footer + time)
        await ctx.send(embed=em)
        await ctx.message.delete()

@bug.command()
async def report(ctx, *, args):
    """Open a new bug report"""
    data = read_json('reports')
    time = getTime()
    uid = '{0.id}'.format(ctx.message.author)
    randomString = getRandomString()
    bugReportCheck()
    newRid = bot.next_bug_report_id
    channel = bot.get_channel(601420701580132352)
    if not newRid in data['bug']:
        data['bug'][newRid] = {}
        data['bug'][newRid]['content'] = args
        data['bug'][newRid]['status'] = "open"
        data['bug'][newRid]['authorId'] = uid
        em = discord.Embed(title="Bug report", description="Certified bug bounty hunter.", colour=0xFF00CC)
        em.add_field(name="Bug:",value=args, inline=False)
        em.add_field(name="Report id:",value=newRid, inline=False)
        em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
        em.set_footer(text=bot.embed_footer + time)
        try:
            user = bot.get_user(int(uid))
            await user.send("Thanks for reporting the bug to us. :smiley:")
            msg = await user.send(embed=em)
        except:
            await ctx.send(content=f"Open your dm's or you won't receive the response to your report <@{uid}>..")
            msg = await ctx.send(embed=em, delete_after=10)
        msgTwo = await channel.send(embed=em)
        data['bug'][newRid]['msgId'] = msgTwo.id
        write_json(data, 'reports')
        await asyncio.sleep(5)
        await ctx.message.delete()
    else:
        await channel.send(f"An error occured when ({uid}) tried making a bug report")

@bug.command()
async def status(ctx, rid):
    """Check the status of any bug report"""
    data = read_json('reports')
    time = getTime()
    validReport = False
    if rid in data['bug']:
        validReport = True
    if validReport == True:
        state = data['bug'][rid]['status']
        if state == "open":
            colour = 0xFFFFFF
        elif state == "Accepted":
            colour = 0x006400
        elif state == "Denied":
            colour = 0x8B0000
        em = discord.Embed(title="Bug report", description=f"Status: {state}", colour=colour)
        em.add_field(name="Report id:",value=rid, inline=False)
        em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
        em.set_footer(text=bot.embed_footer + time)
        await ctx.send(embed=em)
        await ctx.message.delete()
    else:
        await ctx.send(content="Invalid report id...", delete_after=5)
        await ctx.message.delete()

@bug.command()
@commands.has_role('Cool Kid')
async def accept(ctx, rid, *, reason=None):
    """Accept and close a bug report"""
    state = "Accepted"
    data = read_json('reports')
    time = getTime()
    validReport = False
    if rid in data['bug']:
        validReport = True
    if validReport == True:
        if not reason:
            reason = f"{state} by {ctx.author.name}."
        msgId = data['bug'][rid]['msgId']
        openReportChannel = bot.get_channel(601420701580132352)
        channel = bot.get_channel(601420726737829901)
        msg = await openReportChannel.fetch_message(int(msgId))
        reportContent = data['bug'][rid]['content']
        reporterId = data['bug'][rid]['authorId']
        reportUser = bot.get_user(int(reporterId))
        em = discord.Embed(title="Bug report", description=f"Status: {state}", colour=0x006400)
        em.add_field(name="Bug report content:",value=reportContent, inline=False)
        em.add_field(name="Report id:",value=rid, inline=False)
        em.add_field(name="Closing comment:",value=reason, inline=False)
        em.set_author(name = str(reportUser.name), icon_url = str(reportUser.avatar_url))
        em.set_footer(text=bot.embed_footer + time)
        data['bug'][rid]['status'] = f"{state}"
        write_json(data, 'reports')
        await channel.send(embed=em)
        try:
            user = bot.get_user(int(reporterId))
            em = discord.Embed(title="Bug report", description=f"Status: {state}", colour=0x006400)
            em.add_field(name="Bug report content:",value=reportContent, inline=False)
            em.add_field(name="Report id:",value=rid, inline=False)
            em.add_field(name="Closing comment:",value=reason, inline=False)
            em.set_author(name = str(reportUser.name), icon_url = str(reportUser.avatar_url))
            em.set_footer(text=bot.embed_footer + time)
            await user.send(embed=em)
        except:
            print(f"Unable to dm {reporterId} in response to report {rid}")
        await msg.delete()
        await ctx.message.delete()
    else:
        await ctx.send(content="Invalid report id...", delete_after=5)
        await ctx.message.delete()

@bug.command()
@commands.has_role('Cool Kid')
async def deny(ctx, rid, *, reason=None):
    """Deny and close a bug report"""
    state = "Denied"
    data = read_json('reports')
    time = getTime()
    validReport = False
    if rid in data['bug']:
        validReport = True
    if validReport == True:
        if not reason:
            reason = f"{state} by {ctx.author.name}."
        msgId = data['bug'][rid]['msgId']
        openReportChannel = bot.get_channel(601420701580132352)
        channel = bot.get_channel(601420726737829901)
        msg = await openReportChannel.fetch_message(int(msgId))
        reportContent = data['bug'][rid]['content']
        reporterId = data['bug'][rid]['authorId']
        reportUser = bot.get_user(int(reporterId))
        em = discord.Embed(title="Bug report", description=f"Status: {state}", colour=0x8B0000)
        em.add_field(name="Bug report content:",value=reportContent, inline=False)
        em.add_field(name="Report id:",value=rid, inline=False)
        em.add_field(name="Closing comment:",value=reason, inline=False)
        em.set_author(name = str(reportUser.name), icon_url = str(reportUser.avatar_url))
        em.set_footer(text=bot.embed_footer + time)
        data['bug'][rid]['status'] = f"{state}"
        write_json(data, 'reports')
        await channel.send(embed=em)
        try:
            user = bot.get_user(int(reporterId))
            em = discord.Embed(title="Bug report", description=f"Status: {state}", colour=0x8B0000)
            em.add_field(name="Bug report content:",value=reportContent, inline=False)
            em.add_field(name="Report id:",value=rid, inline=False)
            em.add_field(name="Closing comment:",value=reason, inline=False)
            em.set_author(name = str(reportUser.name), icon_url = str(reportUser.avatar_url))
            em.set_footer(text=bot.embed_footer + time)
            await user.send(embed=em)
        except:
            print(f"Unable to dm {reporterId} in response to report {rid}")
        await msg.delete()
        await ctx.message.delete()
    else:
        await ctx.send(content="Invalid report id...", delete_after=5)
        await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def logout(ctx):
    """Log the bot out of discord"""
    await ctx.send("Logging out...")
    await bot.logout()

"""
#music stuffs
@bot.command()
@commands.is_owner()
async def play(ctx, song, channel=None):
    if not channel:
        channel = ctx.author.voice.channel.id
    channel = bot.get_channel(int(channel))
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio(str(cwd) + f'/{song}.mp3'), after=lambda e: print('done', e))
    vc.source = discord.PCMVolumeTransformer(vc.source)
    vc.source.volume = 0.5
    vc.is_playing()
    print('Bot should joined the Channel')

@bot.command()
@commands.is_owner()
async def stop(ctx):
    guild = ctx.guild
    vc: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=guild)
    await vc.disconnet()
"""


#starting eco stuff
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def income(ctx):
    """A command to generate income"""
    randomOne = random.randint(1,6)
    randomTwo = random.randint(1,6)
    #await ctx.send(f"{randomOne} + {randomTwo}")
    uid = '{0.id}'.format(ctx.message.author)
    did = '{0.id}'.format(ctx.message.guild)
    if randomOne == randomTwo:
        await botCheck(ctx)
    checkData = read_json('userConfig')
    if not 'botCheck' in checkData[uid]:
        checkData[uid]['botCheck'] = "pass"
    write_json(checkData, 'userConfig')

    if checkData[uid]['botCheck'] == "pass":
        verified = await checkVerified(ctx)
        if verified == True:
            userModData = read_json('userConfig')
            if not uid in userModData:
                userModData[uid] = {}
            if not 'modifier' in userModData[uid]:
                userModData[uid]['modifier'] = 1
            write_json(userModData, 'userConfig')
            discordModData = read_json('discordConfig')
            if not did in discordModData:
                discordModData[did] = {}
            if not 'modifier' in discordModData[did]:
                discordModData[did]['modifier'] = 1
            write_json(discordModData, 'discordConfig')
            discordMod = discordModData[did]['modifier']
            userMod = userModData[uid]['modifier']
            totalMod = (discordMod + userMod) / 2
            await ctx.trigger_typing()
            responseData = read_json('responses')
            responseNumber = random.randint(1,6)
            time = getTime()
            income = random.randint(25, 75)
            income = income * totalMod
            name = '{}'.format(ctx.message.author)
            moneyData = read_json('money')
            if uid in moneyData:
                currentMoney = moneyData[uid]['money']
                money = currentMoney + income
                moneyData[uid]['money'] = money
                moneyData[uid]['name'] = name
                try:
                    bankedMoney = moneyData[uid]['bankedMoney']
                except:
                    bankedMoney = 0
                moneyData[uid]['bankedMoney'] = bankedMoney
            else:
                moneyData[uid] = {}
                moneyData[uid]['money'] = income
                moneyData[uid]['name'] = name
                try:
                    bankedMoney = moneyData[uid]['bankedMoney']
                except:
                    bankedMoney = 0
                moneyData[uid]['bankedMoney'] = bankedMoney
            write_json(moneyData, 'money')
            msgResponse = responseData[f'{responseNumber}']
            em = discord.Embed(title="Income", description="Make that cash money.", colour=0x0000CC)
            em.add_field(name=f"{msgResponse}",value=f"You made: ${income}", inline=False)
            em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
            em.set_footer(text=bot.embed_footer + time)
            await ctx.send(embed=em)
            await ctx.message.delete()
    else:
        time = getTime()
        em = discord.Embed(title="Income", description="Botting money.", colour=0x0000CC)
        em.add_field(name="You have a failed status in an anti bot check. ",value="Please run the command `antibot` to resolve this issue.\nIf you need assistance contact <@271612318947868673> to resolve this issues.", inline=False)
        em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
        em.set_footer(text=bot.embed_footer + time)
        await ctx.send(embed=em)
        await ctx.send(f"<@{uid}>")
        await ctx.message.delete()


@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def bank(ctx, type='e', amount=0.0):
    """A command to move your money around"""
    verified = await checkVerified(ctx)
    if verified == True:
        await ctx.trigger_typing()
        amount = float(amount)
        uid = '{0.id}'.format(ctx.message.author)
        if amount == 0:
            await ctx.send("Please specify either `deposit (amount)` or `withdraw (amount)`")
        elif amount <= 0:
            await ctx.send("You need to specify a positive amount aswell...")
        else:
            time = getTime()
            if type.lower() == 'deposit':
                amount = round(amount)
                r = deposit(uid, amount)
                if "you" in r.lower():
                    em = discord.Embed(title="Bank", description="Its theft your honour.", colour=0x228B22)
                else:
                    em = discord.Embed(title="Bank", description="Into the safe it goes.", colour=0x228B22)
                em.add_field(name="Deposit:",value=f"{r}", inline=False)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                em.set_footer(text=bot.embed_footer + time)
                await ctx.send(embed=em)
                await ctx.message.delete()
            elif type.lower() == 'withdraw':
                amount = round(amount)
                t = withdraw(uid, amount)
                em = discord.Embed(title="Bank", description="Cash in hand makes a solid plan.", colour=0x990099)
                em.add_field(name="Withdrawl:",value=f"{t}", inline=False)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                em.set_footer(text=bot.embed_footer + time)
                await ctx.send(embed=em)
                await ctx.message.delete()
            else:
                await ctx.send("Oof, Please specify either `deposit (amount)` or `withdraw (amount)`")

@bot.command()
async def bal(ctx, user: discord.User=None):
    """A command to checkout yourself or others"""
    verified = await checkVerified(ctx)
    if verified == True:
        await ctx.trigger_typing()
        did = '{}'.format(ctx.message.guild.id)
        configData = read_json('discordConfig')
        prefix = configData[did]['prefix']
        if not user:
            user = ctx.author
        uid = '{0.id}'.format(user)
        moneyData = read_json('money')
        try:
            bankedMoney = moneyData[uid]['bankedMoney']
        except:
            bankedMoney = 0
        try:
            currentMoney = moneyData[uid]['money']
        except:
            currentMoney = 0
        totalMoney = currentMoney + bankedMoney
        if uid in moneyData:
            time = getTime()
            currentMoney = round(currentMoney)
            bankedMoney = round(bankedMoney)
            totalMoney = round(totalMoney)
            em = discord.Embed(title="Bank", description="Little nerdy boi.", colour=0xCCCC00)
            em.add_field(name="Balance for:",value=f"<@{uid}>", inline=False)
            em.add_field(name="Cash:",value=f"${currentMoney}", inline=False)
            em.add_field(name="Banked money:",value=f"${bankedMoney}", inline=False)
            em.add_field(name="Total money:",value=f"${totalMoney}", inline=False)
            em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
            em.set_footer(text=bot.embed_footer + time)
            await ctx.send(embed=em)
            await ctx.message.delete()
        else:
            await ctx.send("Um yea, so you don't exist in the db for this discord. E.g. You should use {}income".format(prefix))

@bot.command()
async def baltop(ctx, pagenum='1'):
    """Check out the money balances"""
    verified = await checkVerified(ctx)
    if verified == True:
        await ctx.trigger_typing()
        time = getTime()
        moneyData = read_json('money')
        for uid in moneyData:
            try:
                currentCash = moneyData[uid]['money']
            except:
                currentCash = 0
            try:
                bankedCash = moneyData[uid]['bankedMoney']
            except:
                bankedCash = 0
            totalMoney = currentCash + bankedCash
            moneyData[uid]['totalMoney'] = totalMoney
        write_json(moneyData, 'money')
        pagenum = int(pagenum)
        username = ''
        count = 0
        total = 0
        di = {}
        data = read_json('money')
        for i in data:
            di[data[i]['name']] = int(data[i]['totalMoney'])
            total += 1
        results = sorted(di.items(), key=lambda t : t[1], reverse=True)
        for k, v in results:
            v = str(v)
            count += 1
            if count > ((pagenum*10)-10) and count  <= (pagenum*10):
                if count in [1,2,3,4,5]:
                    medal = bot.config_stars['medals'][(count-1)]
                else:
                    medal =''
            username = username + '``#' + str(count) + addspace(3-len(str(count))) + '- ' + "$" + v + '' + addspace(5-len(v)) + '-' + addspace(5-len(v)) + k + ''+ addspace(18-len(k)) + '-``' + medal + '\n\n'
        em = discord.Embed(colour=12745742)
        try:
                em.add_field(name ='Top Bals | page ' + str(pagenum) + ' of ' + str(math.ceil(total/10)), value=username, inline=False)
                em.set_footer(text=bot.embed_footer + time)
        except:
            em.add_field(name =':x: ERROR :x:', value='Invalid page number! (' + str(pagenum) + ')\nPlease use ``'+bot.config_prefix+'help`` for more information.', inline=False)
        await asyncio.sleep(1)
        await ctx.send(embed=em)
        await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def emtest(ctx, *, em):
    """Set embed footers"""
    bot.embed_footer = em

@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def rob(ctx, user: discord.User):
    """Rob someone else"""
    verified = await checkVerified(ctx)
    if verified == True:
        randomOne = random.randint(1,6)
        randomTwo = random.randint(1,6)
        uid = '{0.id}'.format(ctx.message.author)
        name = '{}'.format(ctx.message.author)
        userId = '{0.id}'.format(user)
        moneyData = read_json('money')
        if userId == uid:
            await ctx.send("Bruh you can't just rob yourself")
        else:
            if randomOne != randomTwo:
                if userId in moneyData:
                    randomThree = random.randint(1,50)
                    theftPercentage = randomThree / 100
                    userCash = moneyData[userId]['money']
                    stolenCash = userCash * theftPercentage
                    moneyData[userId]['money'] = userCash - stolenCash
                    try:
                        currentCash = moneyData[uid]['money']
                        moneyData[uid]['money'] = currentCash + stolenCash
                    except:
                        currentCash = 0
                        moneyData[uid] = {}
                        moneyData[uid]['money'] = currentCash + stolenCash
                        moneyData[uid]['name'] = name
                        try:
                            bankedMoney = moneyData[uid]['bankedMoney']
                        except:
                            bankedMoney = 0
                        moneyData[uid]['bankedMoney'] = bankedMoney
                    time = getTime()
                    stolenCash = round(stolenCash)
                    em = discord.Embed(title="Robbery", description="Shank shank", colour=0xCC0000)
                    em.add_field(name="Victim:",value=f"{user}", inline=False)
                    em.add_field(name="Cash stolen:",value=f"${stolenCash}", inline=False)
                    em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                    em.set_footer(text=bot.embed_footer + time)
                    await ctx.send(embed=em)
                    await ctx.message.delete()
                else:
                    await ctx.send(f"Uh, yea {user} doesn't appear to exist so you can't rob them. Try someone else?")
            else:#get total money - get % for bank, cash - divide fine between
                randomFour = random.randint(1.000,10)
                lossPercentage =  randomFour / 100
                try:
                    currentCash = moneyData[uid]['money']
                except:
                    currentCash = 0
                try:
                    bankedCash = moneyData[uid]['bankedMoney']
                except:
                    bankedCash = 0
                totalMoney = currentCash + bankedCash
                if totalMoney != 0:
                    if currentCash != 0 and bankedCash != 0:
                        cashPercentage = (totalMoney - bankedCash) / 100
                        bankedPercentage = (totalMoney - currentCash) / 100
                        fine = totalMoney * lossPercentage
                        bankFine = (fine / randomFour) * bankedPercentage
                        cashFine = (fine / randomFour) * cashPercentage
                        moneyData[uid]['money'] = currentCash - cashFine
                        moneyData[uid]['bankedMoney'] = bankedCash - bankFine
                    elif currentCash == 0 and bankedCash != 0:
                        bankFine = totalMoney * lossPercentage
                        moneyData[uid]['bankedMoney'] = bankedCash - bankFine
                    elif currentCash != 0 and bankedCash == 0:
                        cashFine = totalMoney * lossPercentage
                        moneyData[uid]['money'] = currentCash - cashFine
                    if not cashFine:
                        cashFine = 0
                    if not bankFine:
                        bankFine = 0
                    bankFine = round(bankFine)
                    cashFine = round(cashFine)
                    time = getTime()
                    em = discord.Embed(title="Robbery", description="You played yourself fool.", colour=0xCC0000)
                    em.add_field(name="Victim:",value=f"You", inline=False)
                    em.add_field(name="Cash lost:",value=f"${cashFine}", inline=False)
                    em.add_field(name="Banked money lost:",value=f"${bankFine}", inline=False)
                    em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                    em.set_footer(text=bot.embed_footer + time)
                    await ctx.send(embed=em)
                    await ctx.message.delete()
                else:
                    await ctx.send("Lucky... Your too poor to tax as of right now...")
        write_json(moneyData, 'money')

@bot.group()
@commands.is_owner()
async def admin(ctx):
    """Add or remove bot admins"""
    verified = await checkVerified(ctx)
    if verified == True:
        if ctx.invoked_subcommand is None:
            await ctx.send("Either admin add or admin remove mate")

@admin.command()
@commands.is_owner()
async def add(ctx, user=None):
    """Add a user as bot admin - `Owner only`"""
    verified = await checkVerified(ctx)
    if verified == True:
        if not user:
            user = '{0.id}'.format(ctx.author)
        try:
            user = user.strip("<@>")
        except:
            user = user
        uid = user
        data = read_json('config')
        if not uid in data['admins']:
            data['admins'][uid] = {}
            data['admins'][uid]['admin'] = "true"
        else:
            data['admins'][uid]['admin'] = "true"
        write_json(data, 'config')
        msg = await ctx.send(f"Added <@{uid}> as bot admin")
        await asyncio.sleep(5)
        await msg.delete()
        await ctx.message.delete()

@admin.command()
async def remove(ctx, user=None):
    """Remove someone as bot admin - `Owner only`"""
    verified = await checkVerified(ctx)
    if verified == True:
        if not user:
            user = '{0.id}'.format(ctx.author)
        try:
            user = user.strip("<@>")
        except:
            user = user
        uid = user
        data = read_json('config')
        if not uid in data['admins']:
            data['admins'][uid] = {}
            data['admins'][uid]['admin'] = "false"
        else:
            data['admins'][uid]['admin'] = "false"
        write_json(data, 'config')
        msg = await ctx.send(f"Removing <@{uid}> as bot admin")
        await asyncio.sleep(5)
        await msg.delete()
        await ctx.message.delete()

@bot.command()
async def rtest(ctx, invite: discord.Invite):
        """Shows information about an invite."""
        guild = bot.get_guild(599164187385659402)
        invites = guild.invites
        for invite in invites:
            if invite.inviter == message.author:
                await ctx.send(invite.uses)

        invite = bot.fetch_invite(f"{invite}")
        print(invite)
        embed = discord.Embed(title=f'Invite for {invite.guild.name} (`{invite.guild.id}`)')
        embed.add_field(name='Channel', value=f'{invite.channel.name} (`{invite.channel.id}`)', inline=False)
        embed.add_field(name='Uses', value=invite.uses, inline=False)
        if invite.inviter:
            embed.add_field(name='Inviter', value=invite.inviter, inline=False)
        await ctx.send(embed=embed)
        await ctx.send(f"{invite.max_age} {invite.approximate_member_count} {invite.id} {invite.url}")


@bot.command()
async def antibot(ctx):
    """For when you fail an anti bot check, this can get you out of a sticky situation"""
    uid = '{0.id}'.format(ctx.author)
    data = read_json('userConfig')
    if uid in data:
        if data[uid]['botCheck'] == "fail":
            user = bot.get_user(int(uid))
            randNum = random.randint(000000, 999999)
            time = getTime()
            embed = discord.Embed(title=f"{ctx.message.author}", description="Please repeat the below code to avoid being known to me as a bot.", colour=0xffffff)
            embed.add_field(name="You have 60 seconds to verify with the below code.",value=f"{randNum}")
            embed.set_footer(text=bot.embed_footer + time)
            await ctx.send(content=f"Hey {user.mention}, please check your dms from me", delete_after=15)
            message = await user.send(embed=embed)
            try:
                msg = await bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
                if msg:
                    if msg.content == str(randNum):
                        em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nPass", colour=0x228B22)
                        em.add_field(name="Thank you for completing this bot check.",value=f"Your input: *{msg.content}*")
                        data = read_json('userConfig')
                        data[uid]['botCheck'] = "pass"
                        write_json(data, 'userConfig')
                    else:
                        data = read_json('userConfig')
                        data[uid]['botCheck'] = "fail"
                        write_json(data, 'userConfig')
                        em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nFail-Wrong Input", colour=0xff0000)
                        em.add_field(name="Im sorry but you failed this bot check.",value=f"Your input: *{msg.content}*")
                    time = getTime()
                    em.set_footer(text=bot.embed_footer + time)
                    messageTwo = await user.send(embed=em)
            #if msg is None:
            except asyncio.TimeoutError:
                data = read_json('userConfig')
                data[uid]['botCheck'] = "fail"
                write_json(data, 'userConfig')
                time = getTime()
                em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nFail-No Input", colour=0x808080)
                em.add_field(name="Im sorry but you failed to verify you aren't a bot.",value=f"Your input: *null*")
                em.set_footer(text=bot.embed_footer + time)
                messageTwo = await user.send(embed=em)

"""
global before_invites
    before_invites = []
    for guild in self.client.guilds:
        for invite in await guild.invites():
            x = [invite.url, invite.uses, invite.inviter.id]
            before_invites.append(x)
        print(before_invites)
        """


@bot.command()
async def serverinfo(ctx, guild: discord.Guild):
        """Command to show server info"""
        guild = bot
        embed = discord.Embed(
            color=discord.Color.from_rgb(241, 90, 36)
        )
        sender = ctx.author
        embed.set_author(name="• Server Info → " + str(guild.name))
        embed.set_thumbnail(url=guild.banner(size=4096, format="png"))
        embed.add_field(name="—", value="→ Shows all information about a guild. The information will be listed below!"
                                        "\n —")
        embed.add_field(name="• Guild name: ", value=str(guild.name))
        embed.add_field(name="• Discord ID: ", value=str(guild.id))
        embed.add_field(name="• Guild owner: ", value=guild.owner)
        embed.add_field(name="• Guild owner ID: ", value=guild.owner_id)

        await ctx.send(embed=embed)

#functions
async def botCheck(ctx):
    """A function that can be used to check if someone is scripting or not"""
    data = read_json('userConfig')
    uid = '{0.id}'.format(ctx.author)
    user = bot.get_user(int(uid))
    if not uid in data:
        data[uid] = {}
    randNum = random.randint(000000, 999999)
    time = getTime()
    embed = discord.Embed(title=f"{ctx.message.author}", description="Please repeat the below code to avoid being flagged as a bot.", colour=0xffffff)
    embed.add_field(name="You have 60 seconds to verify with the below code.",value=f"{randNum}")
    embed.set_footer(text=bot.embed_footer + time)
    await ctx.send(content=f"Hey {user.mention}, please check your dms from me", delete_after=15)
    message = await user.send(embed=embed)
    try:
        msg = await bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        if msg:
            if msg.content == str(randNum):
                em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nPass", colour=0x228B22)
                em.add_field(name="Thank you for completing this bot check.",value=f"Your input: *{msg.content}*")
                data = read_json('userConfig')
                data[uid]['botCheck'] = "pass"
                write_json(data, 'userConfig')
            else:
                data = read_json('userConfig')
                data[uid]['botCheck'] = "fail"
                write_json(data, 'userConfig')
                em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nFail-Wrong Input", colour=0xff0000)
                em.add_field(name="Im sorry but you failed this bot check.",value=f"Your input: *{msg.content}*")
            time = getTime()
            em.set_footer(text=bot.embed_footer + time)
            messageTwo = await user.send(embed=em)
    except asyncio.TimeoutError:
        data = read_json('userConfig')
        data[uid]['botCheck'] = "fail"
        write_json(data, 'userConfig')
        time = getTime()
        em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nFail-No Input", colour=0x808080)
        em.add_field(name="Im sorry but you failed to verify you aren't a bot.",value=f"Your input: *null*")
        em.set_footer(text=bot.embed_footer + time)
        messageTwo = await user.send(embed=em)


def bugReportCheck():
    """Used to generate new bug report id's will forever loop untill an unused id is found theoretically"""
    data = read_json('reports')
    if not 'bug' in data:
        data['bug'] = {}
        write_json(data, 'reports')
    reportId = getRandomString()
    for rid in data['bug']:
        if rid == reportId:
            bugReportCheck()
    bot.next_bug_report_id = reportId

def getRandomString():
    """Creates a random string of ascii letters and digits, used for report id generation"""
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return x

async def checkVerified(ctx):
    """Checks if someone is verified or not"""
    data = read_json('userConfig')
    uid = '{0.id}'.format(ctx.author)
    if uid in data:
        if data[uid]['verify'] == True:
            return True
        else:
            try:
                member = bot.get_user(int(uid))
                msg = await member.send("Hey bro. So you arent verified. Join this discord and do `-verify`\nhttps://discord.gg/RkfHxmv")
                msgTwo = await ctx.send(f"Hey <@{uid}>, check your dms from me")
                await asyncio.sleep(5)
                await msg.delete()
                await msgTwo.delete()
                await ctx.message.delete()
            except:
                msg = await ctx.send(f"Hey <@{uid}, so i can't dm you it seems... Join this discord and do `-verify`\nhttps://discord.gg/RkfHxmv")
                await asyncio.sleep(5)
                await msg.delete()
                await msgTwo.delete()
                await ctx.message.delete()
            return False
    else:
        try:
            member = bot.get_user(int(uid))
            msg = await member.send("Hey bro. So you arent verified. Join this discord and do `-verify`\nhttps://discord.gg/RkfHxmv")
            msgTwo = await ctx.send(f"Hey <@{uid}>, check your dms from me")
            await asyncio.sleep(5)
            await msg.delete()
            await msgTwo.delete()
            await ctx.message.delete()
        except:
            msg = await ctx.send(f"Hey <@{uid}, so i can't dm you it seems... Join this discord and do `-verify`\nhttps://discord.gg/RkfHxmv")
            await asyncio.sleep(5)
            await msg.delete()
            await msgTwo.delete()
            await ctx.message.delete()
        return False

async def checkWhitelist(ctx):
    """A function made for usage with bot restrictions in the back alley"""
    if ctx.guild.id == 599164187385659402:
        data = read_json('whitelistedChannels')
        channel = '{0.id}'.format(ctx.channel)
        if channel in data:
            if data[channel]['state'] == "true":
                return True
            else:
                msg = await ctx.send("This channel is not whitelisted therefore you cannont use bot commands here.")
                await asyncio.sleep(5)
                await msg.delete()
                await ctx.message.delete()
                return False
        else:
            msg = await ctx.send("This channel is not whitelisted therefore you cannont use bot commands here.")
            await asyncio.sleep(5)
            await msg.delete()
            await ctx.message.delete()
            return False

def getTime():
    """Gets current date"""
    time = datetime.now().strftime('%d/%m/%Y')
    return time

def round(amount):
    """Rounds a number to 2 decimal places"""
    easy = []
    newAmount = 0
    amountStr = str(amount)
    if "." in amountStr:
        for char in amountStr:
            easy.append(str(char.lower()))
        length = len(easy)
        for x in range(length):
            if str(easy[x]) == '.':
                split = x + 3
                newAmount = amountStr[:split]
                return newAmount
    else:
        return amount

def roundRam(amount):
    """Rounds ram usage to a bigger decimal place then the other round command"""
    easy = []
    newAmount = 0
    amountStr = str(amount)
    if "." in amountStr:
        for char in amountStr:
            easy.append(str(char.lower()))
        length = len(easy)
        for x in range(length):
            if str(easy[x]) == '.':
                split = x + 5
                newAmount = amountStr[:split]
                return newAmount
    else:
        return amount


def deposit(uid, amount):
    """Used with the bank commands to deposit money to people's bank accounts"""
    moneyData = read_json('money')
    w = " "
    amount = float(amount)
    if uid in moneyData:
        if amount > moneyData[uid]['money']:
            w = "You don't have enough money to do this... You only have ${}".format(moneyData[uid]['money'])
        else:
            currentMoney = moneyData[uid]['money']
            try:
                bankedMoney = moneyData[uid]['bankedMoney']
            except:
                bankedMoney = 0
            currentMoney = currentMoney - amount
            bankedMoney = bankedMoney + amount
            moneyData[uid]['bankedMoney'] = bankedMoney
            moneyData[uid]['money'] = currentMoney
            write_json(moneyData, 'money')
            w = "Deposited ${} into the bank".format(amount)
    else:
        w = "It appears you don't exist to me, im sorry. :cry:"
    return w

def withdraw(uid, amount):
    """Used with the bank commands to withdraw money from peoples bank accounts"""
    moneyData = read_json('money')
    w = " "
    amount = float(amount)
    if uid in moneyData:
        if amount > moneyData[uid]['bankedMoney']:
            w = "You don't have enough money to do this... You have ${} in your bank".format(moneyData[uid]['bankedMoney'])
        else:
            bankedMoney = moneyData[uid]['bankedMoney']
            try:
                currentMoney = moneyData[uid]['money']
            except:
                currentMoney = 0
            currentMoney = currentMoney + amount
            bankedMoney = bankedMoney - amount
            moneyData[uid]['bankedMoney'] = bankedMoney
            moneyData[uid]['money'] = currentMoney
            write_json(moneyData, 'money')
            w = "Withdrew ${} from your bank account".format(amount)
    else:
        w = "It appears you don't exist to me, im sorry. :cry:"
    return w

async def verifyFunction(ctx):
    """Used to check if someone has the role or not i dont actually know?"""
    guild = ctx.guild
    if "$Verified$" in [role.name for role in guild.roles]:
        role = discord.utils.get(ctx.guild.roles, name="$Verified$")
        if role in ctx.author.roles:
            msg = "Already verified."
            return msg
        else:
            await ctx.author.add_roles(role)
            msg = "verified"
            return msg
    else:
        perms = discord.Permissions(permissions=0)
        guild = ctx.guild
        await guild.create_role(name="$Verified$", permissions=perms)
        await asyncio.sleep(1)
        role = discord.utils.get(ctx.guild.roles, name="$Verified$")
        if role in ctx.author.roles:
            msg = "Already verified."
            return msg
        else:
            await ctx.author.add_roles(role)
            msg = "verified"
            return msg

def addspace(n):
    """Basically makes an empty string of x length for usage as a spacer"""
    w = ''
    for x in range(0, n):
        w = w + ' '
    return w

def read_json(filename):
    """Read a json file in /bot_config/"""
    jsonFile = open(str(cwd)+'/bot_config/'+filename+'.json', 'r')
    data = json.load(jsonFile)
    jsonFile.close()
    return data

def write_json(data, filename):
    """Write to a json file in the /bot_config/ directory"""
    jsonFile = open(str(cwd)+'/bot_config/'+filename+'.json', 'w+')
    jsonFile.write(json.dumps(data))
    jsonFile.close()

@bot.group()
async def stats(ctx):
    """Show some basic stats"""
    if ctx.invoked_subcommand is None:
        time = getTime()
        data = read_json('secrets')
        pythonVersion = platform.python_version()
        rewriteVersion = discord.__version__
        #loop for members
        botServers = bot.guilds
        serverCount = 0
        for guild in botServers:
            serverCount += 1
        userCount = 0
        for g in botServers:
            userCount += len(g.members)
        embed = discord.Embed(title='{} Stats'.format(bot.user.name), description='\uFEFF', colour=ctx.author.colour)
        embed.add_field(name='Bot Version:', value=botVersion)
        embed.add_field(name='Python Version:', value=pythonVersion)
        embed.add_field(name='Discord.Py Version', value=rewriteVersion)
        embed.add_field(name='Total Guilds:', value=serverCount)
        embed.add_field(name='Total Users:', value=userCount)
        embed.add_field(name='Total commands run:', value=data['cc'])
        embed.add_field(name='Bot Developer:', value="<@271612318947868673>")
        embed.set_footer(text=bot.embed_footer + time)
        embed.set_author(name = str(bot.user.name), icon_url = str(bot.user.avatar_url))
        await ctx.send(embed = embed)

@stats.command()
@commands.is_owner()
async def admin(ctx):
    """Some nice admin stats surrounding the bot"""
    time = getTime()
    data = read_json('secrets')
    totalCommandUsers = data['commandUsers']
    botServers = bot.guilds
    serverCount = 0
    for guild in botServers:
        serverCount += 1
    userCount = 0
    for g in botServers:
        userCount += len(g.members)
    cpuUsage = psutil.cpu_percent()
    pid = os.getpid()
    py = psutil.Process(pid)
    memoryUse = py.memory_info()[0]/2.**30
    memoryUse = roundRam(memoryUse)
    embed = discord.Embed(title='{} Admin Stats'.format(bot.user.name), description='Special Kids Only.', colour=ctx.author.colour)
    embed.add_field(name="Total Guilds:", value=serverCount)
    embed.add_field(name='Total Users:', value=userCount)
    embed.add_field(name='Total Bot Users:', value=totalCommandUsers)
    embed.add_field(name='Cpu Usage %:', value=cpuUsage)
    embed.add_field(name='Script memory usage:', value=memoryUse)
    embed.set_footer(text=bot.embed_footer + time)
    embed.set_author(name = str(bot.user.name), icon_url = str(bot.user.avatar_url))
    await ctx.send(embed = embed)

initial_extensions = ['cogs.music']

if __name__ == '__main__':
    """If this is the 'main' file, run this code and run the bot when the script is ran"""
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()
    bot.run(bot.config_token)
