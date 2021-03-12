import discord
from discord.ext import commands
from itertools import cycle
import random
import json
import os
import time
import datetime
import datetime
import asyncio
from datetime import timedelta
from skindict import skin_dict


client = commands.Bot(command_prefix = "a.")
auctions = []
skin_dict = skin_dict

class Auction:
    def __init__(self, embed, channel, message, highest_bid, host, seller, duration, highest_bidder=None):
        self._embed = embed
        self._channel = channel
        self._message = message
        self._id = self._channel.id
        self._highest_bid = highest_bid
        self._host = host
        self._seller = seller
        self._duration = int(duration)
        self._highest_bidder = highest_bidder
        self._end_time = datetime.datetime.now()+timedelta(days=duration)
        self._finished = False

    
    async def addBid(self, amount, bidder):
        if amount > self._highest_bid:
            self._highest_bid = amount
            self._highest_bidder = bidder
            await self._channel.send("Bid by %s for %s" % (bidder.mention, amount))
        else:
            await self._channel.send("Bid has to be higher than the highest bid")
        
    @property
    def channel(self):
        return self._channel

    @property
    def end_time(self):
        return self._end_time
    
    @property
    def embed(self):
        return self._embed

    @property
    def message(self):
        return self._message

    @property
    def finished(self):
        return self._finished

    @message.setter
    def message(self, m):
        self._message = m

    @property
    def highest_bidder(self):
        return self._highest_bidder

    @highest_bidder.setter
    def highest_bidder(self, h):
        self._highest_bidder = h

    async def start(self):
        await asyncio.sleep(86400*self._duration)
        if datetime.datetime.now().strftime("%d-%m-%Y at %H:%M") == self.end_time.strftime("%d-%m-%Y at %H:%M"): 
            self._finished = True
            if self._highest_bidder != None:
                await self._channel.send("""Going once.... going twice.... 
                                            \nSold to %s for %d.
                                            \n%s and %s contact %s ASAP""" % (self._highest_bidder.mention, self._highest_bid, self._highest_bidder.mention, self._seller, self._host.mention))

            else:
                await self._channel.send("No one offered. :FeelsBdman:")
            
            

    async def time_left(self):
        TL = self._end_time.strftime("%d-%m-%Y at %H:%M")
        await self._channel.send(TL)
    

@client.event 
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("a.help KTH is the Goat"))
    print("Auction Time")


async def create_channel(context, channelName):
    channelName = "「🔨」" + channelName
    guild = context.guild
    for category in guild.categories:
        if category.id == 701856425965649992 or category.id == 813803826573475902:
            c = await category.create_text_channel(name=channelName)
            return c


async def delete_channel(channel:discord.TextChannel):
    await channel.delete()


@client.command()
async def ping(context):
    await context.send(f"Pong! {round(client.latency * 1000)}ms")


@client.command()
@commands.has_permissions(manage_messages=True)
async def auction(context, skin, last_sold, seller, duration):
    
    try:
        starting_bid = int(last_sold)-int(last_sold)//10
    except:
        await context.send("Last sold has to be a number. Don't add 'KR' after.\nAlso if the skin name has a [SPACE] either put it in ' '.")
        return
    guild = context.guild
    embed = discord.Embed(title="%s" % skin, description="", timestamp=context.message.created_at, color=discord.Color.blue())
    embed.set_thumbnail(url=guild.icon_url)
    try:
        embed.set_image(url=skin_dict[skin])
    except KeyError:
        await context.send("Check the skin name please. (It's case sensitive)")
        return
    embed.add_field(name="**Last Sold: **", value=last_sold+"KR", inline=False)
    embed.add_field(name="**Starting Bid: **", value=str(starting_bid)+"KR", inline=False)
    embed.add_field(name="**Seller: **", value=seller, inline=False)
    embed.set_footer(text="Hosted by %s" % context.author, icon_url=context.author.avatar_url)

    try:
        duration = int(duration)
    except:
        await context.send("Duration has to be a whole number.")
    c = await create_channel(context, skin)

    
    try:
        await c.send("@Auctions Ping")
        m = c.send(embed=embed)
        await m
        auc = Auction(embed, c, m, starting_bid, context.author, seller, duration)
        auctions.append(auc)
        await auc.start() 
    except ValueError:
        await context.send("Didnt work")


@client.command()
async def bid(context, amount=None):
    bidder = context.author
    x = False
    for r in context.author.roles:
        if r.name == "Bidders":
            x = True

    if x == False:
        await context.send("U have to have the Bidders role.")
        return
    if amount == None:
        await context.send("Please add an amount")
        return None
    print(auctions)
    try:
        amount = int(amount)
    except:
        await context.send("Amount has to be a number. Don't add 'KR' after.")
    for a in auctions:
        if a.channel == context.channel:
            await a.addBid(amount, bidder)


@client.command()
async def deadline(context):
    if auctions == []:
        await context.send("I'm not currently running any auctions")
    else:
        for a in auctions:
            if a.channel == context.channel:
                await a.time_left()
            

@client.command()
@commands.has_permissions(manage_messages=True)
async def end_auction(context):
    if auctions == []:
        await context.send("I'm not currently running any auctions")
    else:
        for a in auctions:
            if a.channel == context.channel: 
                if a.finished == True:
                    auctions.remove(a)
                    await delete_channel(context.channel)
                else:
                    await context.send("This auction isn't over yet. (a.deadline to check when it is)")

@client.command()
@commands.has_permissions(manage_messages=True)
async def giveaway(context, giveaway_name=None, giveaway_channel=None, finished=None):
    guild = context.guild
    if finished == None:
        for channel in guild.channels:
            if channel.id == 764378320665837601:
                if giveaway_name != None and giveaway_channel != None:
                    await channel.send("Go to %s and react for %s giveaway" % (giveaway_channel, giveaway_name))
                    await asyncio.sleep(7200)
                    await giveaway()

                else:
                    await channel.send("Go to <#764399050866819082> and react for daily giveaways")
                    await asyncio.sleep(7200)
                    await giveaway()
    else:
        await context.send("No more reminders will be sent")

@client.command()
async def skin(context, skin=None):
    if skin == None:
        await context.send("Add a skin name please")
        return 
    guild = context.guild
    embed = discord.Embed(title="%s" % skin, description="", timestamp=context.message.created_at, color=discord.Color.blue())
    embed.set_thumbnail(url=guild.icon_url)
    try:
        embed.set_image(url=skin_dict[skin])
    except KeyError:
        await context.send("Check the skin name please. (It's case sensitive)\nAlso if the skin name has a [SPACE] either put it in ' '.")
        return
    embed.set_footer(text="Requested by %s" % context.author, icon_url=context.author.avatar_url)
    await context.send(embed=embed)

client.run("ODE0NTQ5Njk3NTY1Mjk0NjQz.YDfehQ.IuLfzqA5q89ZDE__a0tS_n3wnWQ")