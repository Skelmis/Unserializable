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
#import lavalink #music
import re # regex

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
bot.dedsec_enabled = False
bot.check_num = 1
bot.greek = ";"
bot.blacklisted_users = None
bot.ready = False
bot.invite = "https://discord.gg/xaprPYX"
bot.invite_id = "xaprPYX"
bot.admins = [271612318947868673, 294863378260688897]

botVersion = "0.9.1"

@bot.event
async def on_ready():
    """When the bot has connected to discord and is ready to go, is different to on connect"""
    await bot.change_presence(activity=discord.Game(name="Negotiating a connection to discord."))
    bot.config_token = bot.config_token.swapcase()
    bot.config_token = bot.config_token.encode("cp037", "replace")
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
    if not bot.invite_id in data:
        channel = bot.get_channel(599169305552224256)
        await channel.send(f"uh @everyone, the invite im using is invalid\nI am using `{bot.invite}` as my invite however it is invalid -_-")
    print(before_invites)
    print('------')
    print('Logged in as')
    print(bot.user.name)
    bot.embed_footer = f"Carpe Noctem | {bot.user.name} "
    print(bot.user.id)
    print('------')
    bot.blacklisted_users = read_json('userConfig')
    bot.ready = True
    await asyncio.sleep(2.5)
    await bot.change_presence(activity=discord.Game(name="Beware of keeping cash, but can you trust the banks?"))

@bot.event
async def on_message(message):
    """On discord message, this events called"""
    if message.content == "ALPHA AidaN FOXTROT CharliE. Bravo six going dark.":
        channel = bot.get_channel(608586455731929088)
        await channel.send("Logging out...\n**DO NOT LOGIN UNTILL A LOGOUT PHRASE HAS BEEN REGENERATED**\n\n||@everyone||")
        print(f"{message.author} has logged the bot out")
        print("DO NOT LOGIN UNTILL A LOGOUT PHRASE HAS BEEN REGENERATED")
        await bot.logout()
    if message.content == "ALPHA AidaN FOXTROT CharliE. Delta one coming online.":
        bot.ready = True
    if bot.ready == False:
        return
    if message.author.id == bot.user.id:
        return
    uid = '{0.id}'.format(message.author)
    if str(message.author.id) in bot.blacklisted_users:
        try:
            if bot.blacklisted_users[uid]['blacklisted'] == True:
                return
        except:
            pass
    '''
    if bot.user.mentioned_in(message) and message.mention_everyone is False and:
        did = '{}'.format(message.guild.id)
        configData = read_json('config')
        prefix = configData[did]['prefix']
        prefixMsg = await message.channel.send(f"My prefix here is `{prefix}`")
        await prefixMsg.add_reaction('👀')'''
    if message.channel.id == 600681150217846784:
        if not message.author.id in bot.admins:
            await message.delete()
    if bot.dedsec_enabled == True:
        try:
            file = open(str(cwd) + f"/dedsec_logs/{uid}.txt", 'a')
        except FileNotFoundError:
            file = open(str(cwd) + f"/dedsec_logs/{uid}.txt", 'w')
        time = getTime()
        file.write(f"{time}, {message.content} \n")
        file.close()
    if not message.guild is None:
        if message.guild.id == 599164187385659402: #Back alley discord
            if not message.author.id in bot.admins:
                match = False
                patterns = ['https://discord.gg', 'discord.gg']
                for pattern in patterns:
                    #print('Looking for "%s" in "%s" ->' % (pattern, message.content))
                    if re.search(pattern, message.content):
                        match = True
                        break
                else:
                    match = False
                if match == True:
                    await message.delete()
                    author = message.author
                    await author.send("Lowkey stop advertising, if u got a problem dm management.\n||Error code - 400 Bad message body||")
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    """When the bot joins a new guild this runs"""
    guildId = '{}'.format(guild.id)
    guildName = '{}'.format(guild.name)
    failure = False
    modifier = 0
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
            failure = False
            break
        except:
            failure = True

    time = getTime()
    logChannel = bot.get_channel(600666300460695592)
    em = discord.Embed(title="Guild Joined", description=f"{guild.name}", colour=0x0000CC)
    em.add_field(name="Guild Info",value=f"Owner: <@{guild.owner_id}> `({guild.owner_id})`\nMembers: {userCount}\nModifier: {modifier}\nCriminal Discord: {criminalDiscord}", inline=False)
    if failure == True:
        em.add_field(name="Failure occured in process",value="I could not send the default message to any channels.")
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
    ignored = (commands.CommandNotFound)#, commands.UserInputError)
    if isinstance(error, ignored):
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is on a `{round(error.retry_after)}s` cooldown, {ctx.author.mention}')
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
@commands.cooldown(1, 2, commands.BucketType.user)
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
    try:
        await ctx.message.delete()
    except:
        pass
    write_json(data, 'config')

@bot.command()
@commands.has_role("Discord Administrator")
@commands.cooldown(1, 2, commands.BucketType.user)
async def cw(ctx, channel=None):
    """Whitelist channels for the bot"""
    botAdmin = checkBotAdmin(ctx)
    if botAdmin == True and ctx.author.id in bot.admins:
        if not channel:
            channel = '{0.id}'.format(ctx.message.channel)
        data = read_json('whitelistedChannels')
        if channel in data:
            if data[channel]['state'] == "true":
                await ctx.send(f"Removing {channel} from the channel whitelist",delete_after=5)
                data[channel]['state'] = "false"
            elif data[channel]['state'] == "false":
                await ctx.send(f"Adding {channel} to the channel whitelist",delete_after=5)
                data[channel]['state'] = "true"
        else:
            await ctx.send(f"Adding {channel} to the channel whitelist",delete_after=5)
            data[channel] = {}
            data[channel]['state'] = "true"
        await ctx.message.delete()
        write_json(data, 'whitelistedChannels')


@bot.command()
@commands.is_owner()
@commands.cooldown(1, 2, commands.BucketType.user)
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
@commands.cooldown(1, 2, commands.BucketType.user)
async def verify(ctx):
    '''Used to verify your not a bot'''
    try:
        await ctx.message.delete()
    except:
        pass
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
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
                data[uid]['botCheck'] = "pass"
                data[uid]['modifier'] = 0
                data[uid]['criminalNum'] = 0
                data[uid]['blacklisted'] = False
                data[uid]['inviteLogged'] = None
                write_json(data, 'userConfig')
                user = ctx.author
                if verified == False:
                    randNum = random.randint(000000, 999999)
                    time = getTime()
                    embed = discord.Embed(title=f"{ctx.message.author}", description="Please repeat the below code to be verified.\nBy verifying you accept our terms of service.", colour=0xffffff)
                    embed.add_field(name="You have 60 seconds to verify with the below code.",value=f"{randNum}")
                    embed.set_footer(text=bot.embed_footer + time)
                    myFile = discord.File(str(cwd)+'/tos.pdf')
                    message = await user.send(embed=embed)
                    await user.send(file=myFile)
                    try:
                        msg = await bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
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
                                embedThree = discord.Embed(title="User verfied", description=f"{ctx.message.guild.name}", colour=0x00ff00)
                                embedThree.add_field(name="Status:",value="Pass")
                                embedThree.set_footer(text=bot.embed_footer + time)
                                embedThree.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                                verifiedChannel = bot.get_channel(607861542326894623)
                                await verifiedChannel.send(embed=embedThree)
                            else:
                                em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nFail-Wrong Input", colour=0xff0000)
                                em.add_field(name="Im sorry but you failed verification.",value=f"Your input: *{msg.content}*")
                            time = getTime()
                            em.set_footer(text=bot.embed_footer + time)
                            messageTwo = await user.send(embed=em)
                    except asyncio.TimeoutError:
                        time = getTime()
                        em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nFail-No Input", colour=0x808080)
                        em.add_field(name="Im sorry but you failed verification.",value=f"Your input: *null*")
                        em.set_footer(text=bot.embed_footer + time)
                        messageTwo = await user.send(embed=em)
                else:
                    await user.send(f"You are already verfied!\n||If you are missing verifed roles pm Skelmis||")
            else:
                await ctx.send("**This discord does not have verification enabled.\nPlease contact a staff member in your discord to enable this.**")
        else:
            await ctx.send("**This discord has not setup verification yet.\nPlease contact a staff member in your discord in order to do this.**")

