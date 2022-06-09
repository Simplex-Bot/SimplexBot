import discord
import discord
from discord.ext import commands
import json
import numexpr as ne
import numpy

def load_counting_data():
    with open("./databases/counting.json") as f:
        return json.load(f)

def load_db_data():
    with open("./databases/db.json") as f:
        return json.load(f)

def get_guild_db_data(db_data, guild):
    for datum in db_data:
        if datum["guild_id"] == guild.id:
            return datum
    return None

def save_counting_data(counting_data):
    with open("./databases/counting.json", 'w') as f:
        json.dump(counting_data, f, indent=4)

def save_db_data(db_data):
    with open("./databases/db.json", 'w') as f:
        json.dump(db_data, f, indent=4)

# Counting


async def counting(msg, guild, channel, m):
    
    try:
        if msg.startswith('this'):
         return

        if msg.startswith('that'):
         return
        msg = int(msg)
    except:
        try:
          calc = ne.evaluate(msg)
          msg = int(calc)
        except:
         return    

    db_data = load_db_data()
    guild_db_data = get_guild_db_data(db_data, guild)
    try:
        counting_channel_id = int(guild_db_data["counting_channel"])
        if counting_channel_id is None:
            return
    except:
        return

    if channel.id == counting_channel_id:
        counting_data = get_counting_data()

        if guild_db_data['lastcounter'] == m.author.id:
            counting_data[f"{guild.id}"] = 0
            guild_db_data['lastcounter'] = None
            await m.add_reaction("❌")
            em = discord.Embed(title=f"{m.author.name}, You ruined it!", description="Only one person at a time\nCount reset to zero")
            await channel.send(embed=em)
        else:
            guild_db_data['lastcounter'] = m.author.id
            next_number = counting_data[f"{guild.id}"] + 1
                        
            if msg == next_number:
                counting_data[f"{guild.id}"] = next_number
                await m.add_reaction("✅")
            else:
                em = discord.Embed(title=f"{m.author.name}, You ruined it!", description=f"You were supposed to type `{next_number}`\nCount reset to zero")
                guild_db_data['lastcounter'] = None
                counting_data[f"{guild.id}"] = 0
                await channel.send(embed=em)
                await m.add_reaction("❌")
        save_counting_data(counting_data)
        save_db_data(db_data)


class Counting(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command(aliases=['num'])
    async def numrn(self, ctx):
        guild = ctx.guild
        counting_data = load_counting_data()
        guild_id = f'{guild.id}'
        numrn = data[guild_id]
        await ctx.send(f"Current number is {numrn}")

    @commands.Cog.listener()
    async def on_message(self, message):

        channel = message.channel
        msg = message.content
        guild = message.guild

        await counting(msg, guild, channel, message)

    def mic(ctx):
        return ctx.author.id == 481377376475938826

    # delete after usage 
    @commands.command()
    @commands.check(mic) # cmd can only be run by mic
    async def sacc(self, ctx):
        for i in self.client.guilds:
            insert = {
                "guild_id": i.id,
                "counting_channel": None,
                "lastcounter":None,
            }
            db_data = load_db_data()
            db_data.append(insert)
            save_db_data(db_data)
            
            counting_data = load_counting_data()
            counting_data[f"{i.id}"] = 0
            save_counting_data(counting_data)
            
    
    @commands.command()
    async def setcountchannel(self, ctx, channel:discord.TextChannel):
        db_data = load_db_data()

        guild_db_data = get_guild_db_data(db_data, ctx.guild)
        guild_db_data['counting_channel'] = channel.id

        save_db_data(db_data)

    @commands.command()
    async def countingoff(self, ctx):
        data = load_db_data()

        guild_db_data = get_guild_db_data(db_data, ctx.guild)
        guild_db_data['counting_channel'] = None

        save_db_data(db_data)
            
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        insert = {
            "guild_id": guild.id,
            "counting_channel": None,
            "lastcounter":None,
        }
        db_data = load_db_data()
        db_data.append(insert)
        save_db_data(db_data)

        counting_data = load_counting_data()
        counting_data[f"{guild.id}"] = 0
        save_counting_data(counting_data)


def setup(client):
    client.add_cog(Counting(client))
