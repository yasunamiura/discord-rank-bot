import discord
from discord.ext import commands
from discord import app_commands
import os


# トークンとギルドIDを設定
class MyBot(commands.Bot):

  def __init__(self):
    # intentsの設定 (必要に応じて適切なintentsを設定)
    intents = discord.Intents.default()
    super().__init__(command_prefix='/', intents=intents)

  async def setup_hook(self):
    # スラッシュコマンドをギルドに登録
    self.tree.add_command(hi_command, guild=discord.Object(id=GUILD_ID))
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))


bot = MyBot()


@bot.tree.command(name="hi", description="元気を出して！")
async def hi_command(interaction: discord.Interaction):
  await interaction.response.send_message('今日も一日頑張りましょう')


# Botを起動
bot.run(os.getenv('TOKEN'))