@bot.command()
@commands.is_owner()
@commands.cooldown(1, 2, commands.BucketType.user)
async def echo(ctx,*,msg='e'):
    """Echo input"""
    if msg == 'e':
        await ctx.send("Please enter text to echo after the command")
    else:
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(msg)

@bot.event
async def on_member_update(before,after):
    if before.guild.id == 599164187385659402 and after.guild.id == 599164187385659402:
        if len(before.roles) < len(after.roles): #if the user has gained a role
            newRole = next(role for role in after.roles if role not in before.roles)
            if newRole.name in ('~ Level One', '~ Level Two', '~ Level Three', '~ Level X'):
                data = read_json('userConfig')
                money = read_json('money')
                uid = '{0.id}'.format(after)
                if not uid in data:
                    data[uid] = {}
                if not "modifier" in data[uid]:
                    data[uid]['modifier'] = 0
                if not uid in money:
                    money[uid] = {}
                if not "bankedMoney" in money[uid]:
                    money[uid]['bankedMoney'] = 0
                if newRole.name == '~ Level One':
                    change = 0.03
                    data[uid]['modifier'] = data[uid]['modifier'] + 0.03
                    money[uid]['bankedMoney'] = money[uid]['bankedMoney'] + 2500
                elif newRole.name == '~ Level Two':
                    change = 0.05
                    data[uid]['modifier'] = data[uid]['modifier'] + 0.05
                    money[uid]['bankedMoney'] = money[uid]['bankedMoney'] + 5000
                elif newRole.name == '~ Level Three':
                    change = 0.075
                    data[uid]['modifier'] = data[uid]['modifier'] + 0.075
                    money[uid]['bankedMoney'] = money[uid]['bankedMoney'] + 10000
                elif newRole.name == '~ Level X':
                    change = 0.1
                    data[uid]['modifier'] = data[uid]['modifier'] + 0.1
                    money[uid]['bankedMoney'] = money[uid]['bankedMoney'] + 15000
                write_json(data, 'userConfig')
                write_json(money, 'money')
                channel = bot.get_channel(615838615368368148)
                em = discord.Embed(title="User modifier changes:", description=f"<@{uid}>", colour=0x85C1E9)
                em.add_field(name="Modifier change:",value=f"Added `{change}`")
                em.add_field(name="Users current modifier:", value=f"{(data[uid]['modifier'] + 1)}")
                time = getTime()
                em.set_footer(text=bot.embed_footer + time)
                await channel.send(embed=em)
        elif len(before.roles) > len(after.roles):
            removedRole = next(role for role in before.roles if role not in after.roles)
            if removedRole.name in ('~ Level One', '~ Level Two', '~ Level Three', '~ Level X'):
                data = read_json('userConfig')
                money = read_json('money')
                uid = '{0.id}'.format(after)
                if not uid in data:
                    data[uid] = {}
                if not "modifier" in data[uid]:
                    data[uid]['modifier'] = 0
                if not uid in money:
                    money[uid] = {}
                if not "bankedMoney" in money[uid]:
                    money[uid]['bankedMoney'] = 0
                if removedRole.name == '~ Level One':
                    change = 0.03
                    data[uid]['modifier'] = data[uid]['modifier'] - 0.03
                elif removedRole.name == '~ Level Two':
                    change = 0.05
                    data[uid]['modifier'] = data[uid]['modifier'] - 0.05
                elif removedRole.name == '~ Level Three':
                    change = 0.075
                    data[uid]['modifier'] = data[uid]['modifier'] - 0.075
                elif removedRole.name == '~ Level X':
                    change = 0.1
                    data[uid]['modifier'] = data[uid]['modifier'] - 0.1
                write_json(data, 'userConfig')
                channel = bot.get_channel(615838615368368148)
                em = discord.Embed(title="User modifier changes:", description=f"<@{uid}>", colour=0xEC7063)
                em.add_field(name="Modifier change:",value=f"Removed `{change}`")
                em.add_field(name="Users current modifier:", value=f"{(data[uid]['modifier'] + 1)}")
                time = getTime()
                em.set_footer(text=bot.embed_footer + time)
                await channel.send(embed=em)

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
            userData[uid] = {}
            userData[uid]['criminalNum'] = 1
            userData[uid]['blacklisted'] = False
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
@commands.cooldown(1, 30, commands.BucketType.user)
async def docs(ctx):
    """Check out our documents relating to the project"""
    tos = discord.File(str(cwd)+'/tos.pdf')
    manifest = discord.File(str(cwd)+'/The Back Alley.docx')
    await ctx.send(content="Terms of service", file=tos, delete_after=60)
    await ctx.send(content="Manifest and bot overview", file=manifest, delete_after=60)

@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def invites(ctx):
    """Show invites"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
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
            try:
                await ctx.message.delete()
            except:
                pass

spamcount = 0
@bot.command()
@commands.is_owner()
@commands.cooldown(1, 2, commands.BucketType.user)
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
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def purge(ctx, amount:int):
    """Purge some channels"""
    botAdmin = checkBotAdmin(ctx)
    if botAdmin == True:
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.channel.purge(limit=amount)

@bot.command(name='perms', aliases=['perms_for', 'permissions', 'userperms'])
@commands.guild_only()
@commands.cooldown(1, 2, commands.BucketType.user)
async def check_permissions(ctx, member: discord.Member=None):
    """A simple command which checks a members Guild Permissions.
    If member is not provided, the author will be checked."""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
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
@commands.cooldown(1, 2, commands.BucketType.user)
async def embed(ctx, *, content:str):
    """Embed a message"""
    # Usage: (prefix)embed <your message>
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        embed = discord.Embed(
            description = content,
            color = discord.Color.orange()
        );

        embed.set_footer(text = 'ID: ' + str(ctx.author.id));
        embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url));

        await ctx.send(embed = embed);

@bot.group()
@commands.cooldown(1, 5, commands.BucketType.user)
async def buy(ctx):
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            if ctx.invoked_subcommand is None:
                time = getTime()
                em = discord.Embed(title="Commands", description="Avaliable commands.", colour=0x0000CC)
                em.add_field(name="buy nfa (amount)",value="Buy an nfa alt", inline=False)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                em.set_footer(text=bot.embed_footer + time)
                await ctx.send(embed=em)
                try:
                    await ctx.message.delete()
                except:
                    pass

@buy.command()
@commands.cooldown(1, 3600, commands.BucketType.user)
async def nfa(ctx, amount: int=1):
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        await ctx.message.delete()
        verified = await checkVerified(ctx)
        if verified == True:
            money = read_json('money')
            alts = read_json('alts')
            uid = '{0.id}'.format(ctx.message.author)
            if not uid in money:
                await ctx.send("It does not appear you can run this command.\n||Error code - 404 User Money Not Found||")
            else:
                cash = money[uid]['money']
                price = alts["0"]['price']
                currentAlt = alts["0"]['currentAlt']
                price = int(price)
                cash = int(cash)
                if price <= cash:
                    user = bot.get_user(int(uid))
                    em = discord.Embed(title="Purchase", description="Thanks for purchasing an alt from us.", colour=0xffff00)
                    #for i in range(amount):
                    if 1 == 1: #placeholder indent
                        foundAlt = False
                        while foundAlt == False:
                            if alts[str(currentAlt)]['used'] == False:
                                alt = alts[str(currentAlt)]['alt']
                                foundAlt = True
                                break
                            else:
                                currentAlt += 1
                        alts[currentAlt]['used'] = True
                        alts["0"]['currentAlt'] = str(int(currentAlt) + 1)
                        money[uid]['money'] = cash - price
                        em.add_field(name="Alt details:",value=f"{alt}", inline=False)
                    try:
                        time = getTime()
                        em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                        em.set_footer(text=bot.embed_footer + time)
                        await user.send(embed=em)
                        write_json(money, 'money')
                        write_json(alts, 'alts')

                        embedThree = discord.Embed(title="Item purchased in:", description=f"{ctx.message.guild.name}", colour=0x00ff00)
                        embedThree.add_field(name="Item:",value="Nfa alt", inline=False)
                        embedThree.add_field(name="Quantity:",value=f"{amount}", inline=False)
                        embedThree.add_field(name="Purchase complete:",value="Yes", inline=False)
                        embedThree.set_footer(text=bot.embed_footer + time)
                        embedThree.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                        purchaseChannel = bot.get_channel(608276919057776663)
                        await purchaseChannel.send(embed=embedThree)
                    except:
                        await ctx.send(f"Hey <@{uid}>, I don't think I can dm you therefore you cannot purchase this item.\n||Error code - Foxtrot 32, Broken Pipe||")
                        nfa.reset_cooldown(ctx)
                else:
                    await ctx.send(f"You need ${price} in cash to purchase this.\n||<@{uid}>||", delete_after=30)
                    nfa.reset_cooldown(ctx)

@bot.group()
@commands.cooldown(1, 2, commands.BucketType.user)
async def bug(ctx):
    """Bug report section"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        if ctx.invoked_subcommand is None:
            time = getTime()
            em = discord.Embed(title="Commands", description="Avaliable commands.", colour=0x0000CC)
            em.add_field(name="bug report (Describe the bug)",value="Report bot bugs", inline=False)
            em.add_field(name="bug status (Report Id)",value="Check the status of a bug report", inline=False)
            em.add_field(name="bug accept (Report Id) (Closing comment - `optional`)",value="Accept and close active bug reports - `Management Only`", inline=False)
            em.add_field(name="bug deny (Report Id) (Closing comment - `optional`)",value="Deny and close active bug reports - `Management Only`", inline=False)
            em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
            em.set_footer(text=bot.embed_footer + time)
            await ctx.send(embed=em,delete_after=30)
            try:
                await ctx.message.delete()
            except:
                pass

