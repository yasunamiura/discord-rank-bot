import discord
from discord.ext import commands
import os

# Botの設定
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')
  for guild in bot.guilds:
    for channel in guild.text_channels:
      if channel.name == 'bot':  # 'bot'チャンネルを探す
        await channel.send('接続')  # 接続メッセージを送信
        break


# Botのトークンでログイン
bot.run(os.getenv('TOKEN'))