@bug.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def report(ctx, *, args):
    """Open a new bug report"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
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
            try:
                await ctx.message.delete()
            except:
                pass
        else:
            await channel.send(f"An error occured when ({uid}) tried making a bug report")

@bug.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def status(ctx, rid):
    """Check the status of any bug report"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
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
            try:
                await ctx.message.delete()
            except:
                pass
        else:
            await ctx.send(content="Invalid report id...", delete_after=5)
            try:
                await ctx.message.delete()
            except:
                pass

@bug.command()
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def accept(ctx, rid, *, reason=None):
    """Accept and close a bug report"""
    botAdmin = checkBotAdmin(ctx)
    if botAdmin == True:
        state = "Accepted"
        data = read_json('reports')
        time = getTime()
        validReport = False
        if rid in data['bug']:
            validReport = True
        if validReport == True:
            if not reason:
                reason = f"{state} by {ctx.author.name}."
            else:
                reason = reason + f'\nReport closed by {ctx.author.name}'
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
            try:
                await ctx.message.delete()
            except:
                pass
        else:
            await ctx.send(content="Invalid report id...", delete_after=5)
            try:
                await ctx.message.delete()
            except:
                pass

@bug.command()
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def deny(ctx, rid, *, reason=None):
    """Deny and close a bug report"""
    botAdmin = checkBotAdmin(ctx)
    if botAdmin == True:
        state = "Denied"
        data = read_json('reports')
        time = getTime()
        validReport = False
        if rid in data['bug']:
            validReport = True
        if validReport == True:
            if not reason:
                reason = f"{state} by {ctx.author.name}."
            else:
                reason = reason + f'\nReport closed by {ctx.author.name}'
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
            try:
                await ctx.message.delete()
            except:
                pass
        else:
            await ctx.send(content="Invalid report id...", delete_after=5)
            try:
                await ctx.message.delete()
            except:
                pass

@bot.command()
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def logout(ctx):
    """Log the bot out of discord"""
    botAdmin = checkBotAdmin(ctx)
    if botAdmin == True:
        await ctx.send("Logging out...")
        print(f"{ctx.message.author} has logged the bot out")
        await bot.logout()

@bot.command()
@commands.is_owner()
async def guilds(ctx):
    """Check guilds the bot is in"""
    botGuilds = bot.guilds
    string = "Heres my guilds:\n"
    for guild in botGuilds:
        string = string + f"{guild.name}\n"
    await ctx.send(f"{string}")

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
@commands.cooldown(1, 300, commands.BucketType.user)
async def income(ctx):
    """A command to generate income"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            randomOne = random.randint(1,9)
            #await ctx.send(f"{randomOne} + {randomTwo}")
            uid = '{0.id}'.format(ctx.message.author)
            randomTwo = random.randint(1,9)
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
                        userModData[uid]['modifier'] = 0
                    write_json(userModData, 'userConfig')
                    discordModData = read_json('discordConfig')
                    if not did in discordModData:
                        discordModData[did] = {}
                    if not 'modifier' in discordModData[did]:
                        discordModData[did]['modifier'] = 0
                    write_json(discordModData, 'discordConfig')
                    discordMod = discordModData[did]['modifier']
                    userMod = userModData[uid]['modifier']
                    totalMod = 1 + discordMod + userMod
                    await ctx.trigger_typing()
                    responseData = read_json('responses')
                    responseNumber = random.randint(1,10)
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
                    totalCountAdd(uid, 'totalMoneyWon', 'money', income)
                    msgResponse = responseData[f'{responseNumber}']
                    em = discord.Embed(title="Income", description="Make that cash money.", colour=0x0000CC)
                    em.add_field(name=f"{msgResponse}",value=f"You made: ${income}", inline=False)
                    em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                    em.set_footer(text=bot.embed_footer + time)
                    await ctx.send(embed=em)
                    try:
                        await ctx.message.delete()
                    except:
                        pass
            else:
                time = getTime()
                em = discord.Embed(title="Income", description="DisgRaCe", colour=0x0000CC)
                em.add_field(name="You have a failed status in an anti bot check. ",value="Please run the command `antibot` to resolve this issue.\nIf you need assistance contact <@271612318947868673> to resolve this issues.", inline=False)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                em.set_footer(text=bot.embed_footer + time)
                await ctx.send(embed=em)
                await ctx.send(f"<@{uid}>")
                try:
                    await ctx.message.delete()
                except:
                    pass

@bot.group()
@commands.cooldown(1, 2, commands.BucketType.user)
async def bank(ctx):
    """Use your bank here"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            if ctx.invoked_subcommand is None:
                time = getTime()
                em = discord.Embed(title="Bank", description="Its your local", colour=0xffffff)
                em.add_field(name="bank deposit (amount)",value="Put money into your bank", inline=False)
                em.add_field(name="bank withdraw (amount)",value="take money out from your bank", inline=False)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                em.set_footer(text=bot.embed_footer + time)
                await ctx.send(embed=em, delete_after=15)
                try:
                    await ctx.message.delete()
                except:
                    pass

@bank.command()
@commands.cooldown(1, 900, commands.BucketType.user)
async def deposit(ctx, amount=None):
    """A command to deposit money into your bank"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            if not amount:
                amount = 0.0
            all = False
            uid = '{0.id}'.format(ctx.message.author)
            try:
                if amount.lower() == 'all':
                    all == True
                    udc = read_json('money')
                    amount = udc[uid]['money']
            except:
                all = False
            await ctx.trigger_typing()
            amount = float(amount)
            if amount == 0 and all == False:
                await ctx.send("Please specify either `deposit (amount)` or `withdraw (amount)`")
            elif amount <= 0 and all == False:
                await ctx.send("You need to specify a positive amount aswell...")
            else:
                time = getTime()
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
                try:
                    await ctx.message.delete()
                except:
                    pass

@bank.command()
@commands.cooldown(1, 300, commands.BucketType.user)
async def withdraw(ctx, amount=None):
    """A command to remove money from your bank"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            if not amount:
                amount = 0.0
            all = False
            uid = '{0.id}'.format(ctx.message.author)
            try:
                if amount.lower() == 'all':
                    all == True
                    udc = read_json('money')
                    amount = udc[uid]['bankedMoney']
            except:
                all = False
            await ctx.trigger_typing()
            amount = float(amount)
            if amount == 0:
                await ctx.send("Please specify either `deposit (amount)` or `withdraw (amount)`")
            elif amount <= 0:
                await ctx.send("You need to specify a positive amount aswell...")
            else:
                time = getTime()
                amount = round(amount)
                t = withdraw(uid, amount)
                em = discord.Embed(title="Bank", description="Cash in hand makes a solid plan.", colour=0x990099)
                em.add_field(name="Withdrawl:",value=f"{t}", inline=False)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                em.set_footer(text=bot.embed_footer + time)
                await ctx.send(embed=em)
                try:
                    await ctx.message.delete()
                except:
                    pass


@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def bal(ctx, user: discord.User=None):
    """A command to checkout yourself or others"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
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
                try:
                    await ctx.message.delete()
                except:
                    pass
            else:
                await ctx.send("Um yea, so you don't exist in the db for this discord. E.g. You should use {}income".format(prefix))

@bot.command(enabled=True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def baltop(ctx, pagenum='1'):
    """Check out the money balances"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
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
            username = None
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
                k = k.strip("`")
                count += 1
                if count > ((pagenum*10)-10) and count  <= (pagenum*10):
                    if count in [1,2,3,4,5]:
                        medal = bot.config_stars['medals'][(count-1)]
                    else:
                        medal =''
                    if not username:
                        username = f"#{str(count)} - ${v} - {k} {medal}\n"
                    else:
                        username = username + f"\n#{str(count)} - ${v} - {k} {medal}\n"
            em = discord.Embed(colour=12745742)
            if pagenum <= math.ceil(total/10):
                em.add_field(name ='Top Bals | page ' + str(pagenum) + ' of ' + str(math.ceil(total/10)), value=username, inline=False)
                em.set_footer(text=bot.embed_footer + time)
            else:
                em.add_field(name =':x: ERROR :x:', value='Invalid page number! (' + str(pagenum) + ')\nPlease use ``help`` for more information.', inline=False)
            await asyncio.sleep(1)
            await ctx.send(embed=em)
            try:
                await ctx.message.delete()
            except:
                pass

@bot.command(enabled=True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def cashtop(ctx, pagenum='1'):
    """Check out the money balances"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            await ctx.trigger_typing()
            time = getTime()
            pagenum = int(pagenum)
            username = None
            count = 0
            total = 0
            di = {}
            data = read_json('money')
            for i in data:
                di[data[i]['name']] = int(data[i]['money'])
                total += 1
            results = sorted(di.items(), key=lambda t : t[1], reverse=True)
            for k, v in results:
                v = str(v)
                k = k.strip("`")
                count += 1
                if count > ((pagenum*10)-10) and count  <= (pagenum*10):
                    if count in [1,2,3,4,5]:
                        medal = bot.config_stars['medals'][(count-1)]
                    else:
                        medal =''
                    if not username:
                        username = f"#{str(count)} - ${v} - {k} {medal}\n"
                    else:
                        username = username + f"\n#{str(count)} - ${v} - {k} {medal}\n"
            em = discord.Embed(colour=12745742)
            if pagenum <= math.ceil(total/10):
                em.add_field(name ='Top Cash Bals | page ' + str(pagenum) + ' of ' + str(math.ceil(total/10)), value=username, inline=False)
                em.set_footer(text=bot.embed_footer + time)
            else:
                em.add_field(name =':x: ERROR :x:', value='Invalid page number! (' + str(pagenum) + ')\nPlease use ``help`` for more information.', inline=False)
            await asyncio.sleep(1)
            await ctx.send(embed=em)
            try:
                await ctx.message.delete()
            except:
                pass


@bot.command(enabled=True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def banktop(ctx, pagenum='1'):
    """Check out the money balances"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            await ctx.trigger_typing()
            time = getTime()
            pagenum = int(pagenum)
            username = None
            count = 0
            total = 0
            di = {}
            data = read_json('money')
            for i in data:
                di[data[i]['name']] = int(data[i]['bankedMoney'])
                total += 1
            results = sorted(di.items(), key=lambda t : t[1], reverse=True)
            for k, v in results:
                v = str(v)
                k = k.strip("`")
                count += 1
                if count > ((pagenum*10)-10) and count  <= (pagenum*10):
                    if count in [1,2,3,4,5]:
                        medal = bot.config_stars['medals'][(count-1)]
                    else:
                        medal =''
                    if not username:
                        username = f"#{str(count)} - ${v} - {k} {medal}\n"
                    else:
                        username = username + f"\n#{str(count)} - ${v} - {k} {medal}\n"
            em = discord.Embed(colour=12745742)
            if pagenum <= math.ceil(total/10):
                em.add_field(name ='Top Bank Bals | page ' + str(pagenum) + ' of ' + str(math.ceil(total/10)), value=username, inline=False)
                em.set_footer(text=bot.embed_footer + time)
            else:
                em.add_field(name =':x: ERROR :x:', value='Invalid page number! (' + str(pagenum) + ')\nPlease use ``help`` for more information.', inline=False)
            await asyncio.sleep(1)
            await ctx.send(embed=em)
            try:
                await ctx.message.delete()
            except:
                pass


@bot.command()
@commands.is_owner()
@commands.cooldown(1, 2, commands.BucketType.user)
async def emtest(ctx, *, em):
    """Set embed footers"""
    bot.embed_footer = em

@bot.group(enabled=True)
@commands.cooldown(1, 300, commands.BucketType.user)
async def rob(ctx, user: discord.Member=None, type=None):
    """Rob some people"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            if not user:
                time = getTime()
                em = discord.Embed(title="Rob", description="Bloody gangs these days", colour=0xffffff)
                em.add_field(name="rob (user)",value="rob someones cash", inline=False)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                em.set_footer(text=bot.embed_footer + time)
                await ctx.send(embed=em, delete_after=15)
                try:
                    await ctx.message.delete()
                except:
                    pass
                return
            if not type or type.lower() == 'cash':
                randomOne = random.randint(1,6)
                randomTwo = random.randint(1,6)
                uid = '{0.id}'.format(ctx.message.author)
                name = '{}'.format(ctx.message.author)
                userId = '{0.id}'.format(user)
                moneyData = read_json('money')
                if userId == uid:
                    await ctx.send("Bruh you can't just rob yourself")
                    return
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

                            userData = read_json('userConfig')
                            if not uid in userData:
                                userData[uid] = {}
                            if not 'criminalNum' in userData[uid]:
                                userData[uid]['criminalNum'] = 0
                            currentCrimRating = userData[uid]['criminalNum']
                            userData[uid]['criminalNum'] = currentCrimRating - 1
                            write_json(userData, 'userConfig')

                            time = getTime()
                            stolenCash = round(stolenCash)
                            stolenCash = float(stolenCash)
                            totalCountAdd(uid, 'totalMoneyWon', 'money', stolenCash)
                            totalCountAdd(userId, 'totalMoneyLost', 'money', stolenCash)
                            em = discord.Embed(title="Robbery", description="Shank shank", colour=0xCC0000)
                            em.add_field(name="Victim:",value=f"{user}", inline=False)
                            em.add_field(name="Cash stolen:",value=f"${stolenCash}", inline=False)
                            em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                            em.set_footer(text=bot.embed_footer + time)
                            await ctx.send(embed=em)
                            try:
                                await ctx.message.delete()
                            except:
                                pass
                        else:
                            await ctx.send(f"Uh, yea {user} doesn't appear to exist so you can't rob them. Try someone else?")
                    else:#get total money - get % for bank, cash - divide fine between
                        randomFour = random.randint(1.000,10)
                        lossPercentage =  randomFour / 100
                        try:
                            currentCash = moneyData[uid]['money']
                        except:
                            currentCash = 0
                        totalMoney = currentCash
                        if totalMoney != 0:
                            cashFine = None
                            if currentCash != 0:
                                cashPercentage = totalMoney / 100
                                fine = totalMoney * lossPercentage
                                cashFine = (fine / randomFour) * cashPercentage
                                moneyData[uid]['money'] = currentCash - cashFine
                            if not cashFine:
                                cashFine = 0

                            courtRequired = await courtSystem(ctx)
                            if courtRequired == False:
                                userData = read_json('userConfig')
                                if not uid in userData:
                                    userData[uid] = {}
                                currentCrimRating = userData[uid]['criminalNum']
                                userData[uid]['criminalNum'] = currentCrimRating + 1
                                write_json(userData, 'userConfig')
                                cashFine = round(cashFine)
                                time = getTime()
                                tfine = float(cashFine)
                                totalCountAdd(uid, 'totalMoneyLost', 'money', tfine)
                                em = discord.Embed(title="Robbery", description="You played yourself fool.", colour=0xFF6347)
                                em.add_field(name="Victim:",value=f"You", inline=False)
                                em.add_field(name="Cash lost:",value=f"${cashFine}", inline=False)
                                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                                em.set_footer(text=bot.embed_footer + time)
                                await ctx.send(embed=em)
                            try:
                                await ctx.message.delete()
                            except:
                                pass
                        else:
                            await ctx.send("Lucky... Your too poor to tax as of right now...")
                write_json(moneyData, 'money')


@bot.command(aliases=['bankrob','robbank'])
@commands.cooldown(1, 1800, commands.BucketType.user)
async def _bankrob(ctx, user: discord.Member=None):
        whitelistedChannel = await checkWhitelist(ctx)
        if whitelistedChannel == True:
            verified = await checkVerified(ctx)
            if verified == True:
                if not user:
                    time = getTime()
                    em = discord.Embed(title="Rob", description="Bloody gangs these days", colour=0xffffff)
                    em.add_field(name="rob (user)",value="rob someones cash", inline=False)
                    em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                    em.set_footer(text=bot.embed_footer + time)
                    await ctx.send(embed=em, delete_after=15)
                    try:
                        await ctx.message.delete()
                    except:
                        pass
                    return
                """Rob someone elses bank account"""
                userData = read_json('userConfig')
                uid = '{0.id}'.format(ctx.author)
                did = '{0.id}'.format(ctx.guild)
                userId = '{0.id}'.format(user)
                if not uid in userData:
                    userData[uid] = {}
                    userData[uid]['criminalNum'] = 0
                if not 'criminalNum' in userData[uid]:
                    userData[uid]['criminalNum'] = 0
                write_json(userData, 'userConfig')
                userData = read_json('userConfig')
                criminalNum = userData[uid]['criminalNum']
                discordData = read_json('discordConfig')
                if str(uid) == str(userId):
                    await ctx.send("You can't rob yourself but as a penalty for trying im not removing ur cooldown ;p", delete_after=30)
                    return
                if criminalNum <= -100: #if crim num is less then -1
                    randomOne = random.randint(1,5)
                    randomTwo = random.randint(1,5)
                    if randomOne != randomTwo:
                        moneyData = read_json('money')
                        if userId in moneyData:
                            randomThree = random.randint(1,5)
                            theftPercentage = randomThree / 100
                            userBankMoney = moneyData[userId]['bankedMoney']
                            stolenMoney = userBankMoney * theftPercentage
                            moneyData[userId]['bankedMoney'] = userBankMoney - stolenMoney
                            try:
                                robberMoney = moneyData[uid]['bankedMoney']
                            except:
                                robberMoney = 0
                            moneyData[uid]['bankedMoney'] = robberMoney + stolenMoney
                            write_json(moneyData, 'money')
                            userData = read_json('userConfig')
                            if not uid in userData:
                                userData[uid] = {}
                            if not 'criminalNum' in userData[uid]:
                                userData[uid]['criminalNum'] = 0
                            currentCrimRating = userData[uid]['criminalNum']
                            userData[uid]['criminalNum'] = currentCrimRating - 3
                            write_json(userData, 'userConfig')
                            time = getTime()
                            stolenMoney = round(stolenMoney)
                            totalCountAdd(uid, 'totalMoneyWon', 'money', stolenMoney)
                            totalCountAdd(userId, 'totalMoneyLost', 'money', stolenMoney)
                            em = discord.Embed(title="Bank Robbery", description="Sneaky snake you are", colour=0xCC0000)
                            em.add_field(name="Victim:",value=f"{user}", inline=False)
                            em.add_field(name="Money stolen:",value=f"${stolenMoney}", inline=False)
                            em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                            em.set_footer(text=bot.embed_footer + time)
                            await ctx.send(embed=em)
                        else:
                            await ctx.send(content=f"Ouch rude, trying to rob someone I dont have data on", delete_after=15)
                    else:
                        courtRequired = await courtSystem(ctx)
                        await ctx.send(content=f"uh oh, looks like ur going to court <@{uid}>", delete_after=15)
                else:
                    await ctx.send(content=f"Hey <@{uid}>, you can't rob peoples banks yet, k thx lmaooo.\nRob more people's cash to improve your criminal rating and then rob banks", delete_after=10)

@bot.group(aliases=['gangs'])
@commands.cooldown(1, 2, commands.BucketType.user)
async def gang(ctx):
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            if ctx.invoked_subcommand is None:
                em = discord.Embed(title="Commands", description="Avaliable commands.\n*Note these are still in development*", colour=0x0000CC, timestamp=ctx.message.created_at)
                em.add_field(name="gang create",value="create your own gang, Cost $750\n||Command finished.||", inline=False)
                em.add_field(name="gang name",value="change your gang name, Cost $50", inline=False)
                em.add_field(name="gang buy",value="buy gear for your gang", inline=False)
                em.add_field(name="gang invite",value="invite someone to your gang", inline=False)
                em.add_field(name="gang leave",value="leave your current gang", inline=False)
                em.add_field(name="gang stats",value="checkout your gang stats\n||Command finished.||", inline=False)
                em.add_field(name="gang payouts",value="change the payout scheme for your gang", inline=False)
                em.add_field(name="gang settings",value="alter your gangs settings", inline=False)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                em.set_footer(text=bot.embed_footer)
                await ctx.send(embed=em,delete_after=30)
                await ctx.message.delete()

@gang.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def create(ctx):
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            await ctx.message.delete()
            data = read_json('gangs')
            uid = str(ctx.author.id)
            await ctx.send(f"<@{uid}>")
            if uid in data:
                await ctx.send(f"Hey <@{uid}>, you are already leader of a gang.\nIf you wish to create a new gang please delete your old gang first using `gang settings delete`",delete_after=30)
                return
            for i in data:
                if uid in data[i]['members']:
                    await ctx.send(f"Hey <@{uid}>, you are already part of a gang.\nIf you wish to create a new gang please leave your old gang first using `gang leave`",delete_after=30)
                    return
            money = read_json('money')
            if not uid in money:
                await ctx.send("Hey, in order to create a gang you do need to have used my commands to earn money ya know...",delete_after=30)
                return
            if money[uid]['money'] < 750: #If there cash is less than $750 (gang creation cost)
                await ctx.send("Um, so you do actually need $750 cash in order to create a gang ya know...",delete_after=30)
                return

            foundName = False
            duplicate = False
            async def getname():
                msgone = await ctx.send("Please enter a name for your gang. You have 60 seconds.\nNote Gang names must be under 25 characters long.")
                try:
                    msg = await bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
                    if msg:
                        await msgone.delete()
                        return msg.content
                except asyncio.TimeoutError:
                    await msgone.delete()
                    await ctx.send("Timed out.",delete_after=5)
                    await asyncio.sleep(5)
                    return "TimeoutError"

            while foundName is False:
                name = await getname()
                name = name.lower()
                if name in ['cancel', 'stop']:
                    await ctx.send("Cancelling the process...",delete_after=15)
                    return
                if name != "TimeoutError":
                    if len(name) <= 25: #if the name is smaller than 25 characters long
                        for i in data:
                            if data[i]['name'] == name:
                                await ctx.send(f"Hey! This name (`{name}`) is already in use. Please pick another one",delete_after=10)
                                duplicate = True
                        if duplicate is False:
                            msgone = await ctx.send(f"Please confirm you want your gang name to be **{name}**\nTo confirm please type yes.")
                            try:
                                msg = await bot.wait_for('message', timeout=30, check=lambda message: message.author == ctx.author)
                                if msg:
                                    if msg.content.lower() in ['yes', 'confirm', 'yea']:
                                        await msgone.delete()
                                        await ctx.send("Thanks for confirming, we will now begin the next stage of creation.",delete_after=10)
                                        foundName = True
                                        break
                            except asyncio.TimeoutError:
                                msgone.delete()

            data[uid] = {}
            data[uid]['name'] = name
            data[uid]['leader'] = uid
            data[uid]['members'] = []
            data[uid]['members'].append(uid)
            data[uid]['createdAt'] = getTime()
            data[uid]['gangLevel'] = 1
            data[uid]['gunLevel'] = 1
            data[uid]['cribLevel'] = 1
            data[uid]['workers'] = 0
            data[uid]['money'] = 0
            data[uid]['maxMembers'] = 3
            data[uid]['siegeExperience'] = 0
            write_json(data, 'gangs')

            money[uid]['money'] = money[uid]['money'] - 750
            if not "localBank" in money:
                money["localBank"] = {}
                money["localBank"]["cash"] = 750
            money["localBank"]["cash"] = money["localBank"]["cash"] + 750
            write_json(money, 'money')

            em = discord.Embed(title="Gang created",timestamp=ctx.message.created_at,colour=ctx.author.colour)
            em.add_field(name="Gang Name:",value=data[uid]['name'],inline=False)
            em.add_field(name="Gang Leader:",value=f"<@{data[uid]['leader']}>")
            em.add_field(name="Gang Level:",value=data[uid]['gangLevel'])
            em.add_field(name="Gang Money:",value="$0")
            em.set_footer(text="*You have been charged $750 to create this gang.*")
            em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
            await ctx.send(embed=em,delete_after=15)
            await ctx.author.send(embed=em)

@gang.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def stats(ctx):
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            data = read_json('gangs')
            uid = str(ctx.author.id)
            gangLeader = False
            gangMember = False
            gang = None
            if uid in data:
                gangLeader = True
                gang = uid
            if gangLeader is False:
                for i in data:
                    if uid in data[i]['members']:
                        gangMember = True
                        gang = i
            if gangLeader is False and gangMember is False:
                await ctx.send("It doesn't look like your in a gang sorry mate, feel free to create one with `gang create`", delete_after=15)
                return
            gangMembers = None
            memberCount = 0
            for i in data[gang]['members']:
                if not gangMembers:
                    gangMembers = f"<@{i}>"
                else:
                    gangMembers = gangMembers +  f", <@{i}>"
                memberCount += 1

            em = discord.Embed(title="Gang Stats",timestamp=ctx.message.created_at,colour=ctx.author.colour)
            em.add_field(name="Gang Name:",value=data[gang]['name'],inline=False)
            em.add_field(name="Gang Leader:",value=f"<@{data[gang]['leader']}>")
            em.add_field(name="Gang Level:",value=data[gang]['gangLevel'])
            em.add_field(name="Gang Money:",value=data[gang]['money'])
            em.add_field(name='\uFEFF', value='\uFEFF',inline=False)
            em.add_field(name="Gang Members:",value=gangMembers)
            em.add_field(name="Gang Workers:",value=data[gang]['workers'])
            em.add_field(name='\uFEFF', value='\uFEFF',inline=False)
            em.add_field(name="Gang Crib Level:",value=data[gang]['cribLevel'])
            em.add_field(name="Gang Gun Level:",value=data[gang]['gunLevel'])
            em.add_field(name="Gang Siege Experience:",value=data[gang]['siegeExperience'])
            em.add_field(name='\uFEFF', value='\uFEFF',inline=False)
            em.add_field(name="Gang Member Count:",value=memberCount)
            em.add_field(name="Gang Max Member Count:",value=data[gang]['maxMembers'])
            em.add_field(name="Gang Created At:",value=data[gang]['createdAt'])
            em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
            await ctx.send(embed=em,delete_after=30)
            await ctx.message.delete()

@gang.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def leave(ctx):
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        verified = await checkVerified(ctx)
        if verified == True:
            data = read_json('gangs')
            uid = str(ctx.author.id)
            gangLeader = False
            gangMember = False
            gang = None
            if uid in data:
                gangLeader = True
                gang = uid
            if gangLeader is False:
                for i in data:
                    if uid in data[i]['members']:
                        gangMember = True
                        gang = i
            if gangLeader is False and gangMember is False:
                await ctx.send("It doesn't look like your in a gang sorry mate, feel free to create one with `gang create`", delete_after=15)
                return

@bot.group()
@commands.is_owner()
@commands.cooldown(1, 2, commands.BucketType.user)
async def admin(ctx):
    """Add or remove bot admins"""
    verified = await checkVerified(ctx)
    if verified == True:
        if ctx.invoked_subcommand is None:
            await ctx.send("Either admin add or admin remove mate")

@admin.command()
@commands.is_owner()
@commands.cooldown(1, 2, commands.BucketType.user)
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
        try:
            await ctx.message.delete()
        except:
            pass

@admin.command()
@commands.is_owner()
@commands.cooldown(1, 2, commands.BucketType.user)
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
        try:
            await ctx.message.delete()
        except:
            pass

@bot.group()
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def staff(ctx):
    """Add or remove bot admins"""
    verified = await checkVerified(ctx)
    if verified == True:
        botAdmin = checkBotAdmin(ctx)
        if botAdmin == True:
            if ctx.invoked_subcommand is None:
                await ctx.send("Either staff add or staff remove mate")

@staff.command()
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def add(ctx, user=None):
    """Add a user as bot staff"""
    verified = await checkVerified(ctx)
    if verified == True:
        botAdmin = checkBotAdmin(ctx)
        if botAdmin == True:
            if not user:
                user = '{0.id}'.format(ctx.author)
            try:
                user = user.strip("<@>")
            except:
                user = user
            uid = user
            data = read_json('config')
            if not uid in data['staff']:
                data['staff'][uid] = {}
                data['staff'][uid]['staff'] = "true"
            else:
                data['staff'][uid]['staff'] = "true"
            write_json(data, 'config')
            msg = await ctx.send(f"Added <@{uid}> as bot staff")
            await asyncio.sleep(5)
            await msg.delete()
            try:
                await ctx.message.delete()
            except:
                pass

@staff.command()
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def remove(ctx, user=None):
    """Remove someone as bot staff"""
    verified = await checkVerified(ctx)
    if verified == True:
        botAdmin = checkBotAdmin(ctx)
        if botAdmin == True:
            if not user:
                user = '{0.id}'.format(ctx.author)
            try:
                user = user.strip("<@>")
            except:
                user = user
            uid = user
            data = read_json('config')
            if not uid in data['staff']:
                data['staff'][uid] = {}
                data['staff'][uid]['staff'] = "false"
            else:
                data['staff'][uid]['staff'] = "false"
            write_json(data, 'config')
            msg = await ctx.send(f"Removing <@{uid}> as bot staff")
            await asyncio.sleep(5)
            await msg.delete()
            try:
                await ctx.message.delete()
            except:
                pass

@bot.group()
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def blacklist(ctx):
    """Add or remove bot blacklists"""
    verified = await checkVerified(ctx)
    if verified == True:
        botAdmin = checkBotAdmin(ctx)
        if botAdmin == True:
            if ctx.invoked_subcommand is None:
                await ctx.send("Either blacklist add or blacklist remove mate")

@blacklist.command()
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def add(ctx, user=None):
    """Blacklists a user"""
    verified = await checkVerified(ctx)
    if verified == True:
        botAdmin = checkBotAdmin(ctx)
        if botAdmin == True:
            if not user:
                await ctx.send("Please say who to blacklist", delete_after=15)
                return
            try:
                user = user.strip("<@>")
            except:
                user = user
            if user == "271612318947868673" or user == "294863378260688897":
                await ctx.send("Im sorry, you are unable to blacklist this user.", delete_after=15)
                return
            uid = user
            data = read_json('userConfig')
            if not uid in data:
                data[uid] = {}
                data[uid]['blacklisted'] = True
            else:
                data[uid]['blacklisted'] = True
            write_json(data, 'userConfig')
            bot.blacklisted_users = read_json('userConfig')
            msg = await ctx.send(f"Adding <@{uid}> to the blacklist")
            await asyncio.sleep(5)
            await msg.delete()
            try:
                await ctx.message.delete()
            except:
                pass

@blacklist.command()
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def remove(ctx, user=None):
    """Remove someone from the blacklist"""
    verified = await checkVerified(ctx)
    if verified == True:
        botAdmin = checkBotAdmin(ctx)
        if botAdmin == True:
            try:
                user = user.strip("<@>")
            except:
                user = user
            if user == "271612318947868673" or user == "294863378260688897":
                await ctx.send("Im sorry, you are unable to blacklist this user.", delete_after=15)
                return
            uid = user
            data = read_json('userConfig')
            if not uid in data:
                data[uid] = {}
                data[uid]['blacklisted'] = False
            else:
                data[uid]['blacklisted'] = False
            write_json(data, 'userConfig')
            bot.blacklisted_users = read_json('userConfig')
            msg = await ctx.send(f"Removing <@{uid}> from the blacklist")
            await asyncio.sleep(5)
            await msg.delete()
            try:
                await ctx.message.delete()
            except:
                pass


@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def inviteinfo(ctx, invite: discord.Invite):
        """Shows information about an invite."""
        whitelistedChannel = await checkWhitelist(ctx)
        if whitelistedChannel == True:
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
@commands.cooldown(1, 2, commands.BucketType.user)
async def antibot(ctx):
    """For when you fail an anti bot check, this can get you out of a sticky situation"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
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

@bot.command()
@commands.cooldown(1, 100, commands.BucketType.user)
async def serverinfo(ctx, guild: int=None):
        """Command to show server info"""
        whitelistedChannel = await checkWhitelist(ctx)
        if whitelistedChannel == True:
            if not guild:
                guild = ctx.guild.id
            guild = bot.get_guild(guild)
            embed = discord.Embed(
                color=discord.Color.from_rgb(241, 90, 36)
            )
            sender = ctx.author
            embed.set_author(name="• Server Info → " + str(guild.name))
            #embed.set_thumbnail(url=guild.banner(size=4096, format="png"))
            embed.add_field(name="—", value="→ Shows all information about a guild. The information will be listed below!"
                                            "\n —")
            embed.add_field(name="• Guild name: ", value=str(guild.name))
            embed.add_field(name="• Discord ID: ", value=str(guild.id))
            embed.add_field(name='\uFEFF', value='\uFEFF')
            embed.add_field(name="• Guild owner: ", value=guild.owner)
            embed.add_field(name="• Guild owner ID: ", value=guild.owner_id)
            embed.add_field(name='\uFEFF', value='\uFEFF')

            await ctx.send(embed=embed)
            if ctx.author.id == 271612318947868673:
                await ctx.send("Reset cooldown?")
                serverinfo.reset_cooldown(ctx)

@bot.group()
@commands.has_role('~ Staff')
async def payroll(ctx):
    verified = await checkVerified(ctx)
    if verified == True:
        botStaff = checkStaff(ctx)
        if botStaff == True:
            if ctx.invoked_subcommand is None:
                embed = discord.Embed(colur=discord.Color.from_rgb(255,90,40))
                embed.add_field(name="payroll add (user) (amount) (Optional - Type)", value="adds (amount) to (user) money (cash)\nType is the account, bank or cash. Defaults to cash", inline=False)
                embed.add_field(name="payroll remove (user) (amount)", value="removes (amount) from (user) money (cash)\nType is the account, bank or cash. Defaults to cash", inline=False)
                embed.add_field(name="payroll clear (user)", value="sets all money values for (user) to 0\nType is the account, bank or cash. Defaults to all", inline=False)
                await ctx.send(embed=embed, delete_after=30)

@payroll.command()
@commands.has_role('~ Staff')
async def add(ctx, user, amount: float, type=None):
    verified = await checkVerified(ctx)
    if verified == True:
        botStaff = checkStaff(ctx)
        if botStaff == True:
            if not type:
                type = "cash"
            user = user.strip("<@>")
            uid = '{0}'.format(user)
            data = read_json('money')
            if uid in data:
                if type.lower() == "cash":
                    money = data[uid]['money']
                    data[uid]['money'] = money + amount
                    newAmount = data[uid]['money']
                elif type.lower() == "bank":
                    money = data[uid]['bankedMoney']
                    data[uid]['bankedMoney'] = money + amount
                    newAmount = data[uid]['bankedMoney']
                write_json(data, 'money')
                await ctx.message.delete()
                newAmount = round(newAmount)
                money = round(money)
                em = discord.Embed(title="Payroll change:", description=f"{type} money added", colour=0xcccccc,timestamp=ctx.message.created_at)
                em.add_field(name="Affected User:",value=f"<@{uid}>")
                em.add_field(name="Money added:",value=f"${amount}", inline=False)
                em.add_field(name="New balance:", value=f"${newAmount}")
                em.add_field(name="Old balance:", value=f"${money}")
                em.set_footer(text=bot.embed_footer)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                await ctx.send(embed=em, delete_after=30)
                channel = bot.get_channel(613694916874338306)
                await channel.send(embed=em)

@payroll.command()
@commands.has_role('~ Staff')
async def remove(ctx, user, amount: float, type=None):
    verified = await checkVerified(ctx)
    if verified == True:
        botStaff = checkStaff(ctx)
        if botStaff == True:
            if not type:
                type = "cash"
            user = user.strip("<@>")
            uid = '{0}'.format(user)
            data = read_json('money')
            if uid in data:
                if type.lower() == "cash":
                    money = data[uid]['money']
                    data[uid]['money'] = money - amount
                    newAmount = data[uid]['money']
                elif type.lower() == "bank":
                    money = data[uid]['bankedMoney']
                    data[uid]['bankedMoney'] = money - amount
                    newAmount = data[uid]['bankedMoney']
                write_json(data, 'money')
                await ctx.message.delete()
                newAmount = round(newAmount)
                money = round(money)
                em = discord.Embed(title="Payroll change:", description=f"{type} money removed", colour=0xcccccc,timestamp=ctx.message.created_at)
                em.add_field(name="Affected User:",value=f"<@{uid}>")
                em.add_field(name="Money removed:",value=f"${amount}", inline=False)
                em.add_field(name="New balance:", value=f"${newAmount}")
                em.add_field(name="Old balance:", value=f"${money}")
                em.set_footer(text=bot.embed_footer)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                await ctx.send(embed=em, delete_after=30)
                channel = bot.get_channel(613694916874338306)
                await channel.send(embed=em)

@payroll.command()
@commands.has_role('~ Staff')
async def clear(ctx, user, type=None):
    verified = await checkVerified(ctx)
    if verified == True:
        botStaff = checkStaff(ctx)
        if botStaff == True:
            if not type:
                type = "all"
            user = user.strip("<@>")
            uid = '{0}'.format(user)
            data = read_json('money')
            if uid in data:
                if type.lower() == "cash":
                    data[uid]['money'] = 0
                elif type.lower() == "bank":
                    data[uid]['bankedMoney'] = 0
                else:
                    data[uid]['bankedMoney'] = 0
                    data[uid]['totalMoney'] = 0
                    data[uid]['money'] = 0
                write_json(data, 'money')
                await ctx.message.delete()
                em = discord.Embed(title="Payroll change:", description=f"{type} money cleared", colour=0xcccccc,timestamp=ctx.message.created_at)
                em.add_field(name="Affected User:",value=f"<@{uid}>")
                em.add_field(name="Money cleared:",value="Success", inline=False)
                em.set_footer(text=bot.embed_footer)
                em.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                await ctx.send(embed=em, delete_after=30)
                channel = bot.get_channel(613694916874338306)
                await channel.send(embed=em)

@bot.command()
async def linux(ctx):
    """Some linux commands useful for skelmis"""
    embed = discord.Embed(colur=discord.Color.from_rgb(241,90,36))
    embed.add_field(name="Kill screen", value="screen -X -S [session # you want to kill] quit")
    embed.add_field(name="rename screen", value="screen -S (screen number) -X sessionname (new name)")
    embed.add_field(name="Reconnect to 'attached' screens", value="screen -r -d (screen number)")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role('Discord Administrator')
async def dedsec(ctx, arg):
    """Enable/Disable dedsec - `Management Only`"""
    botAdmin = checkBotAdmin(ctx)
    if botAdmin == True:
        if arg.lower() == "enable":
            bot.dedsec_enabled = True
            await ctx.send("Enabled `Dedsec`")
        else:
            bot.dedsec_enabled = False
            await ctx.send("Disabled `Dedsec`")

@bot.command()
@commands.is_owner()
async def tca(ctx):
    uid = '271612318947868673'
    amount = 15
    totalCountAdd(uid, 'totalMoneyWon', 'money', 2500)
    await ctx.send('done')

#functions
def totalCountAdd(uid, type, json, amount):
    data = read_json(str(json))
    uid = str(uid)
    type = str(type)
    json = str(json)
    amount = float(amount)
    if not uid in data:
        data[uid] = {}
    if not type in data[uid]:
        data[uid][type] = amount
    else:
        data[uid][type] = data[uid][type] + amount
    write_json(data, json)

async def courtSystem(ctx):
    channel = bot.get_channel(606405385234153483)
    await channel.send("Make the court system nerd")
    return False

def checkBotAdmin(ctx):
    data = read_json('config')
    uid = '{0.id}'.format(ctx.author)
    if uid in data['admins']:
        if data['admins'][uid]['admin'] == "true":
            return True
    return False

def checkStaff(ctx):
    data = read_json('config')
    uid = '{0.id}'.format(ctx.author)
    if uid in data['staff']:
        if data['staff'][uid]['staff'] == "true":
            return True
    return False

async def botCheck(ctx):
    """A function that can be used to check if someone is scripting or not using multiple verification methods"""
    randNum = random.randint(0, bot.check_num)
    if randNum == 0:
        await CheckOne(ctx)
    elif randNum == 1:
        await CheckTwo(ctx)
    else:
        await CheckOne(ctx)

async def CheckOne(ctx):
    """Verification check one"""
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

async def CheckTwo(ctx):
    """Verification check two"""
    data = read_json('userConfig')
    uid = '{0.id}'.format(ctx.author)
    user = bot.get_user(int(uid))
    if not uid in data:
        data[uid] = {}
    randStr = getRandomString()
    randNum = randStr + bot.greek
    expectedInput = randStr + ";"
    time = getTime()
    embed = discord.Embed(title=f"{ctx.message.author}", description="Please repeat the below code to avoid being flagged as a bot.", colour=0xffffff)
    embed.add_field(name="You have 60 seconds to verify with the below code.",value=f"{randNum}")
    embed.set_footer(text=bot.embed_footer + time)
    await ctx.send(content=f"Hey {user.mention}, please check your dms from me", delete_after=15)
    startTime = datetime.now()
    message = await user.send(embed=embed)
    try:
        msg = await bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        if msg:
            totalTime = datetime.now() - startTime
            totalTime = str(totalTime)
            endTime = None
            check = []
            for char in str(totalTime):
                check.append(str(char.lower()))
            for i in range(len(check)):
                if check[i] == '.':
                    endTime = totalTime[int(i-2):i]
            if msg.content == str(randNum):
                em = discord.Embed(title=f"{ctx.message.author}", description="Verification status:\nPass", colour=0x228B22)
                em.add_field(name="Thank you for completing this bot check.",value=f"Your input: *{msg.content}*")
                data = read_json('userConfig')
                if not uid in data:
                    data[uid] = {}
                data[uid]['botCheck'] = "pass"
                write_json(data, 'userConfig')

                channel = bot.get_channel(608586455731929088)
                dedsecEmbed = discord.Embed(title="Dedsec - Caution Notice", description=f"{ctx.message.author} - `({uid})`", colour=0xff6666)
                dedsecEmbed.add_field(name="User suspected of botting.\n`bot.greek` contents found within input, expected semicolon.",value=f"Input: *{msg.content}*")
                dedsecEmbed.add_field(name=f"User completed the check in `{endTime}` seconds.", value="Average completion time is around `15-30` seconds.")
                time = getFullTime()
                dedsecEmbed.set_footer(text=bot.embed_footer + time)
                await channel.send(embed=dedsecEmbed)
            elif msg.content == str(expectedInput):
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
                await member.send(f"Hey bro. So you arent verified. Join this discord and do `-verify`\n{bot.invite}")
                await ctx.send(f"Hey <@{uid}>, check your dms from me",delete_after=30)
                try:
                    await ctx.message.delete()
                except:
                    pass
            except:
                await ctx.send(f"Hey <@{uid}, so i can't dm you it seems... Join this discord and do `-verify`\n{bot.invite}")
                try:
                    await ctx.message.delete()
                except:
                    pass
            return False
    else:
        try:
            member = bot.get_user(int(uid))
            await member.send(f"Hey bro. So you arent verified. Join this discord and do `-verify`\n{bot.invite}")
            await ctx.send(f"Hey <@{uid}>, check your dms from me",delete_after=30)
            try:
                await ctx.message.delete()
            except:
                pass
        except:
            await ctx.send(f"Hey <@{uid}, so i can't dm you it seems... Join this discord and do `-verify`\n{bot.invite}")
            try:
                await ctx.message.delete()
            except:
                pass
        return False

async def checkWhitelist(ctx):
    """A function made for usage with bot restrictions in the back alley"""
    if ctx.guild.id == 599164187385659402:
        botAdmin = checkBotAdmin(ctx)
        if botAdmin == True:
            return True
        data = read_json('whitelistedChannels')
        channel = '{0.id}'.format(ctx.channel)
        if channel in data:
            if data[channel]['state'] == "true":
                return True
            else:
                msg = await ctx.send("This channel is not whitelisted therefore you cannont use bot commands here.")
                await asyncio.sleep(5)
                await msg.delete()
                try:
                    await ctx.message.delete()
                except:
                    pass
                return False
        else:
            msg = await ctx.send("This channel is not whitelisted therefore you cannont use bot commands here.")
            await asyncio.sleep(5)
            await msg.delete()
            try:
                await ctx.message.delete()
            except:
                pass
            return False
    else:
        return True

def getTime():
    """Gets current date"""
    time = datetime.now().strftime('%d/%m/%Y')
    return time

def getFullTime():
    """Gets current date and time"""
    time = datetime.now().strftime('%S:%M:%H %d/%m/%Y')
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
            w = "You don't have enough money to do this... You only have ${}".format(round(moneyData[uid]['money']))
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
    jsonFile.write(json.dumps(data, indent=4))
    jsonFile.close()

@bot.group()
@commands.cooldown(1, 2, commands.BucketType.user)
async def stats(ctx):
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
        if ctx.invoked_subcommand is None:
            uid = str(ctx.author.id)
            did = str(ctx.guild.id)
            md = read_json('money')
            data = read_json('userConfig')
            dData = read_json('discordConfig')
            if not uid in md:
                await ctx.send("Please generate some money and come back...")
                return
            if not uid in data:
                await ctx.send("Please generate some more data and come back...")
                return
            #Try get total money values
            try:
                totalMoneyWon = md[uid]['totalMoneyWon']
            except:
                totalMoneyWon = 0
            try:
                totalMoneyLost = md[uid]['totalMoneyLost']
            except:
                totalMoneyLost = 0

            #Try get bug report Stats
            try:
                totalBugReportsAccepted = data[uid]['totalAcceptedBugs']
            except:
                totalBugReportsAccepted = 0
            try:
                totalBugReportsDenied = data[uid]['totalDeniedBugs']
            except:
                totalBugReportsDenied = 0

            #crim status
            try:
                crimStatus = data[uid]['criminalNum']
            except:
                crimStatus = 0

            #income modifier
            try:
                dMod = dData[did]['modifier']
            except:
                dMod = 0
            try:
                uMod = data[uid]['modifier']
            except:
                uMod = 0
            tMod = uMod + dMod + 1

            embed = discord.Embed(title='User Stats', description='Your stats for the bot. \n**This feature is still under development**', colour=ctx.author.colour, timestamp=ctx.message.created_at)
            embed.add_field(name='Total Money Won:', value=f"${totalMoneyWon}")
            embed.add_field(name='Total Money Lost:', value=f"${totalMoneyLost}")
            embed.add_field(name='Income Modifer:', value=f'{tMod}')
            embed.add_field(name='Total Bugs Accepted:', value=totalBugReportsAccepted)
            embed.add_field(name='Total Bugs Denied:', value=totalBugReportsDenied)
            embed.add_field(name='\uFEFF', value='\uFEFF')
            embed.add_field(name='Criminal Status:', value=f'You need a status of -100 or lower to rob banks.\nYours is {crimStatus}')
            embed.set_footer(text=bot.embed_footer)
            embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
            await ctx.send(embed = embed)

            pass

@stats.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def general(ctx):
    """Show some basic stats"""
    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
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

@stats.command(name="bot")
@commands.cooldown(1, 2, commands.BucketType.user)
async def _bot(ctx): #called call it bot because it breaks

    whitelistedChannel = await checkWhitelist(ctx)
    if whitelistedChannel == True:
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
@commands.has_role('Discord Administrator')
@commands.cooldown(1, 2, commands.BucketType.user)
async def admin(ctx):
    """Some nice admin stats surrounding the bot"""
    botAdmin = checkBotAdmin(ctx)
    if botAdmin == True:
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

initial_extensions = ['cogs.music', 'cogs.eval']

if __name__ == '__main__':
    """If this is the 'main' file, run this code and run the bot when the script is ran"""
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            print(f'Loaded {extension}')
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()
    bot.run(bot.config_token)
